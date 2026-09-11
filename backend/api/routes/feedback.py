"""
ResolveAI — Feedback Endpoint

Handles user feedback on resolutions and triggers the
CBR Retain cycle when feedback is positive.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from cbr.retention import retain_case_from_feedback
from db.database import create_feedback, get_feedback_for_query, count_queries
from db.models import FeedbackCreate, FeedbackRead

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/feedback", response_model=FeedbackRead)
async def submit_feedback(feedback: FeedbackCreate):
    """
    Submit feedback on a resolution.

    If resolved=true, the system will attempt to retain the resolution
    as a new verified case in the CBR casebase (Retain step).
    """
    try:
        # Save feedback
        fb = create_feedback(feedback)
        logger.info(
            f"Feedback received: query={feedback.query_id}, "
            f"resolved={feedback.resolved}, rating={feedback.rating}"
        )

        # If positive feedback, trigger CBR retention
        if feedback.resolved:
            try:
                # We need to fetch the query details to build the case
                from db.database import get_connection
                conn = get_connection()
                query_row = conn.execute(
                    "SELECT * FROM queries WHERE id = ?",
                    (feedback.query_id,),
                ).fetchone()
                conn.close()

                if query_row:
                    query_data = dict(query_row)
                    retained = retain_case_from_feedback(
                        query_text=query_data.get("problem_text", ""),
                        error_log=query_data.get("error_log", ""),
                        tool=query_data.get("tool", ""),
                        operating_system=query_data.get("os", ""),
                        version="",
                        resolution=query_data.get("response", ""),
                        corrected_solution=feedback.corrected_solution,
                    )
                    if retained:
                        logger.info(f"CBR Retain: new case {retained.id} from feedback")
                    else:
                        logger.info("CBR Retain: skipped (duplicate or empty)")
                else:
                    logger.warning(f"Query {feedback.query_id} not found for retention")

            except Exception as e:
                # Don't fail the feedback just because retention failed
                logger.error(f"CBR retention failed: {e}")

        return fb

    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/feedback/{query_id}", response_model=list[FeedbackRead])
async def get_feedback(query_id: str):
    """Get all feedback for a specific query."""
    return get_feedback_for_query(query_id)
