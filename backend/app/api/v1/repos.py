from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models import Repo
from app.schemas import RepoSubmit, RepoOut

router = APIRouter(prefix="/repos", tags=["repos"])


@router.get("/", response_model=list[RepoOut])
async def list_repos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Repo).order_by(Repo.created_at.desc()).limit(50))
    return result.scalars().all()


@router.get("/{repo_id}", response_model=RepoOut)
async def get_repo(repo_id: str, db: AsyncSession = Depends(get_db)):
    repo = await db.get(Repo, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    return repo


@router.delete("/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repo(repo_id: str, db: AsyncSession = Depends(get_db)):
    repo = await db.get(Repo, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    await db.delete(repo)
