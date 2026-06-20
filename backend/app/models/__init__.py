import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


def _uid() -> str:
    return str(uuid.uuid4())

def _now() -> datetime:
    return datetime.now(timezone.utc)


class Repo(Base):
    __tablename__ = "repos"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    url: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    owner: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="queued")
    cloned_path: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    analyses = relationship("Analysis", back_populates="repo", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="repo", cascade="all, delete-orphan")
    chunks = relationship("Chunk", back_populates="repo", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="repo", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="repo", cascade="all, delete-orphan")
    complexity = relationship("ComplexityScore", back_populates="repo", uselist=False, cascade="all, delete-orphan")
    diagrams = relationship("MermaidDiagram", back_populates="repo", cascade="all, delete-orphan")
    onboarding = relationship("OnboardingGuide", back_populates="repo", uselist=False, cascade="all, delete-orphan")
    comparisons_a = relationship("Comparison", foreign_keys="Comparison.repo_a_id", back_populates="repo_a", cascade="all, delete-orphan")
    comparisons_b = relationship("Comparison", foreign_keys="Comparison.repo_b_id", back_populates="repo_b")


class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    arch_type: Mapped[str | None] = mapped_column(String)
    languages: Mapped[list] = mapped_column(JSON, default=list)
    frameworks: Mapped[list] = mapped_column(JSON, default=list)
    databases: Mapped[list] = mapped_column(JSON, default=list)
    auth_methods: Mapped[list] = mapped_column(JSON, default=list)
    design_patterns: Mapped[list] = mapped_column(JSON, default=list)
    package_managers: Mapped[list] = mapped_column(JSON, default=list)
    deployment_configs: Mapped[list] = mapped_column(JSON, default=list)
    file_count: Mapped[int] = mapped_column(Integer, default=0)
    loc_total: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    repo = relationship("Repo", back_populates="analyses")


class Document(Base):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    doc_type: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    repo = relationship("Repo", back_populates="documents")


class Chunk(Base):
    __tablename__ = "chunks"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, default=0)
    language: Mapped[str] = mapped_column(String, default="unknown")
    repo = relationship("Repo", back_populates="chunks")


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    mode: Mapped[str] = mapped_column(String, default="developer")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    repo = relationship("Repo", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    session = relationship("ChatSession", back_populates="messages")


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, default="queued")
    step: Mapped[str] = mapped_column(String, default="init")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    repo = relationship("Repo", back_populates="jobs")


class ComplexityScore(Base):
    __tablename__ = "complexity_scores"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False, unique=True)
    overall: Mapped[int] = mapped_column(Integer, default=0)
    maintainability: Mapped[int] = mapped_column(Integer, default=0)
    documentation: Mapped[int] = mapped_column(Integer, default=0)
    architecture: Mapped[int] = mapped_column(Integer, default=0)
    test_coverage: Mapped[float] = mapped_column(Float, default=0.0)
    tech_debt: Mapped[int] = mapped_column(Integer, default=0)
    strengths: Mapped[list] = mapped_column(JSON, default=list)
    weaknesses: Mapped[list] = mapped_column(JSON, default=list)
    suggestions: Mapped[list] = mapped_column(JSON, default=list)
    file_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    hotspots: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    repo = relationship("Repo", back_populates="complexity")


class MermaidDiagram(Base):
    __tablename__ = "mermaid_diagrams"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    diagram_type: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    repo = relationship("Repo", back_populates="diagrams")


class OnboardingGuide(Base):
    __tablename__ = "onboarding_guides"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    repo_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False, unique=True)
    day1: Mapped[str] = mapped_column(Text, nullable=False)
    day2: Mapped[str] = mapped_column(Text, nullable=False)
    day3: Mapped[str] = mapped_column(Text, nullable=False)
    key_files: Mapped[list] = mapped_column(JSON, default=list)
    checklist: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    repo = relationship("Repo", back_populates="onboarding")


class Comparison(Base):
    __tablename__ = "comparisons"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uid)
    repo_a_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    repo_b_id: Mapped[str] = mapped_column(ForeignKey("repos.id"), nullable=False)
    score_matrix: Mapped[dict] = mapped_column(JSON, default=dict)
    summary: Mapped[str | None] = mapped_column(Text)
    tech_stack_diff: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    repo_a = relationship("Repo", foreign_keys=[repo_a_id], back_populates="comparisons_a")
    repo_b = relationship("Repo", foreign_keys=[repo_b_id], back_populates="comparisons_b")
