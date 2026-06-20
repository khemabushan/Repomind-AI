from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

router = APIRouter(prefix="/recruiter", tags=["recruiter"])


@router.get("/ping")
async def ping():
    return {"module": "recruiter", "status": "ready"}
