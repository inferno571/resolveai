"""
ResolveAI — Pydantic Models

Request/response schemas for the API and internal data transfer objects.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════
#  Enums
# ═══════════════════════════════════════════════════════════════════

class VerificationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Outcome(str, Enum):
    SOLVED = "solved"
    PARTIAL = "partial"
    UNSOLVED = "unsolved"


class LLMProviderType(str, Enum):
    OLLAMA = "ollama"
    GEMINI = "gemini"


# ═══════════════════════════════════════════════════════════════════
#  Case Models (CBR Casebase)
# ═══════════════════════════════════════════════════════════════════

class CaseBase(BaseModel):
    """Fields shared across case create / read operations."""
    problem: str
    tool: str = ""
    operating_system: str = ""
    version: str = ""
    error_code: str = ""
    symptoms: str = ""
    attempted_steps: str = ""
    supporting_evidence: str = ""
    verified_solution: str = ""
    outcome: str = "solved"
    source_url: str = ""


class CaseCreate(CaseBase):
    """Schema for creating a new case."""
    verification_status: str = "pending"


class CaseRead(CaseBase):
    """Schema for reading a case from the database."""
    id: str
    verification_status: str
    created_at: datetime


class CaseSimilarityResult(BaseModel):
    """A case with its similarity breakdown."""
    case: CaseRead
    total_score: float
    component_scores: dict[str, float]
    match_explanation: str


# ═══════════════════════════════════════════════════════════════════
#  Document Models (RAG Corpus)
# ═══════════════════════════════════════════════════════════════════

class DocumentMeta(BaseModel):
    """Metadata for an ingested document."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    source: str = ""
    url: str = ""
    chunk_count: int = 0
    ingested_at: datetime = Field(default_factory=datetime.utcnow)


class RetrievedChunk(BaseModel):
    """A single retrieved document chunk."""
    chunk_id: str
    content: str
    source: str
    title: str
    url: str = ""
    score: float
    retrieval_method: str  # "dense", "sparse", or "hybrid"


# ═══════════════════════════════════════════════════════════════════
#  Query / Resolution Models
# ═══════════════════════════════════════════════════════════════════

class ResolveRequest(BaseModel):
    """User's issue submission."""
    problem: str = Field(..., min_length=10, description="Describe your technical problem")
    tool: Optional[str] = Field(None, description="Tool name (python, pip, git, etc.)")
    operating_system: Optional[str] = Field(None, description="Your OS (windows, linux, macos)")
    version: Optional[str] = Field(None, description="Tool/language version")
    error_log: Optional[str] = Field(None, description="Paste your error output here")


class ResolutionStep(BaseModel):
    """A single step in the resolution."""
    step_number: int
    instruction: str
    code: Optional[str] = None
    warning: Optional[str] = None


class Citation(BaseModel):
    """A document citation in the response."""
    source: str
    title: str
    url: str = ""
    relevant_text: str


class ResolveResponse(BaseModel):
    """Full resolution response returned to the user."""
    query_id: str
    diagnosis: str
    confidence: str  # "high", "medium", "low"
    steps: list[ResolutionStep]
    citations: list[Citation]
    similar_cases: list[CaseSimilarityResult]
    warnings: list[str] = []
    llm_provider_used: str
    retrieval_metadata: dict = {}


# ═══════════════════════════════════════════════════════════════════
#  Feedback Models
# ═══════════════════════════════════════════════════════════════════

class FeedbackCreate(BaseModel):
    """User feedback on a resolution."""
    query_id: str
    resolved: bool
    corrected_solution: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class FeedbackRead(BaseModel):
    """Feedback record from the database."""
    id: str
    query_id: str
    resolved: bool
    corrected_solution: Optional[str]
    rating: Optional[int]
    created_at: datetime


# ═══════════════════════════════════════════════════════════════════
#  Admin / Config Models
# ═══════════════════════════════════════════════════════════════════

class ConfigUpdate(BaseModel):
    """Partial config update from admin panel."""
    llm_provider: Optional[str] = None
    ollama_model: Optional[str] = None
    gemini_model: Optional[str] = None
    gemini_api_key: Optional[str] = None
    cbr_weight_problem: Optional[float] = None
    cbr_weight_evidence: Optional[float] = None
    cbr_weight_entity: Optional[float] = None
    cbr_weight_environment: Optional[float] = None
    enable_reranker: Optional[bool] = None


class HealthStatus(BaseModel):
    """System health check response."""
    status: str  # "healthy", "degraded", "unhealthy"
    ollama_connected: bool
    ollama_model_loaded: bool
    gemini_configured: bool
    chroma_documents: int
    casebase_size: int
    embedding_model: str


class SystemMetrics(BaseModel):
    """Evaluation and system metrics."""
    total_queries: int
    total_cases: int
    verified_cases: int
    total_feedback: int
    positive_feedback_rate: float
    avg_rating: float
    cases_by_tool: dict[str, int]
    cases_by_os: dict[str, int]


# ═══════════════════════════════════════════════════════════════════
#  Evaluation Models
# ═══════════════════════════════════════════════════════════════════

class EvaluationConfig(BaseModel):
    """Configuration for running an ablation experiment."""
    test_queries: list[dict] = []  # List of {problem, expected_answer, ...}
    modes: list[str] = ["llm_only", "rag_only", "cbr_only", "rag_cbr", "rag_cbr_reranker"]


class EvaluationResult(BaseModel):
    """Result of a single evaluation mode."""
    mode: str
    metrics: dict[str, float]
    sample_results: list[dict] = []


# ═══════════════════════════════════════════════════════════════════
#  LLM Internal Models
# ═══════════════════════════════════════════════════════════════════

class LLMResponse(BaseModel):
    """Response from an LLM provider."""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
