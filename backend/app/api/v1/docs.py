from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

router = APIRouter(prefix="/docs", tags=["docs"])


@router.get("/ping")
async def ping():
    return {"module": "docs", "status": "ready"}
