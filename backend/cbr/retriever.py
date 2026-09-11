"""
ResolveAI — CBR Case Retriever

Retrieves the most similar cases from the casebase for a given query.
Supports pre-filtering by tool/OS for efficiency, and returns ranked
results with full similarity breakdowns.
"""

from __future__ import annotations

import logging
from typing import Optional

from cbr.entity_extractor import ExtractedEntities, extract_entities
from cbr.similarity import compute_case_similarity
from config import get_settings
from db.database import get_all_cases, list_cases
from db.models import CaseRead, CaseSimilarityResult

logger = logging.getLogger(__name__)


def retrieve_similar_cases(
    query_text: str,
    query_error: str = "",
    query_entities: ExtractedEntities | None = None,
    tool_filter: Optional[str] = None,
    os_filter: Optional[str] = None,
    top_k: int = 5,
    min_score: float = 0.1,
) -> list[CaseSimilarityResult]:
    """
    Retrieve the most similar cases from the casebase.

    Args:
        query_text: The user's problem description
        query_error: Error log or error message (optional)
        query_entities: Pre-extracted entities (optional, will extract if None)
        tool_filter: Filter cases by tool before scoring (optional)
        os_filter: Filter cases by OS before scoring (optional)
        top_k: Number of top results to return
        min_score: Minimum similarity score threshold

    Returns:
        Sorted list of CaseSimilarityResult (highest score first)
    """
    # Extract entities if not provided
    if query_entities is None:
        full_text = f"{query_text}\n{query_error}" if query_error else query_text
        query_entities = extract_entities(full_text)

    # Get candidate cases (with optional pre-filtering)
    if tool_filter or os_filter:
        candidates = list_cases(
            tool=tool_filter,
            operating_system=os_filter,
            limit=500,
        )
        # Also get unfiltered cases to avoid missing good matches
        all_cases = get_all_cases()
        # Merge: filtered first, then others not already included
        filtered_ids = {c.id for c in candidates}
        remaining = [c for c in all_cases if c.id not in filtered_ids]
        candidates = candidates + remaining[:200]  # cap for performance
    else:
        candidates = get_all_cases()

    if not candidates:
        logger.info("No cases in casebase for retrieval")
        return []

    logger.info(f"CBR retrieval: scoring {len(candidates)} candidates")

    # Score all candidates
    weights = get_settings().cbr_weights
    results: list[CaseSimilarityResult] = []

    for case in candidates:
        try:
            result = compute_case_similarity(
                query_text=query_text,
                query_error=query_error,
                query_entities=query_entities,
                case=case,
                weights=weights,
            )
            if result.total_score >= min_score:
                results.append(result)
        except Exception as e:
            logger.warning(f"Error scoring case {case.id}: {e}")
            continue

    # Sort by total score descending
    results.sort(key=lambda r: r.total_score, reverse=True)

    top_results = results[:top_k]

    if top_results:
        logger.info(
            f"CBR retrieval: returning {len(top_results)} cases, "
            f"top score={top_results[0].total_score:.4f}"
        )
    else:
        logger.info("CBR retrieval: no cases above minimum score threshold")

    return top_results
