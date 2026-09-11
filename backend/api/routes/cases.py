"""
ResolveAI — Cases Endpoint

CRUD operations for the CBR casebase.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from db.database import (
    create_case, get_case, list_cases, delete_case,
    count_cases, count_verified_cases, cases_by_tool, cases_by_os,
)
from db.models import CaseCreate, CaseRead

router = APIRouter()


@router.get("/cases", response_model=list[CaseRead])
async def get_cases(
    tool: Optional[str] = Query(None),
    operating_system: Optional[str] = Query(None),
    verification_status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """List cases with optional filters."""
    return list_cases(
        tool=tool,
        operating_system=operating_system,
        verification_status=verification_status,
        limit=limit,
        offset=offset,
    )


@router.get("/cases/stats")
async def get_case_stats():
    """Get casebase statistics."""
    return {
        "total_cases": count_cases(),
        "verified_cases": count_verified_cases(),
        "by_tool": cases_by_tool(),
        "by_os": cases_by_os(),
    }


@router.get("/cases/{case_id}", response_model=CaseRead)
async def get_case_by_id(case_id: str):
    """Get a single case by ID."""
    case = get_case(case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/cases", response_model=CaseRead)
async def add_case(case: CaseCreate):
    """Manually add a new case to the casebase."""
    return create_case(case)


@router.delete("/cases/{case_id}")
async def remove_case(case_id: str):
    """Delete a case from the casebase."""
    deleted = delete_case(case_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"message": "Case deleted", "id": case_id}
