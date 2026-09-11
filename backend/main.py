"""
ResolveAI — FastAPI Application Entry Point

Initializes the application, mounts routers, and configures
CORS, lifespan events, and middleware.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from db.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("resolveai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    # ── Startup ────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("  ResolveAI Backend Starting...")
    logger.info("=" * 60)

    # Initialize database
    init_db()
    logger.info("✓ Database initialized")

    settings = get_settings()
    logger.info(f"✓ LLM Provider: {settings.llm_provider}")
    logger.info(f"✓ Embedding Model: {settings.embedding_model}")
    logger.info(f"✓ CBR Weights: {settings.cbr_weights}")

    yield

    # ── Shutdown ───────────────────────────────────────────────
    logger.info("ResolveAI Backend shutting down...")


# ── Create App ─────────────────────────────────────────────────────

app = FastAPI(
    title="ResolveAI",
    description=(
        "Explainable Technical Troubleshooting Assistant using "
        "Hybrid RAG + CBR + Dual LLM (Ollama / Gemini)"
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ───────────────────────────────────────────────────────────

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount Routers ──────────────────────────────────────────────────

from api.routes.resolve import router as resolve_router
from api.routes.feedback import router as feedback_router
from api.routes.cases import router as cases_router
from api.routes.documents import router as documents_router
from api.routes.admin import router as admin_router

app.include_router(resolve_router, prefix="/api", tags=["Resolution"])
app.include_router(feedback_router, prefix="/api", tags=["Feedback"])
app.include_router(cases_router, prefix="/api", tags=["Cases"])
app.include_router(documents_router, prefix="/api", tags=["Documents"])
app.include_router(admin_router, prefix="/api", tags=["Admin"])


@app.get("/", tags=["Health"])
@app.get("/api/health", tags=["Health"])
async def root():
    """Root endpoint — basic health check."""
    return {
        "name": "ResolveAI",
        "status": "running",
        "version": "0.1.0",
        "docs": "/docs",
    }


# ── Run directly ──────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
