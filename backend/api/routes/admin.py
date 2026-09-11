"""
ResolveAI — Admin Endpoint

System health, configuration management, and metrics.
"""

from __future__ import annotations

import logging
import os

from fastapi import APIRouter, HTTPException

from config import get_settings, reload_settings
from db.database import (
    count_cases, count_verified_cases, count_queries,
    count_feedback, count_document_chunks,
    positive_feedback_rate, average_rating,
    cases_by_tool, cases_by_os,
)
from db.models import ConfigUpdate, HealthStatus, SystemMetrics
from llm.orchestrator import get_provider, reset_providers
from rag.ingestion import get_chroma_count

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/admin/health", response_model=HealthStatus)
async def health_check():
    """Full system health check."""
    settings = get_settings()

    # Check Ollama
    ollama_connected = False
    ollama_model_loaded = False
    try:
        from llm.ollama_provider import OllamaProvider
        ollama = OllamaProvider()
        ollama_connected = True
        ollama_model_loaded = await ollama.health_check()
    except Exception:
        pass

    # Check Gemini
    gemini_configured = bool(settings.gemini_api_key)

    return HealthStatus(
        status="healthy" if (ollama_model_loaded or gemini_configured) else "degraded",
        ollama_connected=ollama_connected,
        ollama_model_loaded=ollama_model_loaded,
        gemini_configured=gemini_configured,
        chroma_documents=get_chroma_count(),
        casebase_size=count_cases(),
        embedding_model=settings.embedding_model,
    )


@router.get("/admin/config")
async def get_config():
    """Get current system configuration (safe — no API keys exposed)."""
    settings = get_settings()
    return {
        "llm_provider": settings.llm_provider,
        "ollama_base_url": settings.ollama_base_url,
        "ollama_model": settings.ollama_model,
        "gemini_model": settings.gemini_model,
        "gemini_configured": bool(settings.gemini_api_key),
        "embedding_model": settings.embedding_model,
        "cbr_weights": settings.cbr_weights,
        "enable_reranker": settings.enable_reranker,
    }


@router.patch("/admin/config")
async def update_config(update: ConfigUpdate):
    """
    Update system configuration.

    Changes are applied in-memory and persisted to .env file.
    """
    settings = get_settings()
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")

    updates = {}
    if update.llm_provider is not None:
        updates["LLM_PROVIDER"] = update.llm_provider
    if update.ollama_model is not None:
        updates["OLLAMA_MODEL"] = update.ollama_model
    if update.gemini_model is not None:
        updates["GEMINI_MODEL"] = update.gemini_model
    if update.gemini_api_key is not None:
        updates["GEMINI_API_KEY"] = update.gemini_api_key
    if update.cbr_weight_problem is not None:
        updates["CBR_WEIGHT_PROBLEM"] = str(update.cbr_weight_problem)
    if update.cbr_weight_evidence is not None:
        updates["CBR_WEIGHT_EVIDENCE"] = str(update.cbr_weight_evidence)
    if update.cbr_weight_entity is not None:
        updates["CBR_WEIGHT_ENTITY"] = str(update.cbr_weight_entity)
    if update.cbr_weight_environment is not None:
        updates["CBR_WEIGHT_ENVIRONMENT"] = str(update.cbr_weight_environment)
    if update.enable_reranker is not None:
        updates["ENABLE_RERANKER"] = str(update.enable_reranker).lower()

    # Write updates to .env
    if updates:
        try:
            env_lines = []
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    env_lines = f.readlines()

            for key, value in updates.items():
                found = False
                for i, line in enumerate(env_lines):
                    if line.strip().startswith(f"{key}="):
                        env_lines[i] = f"{key}={value}\n"
                        found = True
                        break
                if not found:
                    env_lines.append(f"{key}={value}\n")

            with open(env_path, "w") as f:
                f.writelines(env_lines)

        except Exception as e:
            logger.warning(f"Could not persist config to .env: {e}")

    # Reload settings and reset providers
    reload_settings()
    reset_providers()

    return {"message": "Configuration updated", "updates": updates}


@router.get("/admin/metrics", response_model=SystemMetrics)
async def get_metrics():
    """Get evaluation and system metrics."""
    return SystemMetrics(
        total_queries=count_queries(),
        total_cases=count_cases(),
        verified_cases=count_verified_cases(),
        total_feedback=count_feedback(),
        positive_feedback_rate=positive_feedback_rate(),
        avg_rating=average_rating(),
        cases_by_tool=cases_by_tool(),
        cases_by_os=cases_by_os(),
    )


@router.post("/admin/test-llm")
async def test_llm(provider: str = "ollama"):
    """Test LLM connection with a simple prompt."""
    try:
        llm = get_provider(provider)
        response = await llm.generate(
            prompt="Say 'ResolveAI is working!' in one short sentence.",
            system_prompt="You are a helpful assistant. Respond briefly.",
            max_tokens=50,
        )
        return {
            "status": "success",
            "provider": provider,
            "model": llm.get_model_name(),
            "response": response.content,
            "latency_ms": response.latency_ms,
        }
    except Exception as e:
        return {
            "status": "error",
            "provider": provider,
            "error": str(e),
        }
