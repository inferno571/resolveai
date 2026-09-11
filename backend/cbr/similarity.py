"""
ResolveAI — CBR Similarity Engine

Transparent, multi-field case similarity scoring.
Every score component is individually computed and explainable.

Default weights (configurable):
  0.40 × problem semantic similarity
  0.25 × evidence/error similarity
  0.20 × entity/error-code overlap (Jaccard)
  0.15 × environment/tool match (exact)
"""

from __future__ import annotations

import logging

from cbr.entity_extractor import ExtractedEntities, extract_entities
from config import get_settings
from db.models import CaseRead, CaseSimilarityResult
from rag.embeddings import cosine_similarity, embed_text

logger = logging.getLogger(__name__)


def _jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
    """Jaccard similarity between two sets of strings (case-insensitive)."""
    a = {s.lower().strip() for s in set_a if s.strip()}
    b = {s.lower().strip() for s in set_b if s.strip()}
    if not a and not b:
        return 0.0
    if not a or not b:
        return 0.0
    intersection = a & b
    union = a | b
    return len(intersection) / len(union)


def _environment_match(
    query_tools: list[str],
    query_os: list[str],
    case_tool: str,
    case_os: str,
) -> float:
    """
    Score environment match (tool + OS).
    Returns 1.0 for exact match, 0.5 for partial, 0.0 for no match.
    """
    tool_score = 0.0
    os_score = 0.0

    # Tool match
    if case_tool:
        case_tool_lower = case_tool.lower().strip()
        for qt in query_tools:
            if qt.lower().strip() == case_tool_lower:
                tool_score = 1.0
                break
            if qt.lower().strip() in case_tool_lower or case_tool_lower in qt.lower().strip():
                tool_score = 0.5

    # OS match
    if case_os:
        case_os_lower = case_os.lower().strip()
        for qo in query_os:
            if qo.lower().strip() == case_os_lower:
                os_score = 1.0
                break
            if qo.lower().strip() in case_os_lower or case_os_lower in qo.lower().strip():
                os_score = 0.5

    # Weighted: tool matters more than OS for tech troubleshooting
    if case_tool and case_os:
        return 0.6 * tool_score + 0.4 * os_score
    elif case_tool:
        return tool_score
    elif case_os:
        return os_score
    else:
        return 0.0


def compute_case_similarity(
    query_text: str,
    query_error: str,
    query_entities: ExtractedEntities,
    case: CaseRead,
    weights: dict[str, float] | None = None,
) -> CaseSimilarityResult:
    """
    Compute transparent multi-field similarity between a query and a case.

    Returns a CaseSimilarityResult with:
    - total_score: weighted sum of all components
    - component_scores: individual scores for each field
    - match_explanation: human-readable explanation
    """
    if weights is None:
        weights = get_settings().cbr_weights

    # ── 1. Problem semantic similarity ─────────────────────────
    query_embedding = embed_text(query_text)
    case_problem_embedding = embed_text(case.problem)
    problem_sim = cosine_similarity(query_embedding, case_problem_embedding)

    # ── 2. Evidence / error similarity ─────────────────────────
    evidence_text = f"{case.error_code} {case.symptoms}".strip()
    if evidence_text and query_error:
        query_error_embedding = embed_text(query_error)
        evidence_embedding = embed_text(evidence_text)
        evidence_sim = cosine_similarity(query_error_embedding, evidence_embedding)
    elif evidence_text:
        evidence_embedding = embed_text(evidence_text)
        evidence_sim = cosine_similarity(query_embedding, evidence_embedding)
    else:
        evidence_sim = 0.0

    # ── 3. Entity / error-code overlap (Jaccard) ───────────────
    case_entities = extract_entities(
        f"{case.problem} {case.error_code} {case.symptoms} {case.verified_solution}"
    )
    query_entity_set = set(query_entities.all_entities())
    case_entity_set = set(case_entities.all_entities())
    entity_sim = _jaccard_similarity(query_entity_set, case_entity_set)

    # ── 4. Environment / tool match ────────────────────────────
    env_sim = _environment_match(
        query_tools=query_entities.tools,
        query_os=query_entities.os_indicators,
        case_tool=case.tool,
        case_os=case.operating_system,
    )

    # ── Weighted total ─────────────────────────────────────────
    total = (
        weights.get("problem", 0.40) * problem_sim
        + weights.get("evidence", 0.25) * evidence_sim
        + weights.get("entity", 0.20) * entity_sim
        + weights.get("environment", 0.15) * env_sim
    )

    # ── Build explanation ──────────────────────────────────────
    component_scores = {
        "problem": round(problem_sim, 4),
        "evidence": round(evidence_sim, 4),
        "entity": round(entity_sim, 4),
        "environment": round(env_sim, 4),
    }

    explanation_parts = []
    if problem_sim > 0.7:
        explanation_parts.append(f"Strong problem match ({problem_sim:.0%})")
    elif problem_sim > 0.4:
        explanation_parts.append(f"Moderate problem match ({problem_sim:.0%})")

    if evidence_sim > 0.7:
        explanation_parts.append(f"similar error pattern ({evidence_sim:.0%})")
    
    if entity_sim > 0.3:
        shared = query_entity_set & {e.lower() for e in case_entity_set}
        if shared:
            explanation_parts.append(f"shared entities: {', '.join(list(shared)[:3])}")

    if env_sim > 0.5:
        env_parts = []
        if case.tool:
            env_parts.append(case.tool)
        if case.operating_system:
            env_parts.append(case.operating_system)
        explanation_parts.append(f"same environment ({', '.join(env_parts)})")

    explanation = "; ".join(explanation_parts) if explanation_parts else "Low similarity across all fields"

    return CaseSimilarityResult(
        case=case,
        total_score=round(total, 4),
        component_scores=component_scores,
        match_explanation=explanation,
    )
