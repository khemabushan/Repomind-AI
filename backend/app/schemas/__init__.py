from datetime import datetime
from typing import Any
from pydantic import BaseModel, field_validator


# ── Repo ──────────────────────────────────────────────────────────────────────
class RepoSubmit(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def github_only(cls, v: str) -> str:
        if "github.com" not in v:
            raise ValueError("Only GitHub URLs are supported")
        return v.rstrip("/")


class RepoOut(BaseModel):
    id: str; url: str; name: str; owner: str
    status: str; created_at: datetime
    model_config = {"from_attributes": True}


# ── Job ───────────────────────────────────────────────────────────────────────
class JobOut(BaseModel):
    id: str; repo_id: str; status: str
    step: str; progress: int; error: str | None
    model_config = {"from_attributes": True}


# ── Analysis ──────────────────────────────────────────────────────────────────
class AnalysisOut(BaseModel):
    id: str; repo_id: str; arch_type: str | None
    languages: list[str]; frameworks: list[str]; databases: list[str]
    auth_methods: list[str]; design_patterns: list[str]
    package_managers: list[str]; deployment_configs: list[str]
    file_count: int; loc_total: int; created_at: datetime
    model_config = {"from_attributes": True}


# ── Document ──────────────────────────────────────────────────────────────────
class DocumentOut(BaseModel):
    id: str; repo_id: str; doc_type: str
    content: str; tokens_used: int; created_at: datetime
    model_config = {"from_attributes": True}


# ── Complexity ────────────────────────────────────────────────────────────────
class ComplexityOut(BaseModel):
    id: str; repo_id: str; overall: int
    maintainability: int; documentation: int
    architecture: int; test_coverage: float; tech_debt: int
    strengths: list[str]; weaknesses: list[str]; suggestions: list[str]
    hotspots: list[str]; created_at: datetime
    model_config = {"from_attributes": True}


# ── Diagram ───────────────────────────────────────────────────────────────────
class DiagramOut(BaseModel):
    id: str; repo_id: str; diagram_type: str
    source: str; created_at: datetime
    model_config = {"from_attributes": True}


# ── Onboarding ────────────────────────────────────────────────────────────────
class OnboardingOut(BaseModel):
    id: str; repo_id: str
    day1: str; day2: str; day3: str
    key_files: list[Any]; checklist: list[str]; created_at: datetime
    model_config = {"from_attributes": True}


# ── Compare ───────────────────────────────────────────────────────────────────
class CompareSubmit(BaseModel):
    url_a: str; url_b: str

    @field_validator("url_a", "url_b")
    @classmethod
    def github_only(cls, v: str) -> str:
        if "github.com" not in v:
            raise ValueError("Only GitHub URLs are supported")
        return v.rstrip("/")


class ComparisonOut(BaseModel):
    id: str; repo_a_id: str; repo_b_id: str
    score_matrix: dict[str, Any]; summary: str | None
    tech_stack_diff: dict[str, Any]; status: str; created_at: datetime
    model_config = {"from_attributes": True}


# ── Chat ──────────────────────────────────────────────────────────────────────
class ChatSessionOut(BaseModel):
    id: str; repo_id: str; mode: str; created_at: datetime
    model_config = {"from_attributes": True}


class ChatMessageIn(BaseModel):
    message: str


class ChatMessageOut(BaseModel):
    id: str; session_id: str; role: str
    content: str; created_at: datetime
    model_config = {"from_attributes": True}
