"""RAG engine using modern LangChain LCEL — FAISS + OpenAI."""
import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from app.core.config import settings

_indexes: dict[str, FAISS] = {}
CHUNK_SIZE    = 1000
CHUNK_OVERLAP = 150

PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert software engineer helping developers understand a codebase.
Use the provided code context to answer questions accurately and concisely.
When relevant, reference specific files, functions, or patterns from the code.
If you include code snippets, use proper markdown code blocks.

Context from repository:
{context}"""),
    ("human", "{question}"),
])


def _embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        model=settings.embedding_model,
        openai_api_key=settings.openai_api_key,
    )


def _index_path(repo_id: str) -> str:
    os.makedirs(settings.faiss_index_dir, exist_ok=True)
    return os.path.join(settings.faiss_index_dir, repo_id)


def build_index(repo_id: str, files: list[dict]) -> None:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    docs = []
    for f in files:
        chunks = splitter.create_documents(
            [f["content"]],
            metadatas=[{"source": f["path"], "language": f["language"]}],
        )
        docs.extend(chunks)

    if not docs:
        return

    index = FAISS.from_documents(docs, _embeddings())
    index.save_local(_index_path(repo_id))
    _indexes[repo_id] = index


def load_index(repo_id: str) -> FAISS | None:
    if repo_id in _indexes:
        return _indexes[repo_id]
    path = _index_path(repo_id)
    if os.path.exists(path):
        idx = FAISS.load_local(
            path, _embeddings(), allow_dangerous_deserialization=True
        )
        _indexes[repo_id] = idx
        return idx
    return None


def _format_docs(docs) -> str:
    parts = []
    for d in docs:
        src = d.metadata.get("source", "unknown")
        parts.append(f"### {src}\n```\n{d.page_content}\n```")
    return "\n\n".join(parts)


async def query(repo_id: str, question: str, history: list[dict]) -> str:
    index = load_index(repo_id)
    if index is None:
        return "Repository index not found. Please re-analyze the repository."

    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=0.1,
        openai_api_key=settings.openai_api_key,
    )

    retriever = index.as_retriever(search_kwargs={"k": 5})

    # Contextualize question with chat history
    if history:
        recent = "\n".join(
            f"{m['role'].title()}: {m['content'][:300]}"
            for m in history[-4:]
        )
        contextualized = f"Chat history:\n{recent}\n\nCurrent question: {question}"
    else:
        contextualized = question

    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | PROMPT
        | llm
        | StrOutputParser()
    )

    return await chain.ainvoke(contextualized)


async def query_stream(repo_id: str, question: str, history: list[dict]):
    """Yield text tokens for SSE streaming."""
    index = load_index(repo_id)
    if index is None:
        yield "Repository index not found. Please re-analyze the repository."
        return

    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=0.1,
        openai_api_key=settings.openai_api_key,
        streaming=True,
    )

    retriever = index.as_retriever(search_kwargs={"k": 5})

    if history:
        recent = "\n".join(
            f"{m['role'].title()}: {m['content'][:300]}"
            for m in history[-4:]
        )
        contextualized = f"Chat history:\n{recent}\n\nCurrent question: {question}"
    else:
        contextualized = question

    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | PROMPT
        | llm
        | StrOutputParser()
    )

    async for chunk in chain.astream(contextualized):
        yield chunk
