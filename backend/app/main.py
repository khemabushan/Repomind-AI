import os, logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.db.session import init_db
from app.api.v1 import (
    analyze,
    chat,
    compare,
    complexity,
    docs,
    mermaid,
    onboarding,
    recruiter,
    repos,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.repo_clone_dir, exist_ok=True)
    os.makedirs(settings.faiss_index_dir, exist_ok=True)
    await init_db()
    log.info("RepoMind AI ready")
    yield


app = FastAPI(
    title="RepoMind AI",
    version="2.0.0",
    description="AI-powered GitHub repository analysis",
    lifespan=lifespan,
    docs_url="/docs",
)

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(analyze.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(compare.router, prefix="/api/v1")
app.include_router(complexity.router, prefix="/api/v1")
app.include_router(docs.router, prefix="/api/v1")
app.include_router(mermaid.router, prefix="/api/v1")
app.include_router(onboarding.router, prefix="/api/v1")
app.include_router(recruiter.router, prefix="/api/v1")
app.include_router(repos.router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}


@app.exception_handler(Exception)
async def global_err(req, exc):
    log.error(f"Unhandled: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
