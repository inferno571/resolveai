"""
ResolveAI — CBR Retention Engine

Handles the Revise → Retain part of the CBR cycle:
- When feedback marks a resolution as "solved", create a new verified case
- When user provides a correction, create a revised case
- Deduplication check to prevent near-duplicate cases
"""

from __future__ import annotations

import logging
from typing import Optional

from cbr.entity_extractor import extract_entities
from cbr.similarity import compute_case_similarity
from config import get_settings
from db.database import create_case, get_all_cases
from db.models import CaseCreate, CaseRead

logger = logging.getLogger(__name__)


def _is_near_duplicate(
    new_problem: str,
    existing_cases: list[CaseRead],
    threshold: float = 0.85,
) -> bool:
    """
    Check if a proposed case is too similar to an existing one.
    Uses problem semantic similarity only for speed.
    """
    from rag.embeddings import cosine_similarity, embed_text

    new_embedding = embed_text(new_problem)

    for case in existing_cases:
        case_embedding = embed_text(case.problem)
        sim = cosine_similarity(new_embedding, case_embedding)
        if sim >= threshold:
            logger.info(
                f"Near-duplicate found (similarity={sim:.4f}): "
                f"existing case {case.id}"
            )
            return True

    return False


def retain_case_from_feedback(
    query_text: str,
    error_log: str,
    tool: str,
    operating_system: str,
    version: str,
    resolution: str,
    corrected_solution: Optional[str] = None,
    skip_dedup: bool = False,
) -> Optional[CaseRead]:
    """
    Create a new verified case from a positively-rated resolution.

    This completes the CBR Retain step: verified human feedback
    is stored as a new case for future retrieval.

    Args:
        query_text: Original problem description
        error_log: Error output if any
        tool: Detected tool name
        operating_system: User's OS
        version: Tool/language version
        resolution: The LLM-generated resolution that worked
        corrected_solution: User's correction (overrides resolution)
        skip_dedup: Skip deduplication check

    Returns:
        The newly created CaseRead, or None if it was a duplicate
    """
    # Use corrected solution if provided (Revise step)
    final_solution = corrected_solution if corrected_solution else resolution

    if not final_solution.strip():
        logger.warning("Cannot retain case: empty solution")
        return None

    # Deduplication check
    if not skip_dedup:
        existing = get_all_cases()
        if _is_near_duplicate(query_text, existing):
            logger.info("Case not retained: near-duplicate exists")
            return None

    # Extract entities for structured fields
    entities = extract_entities(f"{query_text}\n{error_log}")

    # Build the case
    case = CaseCreate(
        problem=query_text,
        tool=tool or (entities.tools[0] if entities.tools else ""),
        operating_system=operating_system or (
            entities.os_indicators[0] if entities.os_indicators else ""
        ),
        version=version or (entities.versions[0] if entities.versions else ""),
        error_code="; ".join(entities.error_codes[:3]) if entities.error_codes else "",
        symptoms=error_log[:500] if error_log else "",
        attempted_steps="",
        supporting_evidence="",
        verified_solution=final_solution,
        outcome="solved" if not corrected_solution else "solved (revised)",
        source_url="",
        verification_status="verified",
    )

    created = create_case(case)
    logger.info(f"Retained new verified case: {created.id}")
    return created
