import asyncio
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models import Repo, Job, Analysis, Document, ComplexityScore, MermaidDiagram, OnboardingGuide
from app.schemas import RepoSubmit, RepoOut, JobOut, AnalysisOut, DocumentOut, ComplexityOut, DiagramOut, OnboardingOut
from app.workers.analysis_worker import run_analysis

router = APIRouter(tags=["analyze"])


def _parse_url(url: str) -> tuple[str, str]:
    parts = url.rstrip("/").split("/")
    return parts[-2], parts[-1].replace(".git", "")


@router.post("/analyze", response_model=dict, status_code=202)
async def submit(payload: RepoSubmit, bg: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    owner, name = _parse_url(payload.url)
    repo = Repo(url=payload.url, name=name, owner=owner, status="queued")
    db.add(repo)
    await db.flush()
    job = Job(repo_id=repo.id, status="queued", step="init", progress=0)
    db.add(job)
    await db.flush()
    await db.commit()
    bg.add_task(run_analysis, repo.id, job.id)
    return {"repo_id": repo.id, "job_id": job.id, "status": "queued"}


@router.get("/repos", response_model=list[RepoOut])
async def list_repos(db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Repo).order_by(Repo.created_at.desc()).limit(50))
    return r.scalars().all()


@router.get("/repos/{repo_id}", response_model=RepoOut)
async def get_repo(repo_id: str, db: AsyncSession = Depends(get_db)):
    repo = await db.get(Repo, repo_id)
    if not repo: raise HTTPException(404, "Repo not found")
    return repo


@router.get("/jobs/{job_id}", response_model=JobOut)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job: raise HTTPException(404, "Job not found")
    return job


@router.get("/repos/{repo_id}/analysis", response_model=AnalysisOut)
async def get_analysis(repo_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Analysis).where(Analysis.repo_id == repo_id).order_by(Analysis.created_at.desc()))
    a = r.scalar_one_or_none()
    if not a: raise HTTPException(404, "Analysis not found")
    return a


@router.get("/repos/{repo_id}/docs", response_model=list[DocumentOut])
async def get_docs(repo_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Document).where(Document.repo_id == repo_id))
    return r.scalars().all()


@router.get("/repos/{repo_id}/docs/{doc_type}", response_model=DocumentOut)
async def get_doc(repo_id: str, doc_type: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(Document).where(Document.repo_id == repo_id, Document.doc_type == doc_type))
    d = r.scalar_one_or_none()
    if not d: raise HTTPException(404, f"Document '{doc_type}' not found")
    return d


@router.get("/repos/{repo_id}/complexity", response_model=ComplexityOut)
async def get_complexity(repo_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(ComplexityScore).where(ComplexityScore.repo_id == repo_id))
    c = r.scalar_one_or_none()
    if not c: raise HTTPException(404, "Complexity data not found")
    return c


@router.get("/repos/{repo_id}/diagrams", response_model=list[DiagramOut])
async def get_diagrams(repo_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(MermaidDiagram).where(MermaidDiagram.repo_id == repo_id))
    return r.scalars().all()


@router.get("/repos/{repo_id}/onboarding", response_model=OnboardingOut)
async def get_onboarding(repo_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(select(OnboardingGuide).where(OnboardingGuide.repo_id == repo_id))
    g = r.scalar_one_or_none()
    if not g: raise HTTPException(404, "Onboarding guide not found")
    return g


@router.delete("/repos/{repo_id}", status_code=204)
async def delete_repo(repo_id: str, db: AsyncSession = Depends(get_db)):
    repo = await db.get(Repo, repo_id)
    if not repo: raise HTTPException(404, "Repo not found")
    await db.delete(repo)
