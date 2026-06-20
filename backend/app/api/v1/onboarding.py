from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("/ping")
async def ping():
    return {"module": "onboarding", "status": "ready"}
