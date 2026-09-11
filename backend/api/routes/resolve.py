"""
ResolveAI — Resolve Endpoint

Main resolution endpoint: accepts a problem, retrieves evidence
from RAG + CBR, and generates a cited resolution via LLM.
"""

from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query

from cbr.entity_extractor import extract_entities
from cbr.retriever import retrieve_similar_cases
from db.database import save_query
from db.models import ResolveRequest, ResolveResponse
from llm.orchestrator import generate_resolution, generate_llm_only
from rag.retriever import retrieve_hybrid

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/resolve", response_model=ResolveResponse)
async def resolve_issue(
    request: ResolveRequest,
    provider: str | None = Query(None, description="LLM provider override: 'ollama' or 'gemini'"),
    mode: str = Query("full", description="Resolution mode: 'full', 'rag_only', 'cbr_only', 'llm_only'"),
):
    """
    Submit a technical issue and receive a diagnosed resolution.

    Modes:
    - full: RAG + CBR + LLM (default)
    - rag_only: RAG + LLM (no CBR)
    - cbr_only: CBR + LLM (no RAG)
    - llm_only: LLM only (no retrieval — for ablation)
    """
    query_id = str(uuid4())

    try:
        # Extract entities from the problem
        full_text = request.problem
        if request.error_log:
            full_text += f"\n{request.error_log}"
        entities = extract_entities(full_text)

        # Auto-detect tool and OS if not provided
        tool = request.tool or (entities.tools[0] if entities.tools else "")
        operating_system = request.operating_system or (
            entities.os_indicators[0] if entities.os_indicators else ""
        )

        # ── LLM-only mode (ablation) ──────────────────────────
        if mode == "llm_only":
            response = await generate_llm_only(
                query_id=query_id,
                problem=request.problem,
                error_log=request.error_log,
                tool=tool,
                operating_system=operating_system,
                provider_name=provider,
            )
            # Save query
            save_query(
                query_id=query_id,
                problem_text=request.problem,
                tool=tool,
                os_name=operating_system,
                error_log=request.error_log or "",
                llm_provider=response.llm_provider_used,
                response=response.diagnosis,
                rag_results=[],
                cbr_results=[],
            )
            return response

        # ── Retrieve evidence ──────────────────────────────────
        rag_chunks = []
        similar_cases = []

        if mode in ("full", "rag_only"):
            try:
                rag_chunks = retrieve_hybrid(
                    query=full_text,
                    top_k=5,
                )
                logger.info(f"RAG retrieved {len(rag_chunks)} chunks")
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")

        if mode in ("full", "cbr_only"):
            try:
                similar_cases = retrieve_similar_cases(
                    query_text=request.problem,
                    query_error=request.error_log or "",
                    query_entities=entities,
                    tool_filter=tool if tool else None,
                    top_k=5,
                )
                logger.info(f"CBR retrieved {len(similar_cases)} similar cases")
            except Exception as e:
                logger.warning(f"CBR retrieval failed: {e}")

        # ── Generate resolution ────────────────────────────────
        response = await generate_resolution(
            query_id=query_id,
            problem=request.problem,
            error_log=request.error_log,
            tool=tool,
            operating_system=operating_system,
            rag_chunks=rag_chunks,
            similar_cases=similar_cases,
            provider_name=provider,
        )

        # ── Save query history ─────────────────────────────────
        save_query(
            query_id=query_id,
            problem_text=request.problem,
            tool=tool,
            os_name=operating_system,
            error_log=request.error_log or "",
            llm_provider=response.llm_provider_used,
            response=response.diagnosis,
            rag_results=[
                {"title": c.title, "source": c.source, "score": c.score}
                for c in rag_chunks
            ],
            cbr_results=[
                {"case_id": r.case.id, "score": r.total_score}
                for r in similar_cases
            ],
        )

        return response

    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Resolution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Resolution failed: {str(e)}")
