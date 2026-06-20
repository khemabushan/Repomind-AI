import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models import ChatSession, ChatMessage, Repo
from app.schemas import ChatSessionOut, ChatMessageIn, ChatMessageOut
from app.services import rag_engine

router = APIRouter(tags=["chat"])


@router.post("/repos/{repo_id}/chat/sessions", response_model=ChatSessionOut)
async def create_session(repo_id: str, db: AsyncSession = Depends(get_db)):
    repo = await db.get(Repo, repo_id)
    if not repo: raise HTTPException(404, "Repo not found")
    session = ChatSession(repo_id=repo_id, mode="developer")
    db.add(session)
    await db.flush()
    await db.commit()
    return session


@router.get("/chat/sessions/{session_id}/history")
async def get_history(session_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at))
    msgs = r.scalars().all()
    return [{"id": m.id, "role": m.role, "content": m.content, "created_at": m.created_at} for m in msgs]


@router.post("/chat/sessions/{session_id}/message")
async def send_message(session_id: str, body: ChatMessageIn, db: AsyncSession = Depends(get_db)):
    session = await db.get(ChatSession, session_id)
    if not session: raise HTTPException(404, "Session not found")

    # Save user message
    user_msg = ChatMessage(session_id=session_id, role="user", content=body.message)
    db.add(user_msg)
    await db.commit()

    # Fetch history
    r = await db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at))
    history = [{"role": m.role, "content": m.content} for m in r.scalars().all()]

    # RAG answer
    answer = await rag_engine.query(session.repo_id, body.message, history[:-1])

    # Save assistant message
    ai_msg = ChatMessage(session_id=session_id, role="assistant", content=answer)
    db.add(ai_msg)
    await db.commit()

    return {"role": "assistant", "content": answer}


@router.post("/chat/sessions/{session_id}/stream")
async def stream_message(session_id: str, body: ChatMessageIn, db: AsyncSession = Depends(get_db)):
    session = await db.get(ChatSession, session_id)
    if not session: raise HTTPException(404, "Session not found")

    user_msg = ChatMessage(session_id=session_id, role="user", content=body.message)
    db.add(user_msg)
    await db.commit()

    r = await db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at))
    history = [{"role": m.role, "content": m.content} for m in r.scalars().all()]

    full_response = []

    async def gen():
        async for token in rag_engine.query_stream(session.repo_id, body.message, history[:-1]):
            full_response.append(token)
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"
        # Save response after streaming
        ai_msg = ChatMessage(session_id=session_id, role="assistant", content="".join(full_response))
        async with __import__('app.db.session', fromlist=['AsyncSessionLocal']).AsyncSessionLocal() as db2:
            db2.add(ai_msg)
            await db2.commit()

    return StreamingResponse(gen(), media_type="text/event-stream")
