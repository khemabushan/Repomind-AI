import asyncio
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models import Repo, Job, Analysis, ComplexityScore, Comparison
from app.schemas import CompareSubmit, ComparisonOut
from app.services.compare_engine import compare_repos
from app.workers.analysis_worker import run_analysis
import logging

router = APIRouter(tags=["compare"])
log = logging.getLogger(__name__)


def _parse_url(url: str) -> tuple[str, str]:
    parts = url.rstrip("/").split("/")
    return parts[-2], parts[-1].replace(".git", "")


async def _ensure_repo(db: AsyncSession, url: str, bg: BackgroundTasks) -> str:
    """Return repo_id, starting analysis if needed."""
    from sqlalchemy import select
    r = await db.execute(select(Repo).where(Repo.url == url).order_by(Repo.created_at.desc()))
    existing = r.scalar_one_or_none()
    if existing and existing.status == "complete":
        return existing.id
    owner, name = _parse_url(url)
    repo = Repo(url=url, name=name, owner=owner, status="queued")
    db.add(repo)
    await db.flush()
    job = Job(repo_id=repo.id, status="queued", step="init", progress=0)
    db.add(job)
    await db.flush()
    await db.commit()
    bg.add_task(run_analysis, repo.id, job.id)
    return repo.id


@router.post("/compare", response_model=dict, status_code=202)
async def start_compare(payload: CompareSubmit, bg: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    repo_a_id = await _ensure_repo(db, payload.url_a, bg)
    repo_b_id = await _ensure_repo(db, payload.url_b, bg)

    comp = Comparison(repo_a_id=repo_a_id, repo_b_id=repo_b_id, status="pending")
    db.add(comp)
    await db.flush()
    await db.commit()

    bg.add_task(_run_compare, comp.id, repo_a_id, repo_b_id)
    return {"comparison_id": comp.id, "repo_a_id": repo_a_id, "repo_b_id": repo_b_id}


async def _run_compare(comp_id: str, repo_a_id: str, repo_b_id: str):
    from app.db.session import AsyncSessionLocal
    from app.models import Analysis, ComplexityScore
    import asyncio
    await asyncio.sleep(2)  # let analyses start

    max_wait = 300
    waited = 0
    while waited < max_wait:
        async with AsyncSessionLocal() as db:
            ra = await db.get(Repo, repo_a_id)
            rb = await db.get(Repo, repo_b_id)
            if ra and rb and ra.status == "complete" and rb.status == "complete":
                break
            if ra and ra.status == "failed":
                break
            if rb and rb.status == "failed":
                break
        await asyncio.sleep(5)
        waited += 5

    async with AsyncSessionLocal() as db:
        r_a = await db.execute(select(Analysis).where(Analysis.repo_id == repo_a_id))
        r_b = await db.execute(select(Analysis).where(Analysis.repo_id == repo_b_id))
        ana_a = r_a.scalar_one_or_none()
        ana_b = r_b.scalar_one_or_none()
        r_ca = await db.execute(select(ComplexityScore).where(ComplexityScore.repo_id == repo_a_id))
        r_cb = await db.execute(select(ComplexityScore).where(ComplexityScore.repo_id == repo_b_id))
        cx_a = r_ca.scalar_one_or_none()
        cx_b = r_cb.scalar_one_or_none()

        if not ana_a or not ana_b:
            comp = await db.get(Comparison, comp_id)
            if comp: comp.status = "failed"
            await db.commit()
            return

        def _to_dict(obj): return {c.key: getattr(obj, c.key) for c in obj.__table__.columns} if obj else {}

        try:
            result = await compare_repos(
                _to_dict(ana_a), _to_dict(ana_b),
                [], [],
                _to_dict(cx_a), _to_dict(cx_b),
            )
            comp = await db.get(Comparison, comp_id)
            if comp:
                comp.score_matrix = result["score_matrix"]
                comp.summary = result["summary"]
                comp.tech_stack_diff = result["tech_stack_diff"]
                comp.status = "complete"
            await db.commit()
        except Exception as e:
            log.error(f"Compare failed: {e}")
            comp = await db.get(Comparison, comp_id)
            if comp: comp.status = "failed"
            await db.commit()


@router.get("/compare/{comp_id}", response_model=ComparisonOut)
async def get_comparison(comp_id: str, db: AsyncSession = Depends(get_db)):
    c = await db.get(Comparison, comp_id)
    if not c: raise HTTPException(404, "Comparison not found")
    return c
