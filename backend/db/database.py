"""
ResolveAI — SQLite Database Layer

Handles schema creation, connection management, and CRUD operations for:
- cases (CBR casebase)
- documents (RAG corpus metadata)
- queries (query history)
- feedback (user feedback on resolutions)
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from config import get_settings
from db.models import (
    CaseCreate,
    CaseRead,
    FeedbackCreate,
    FeedbackRead,
    DocumentMeta,
)

# ═══════════════════════════════════════════════════════════════════
#  Schema Definitions
# ═══════════════════════════════════════════════════════════════════

SCHEMA_SQL = """
-- CBR Casebase
CREATE TABLE IF NOT EXISTS cases (
    id                  TEXT PRIMARY KEY,
    problem             TEXT NOT NULL,
    tool                TEXT DEFAULT '',
    operating_system    TEXT DEFAULT '',
    version             TEXT DEFAULT '',
    error_code          TEXT DEFAULT '',
    symptoms            TEXT DEFAULT '',
    attempted_steps     TEXT DEFAULT '',
    supporting_evidence TEXT DEFAULT '',
    verified_solution   TEXT DEFAULT '',
    outcome             TEXT DEFAULT 'solved',
    source_url          TEXT DEFAULT '',
    verification_status TEXT DEFAULT 'pending',
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Full-Text Search index on cases for BM25 lexical retrieval
CREATE VIRTUAL TABLE IF NOT EXISTS cases_fts USING fts5(
    problem,
    error_code,
    symptoms,
    verified_solution,
    content='cases',
    content_rowid='rowid'
);

-- Triggers to keep FTS in sync with cases table
CREATE TRIGGER IF NOT EXISTS cases_ai AFTER INSERT ON cases BEGIN
    INSERT INTO cases_fts(rowid, problem, error_code, symptoms, verified_solution)
    VALUES (new.rowid, new.problem, new.error_code, new.symptoms, new.verified_solution);
END;

CREATE TRIGGER IF NOT EXISTS cases_ad AFTER DELETE ON cases BEGIN
    INSERT INTO cases_fts(cases_fts, rowid, problem, error_code, symptoms, verified_solution)
    VALUES ('delete', old.rowid, old.problem, old.error_code, old.symptoms, old.verified_solution);
END;

CREATE TRIGGER IF NOT EXISTS cases_au AFTER UPDATE ON cases BEGIN
    INSERT INTO cases_fts(cases_fts, rowid, problem, error_code, symptoms, verified_solution)
    VALUES ('delete', old.rowid, old.problem, old.error_code, old.symptoms, old.verified_solution);
    INSERT INTO cases_fts(rowid, problem, error_code, symptoms, verified_solution)
    VALUES (new.rowid, new.problem, new.error_code, new.symptoms, new.verified_solution);
END;

-- RAG Document metadata
CREATE TABLE IF NOT EXISTS documents (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    source      TEXT DEFAULT '',
    url         TEXT DEFAULT '',
    chunk_count INTEGER DEFAULT 0,
    ingested_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Query history
CREATE TABLE IF NOT EXISTS queries (
    id              TEXT PRIMARY KEY,
    problem_text    TEXT NOT NULL,
    tool            TEXT DEFAULT '',
    os              TEXT DEFAULT '',
    error_log       TEXT DEFAULT '',
    llm_provider    TEXT DEFAULT '',
    response        TEXT DEFAULT '',
    rag_results     TEXT DEFAULT '[]',
    cbr_results     TEXT DEFAULT '[]',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User feedback
CREATE TABLE IF NOT EXISTS feedback (
    id                  TEXT PRIMARY KEY,
    query_id            TEXT NOT NULL,
    resolved            BOOLEAN NOT NULL,
    corrected_solution  TEXT DEFAULT '',
    rating              INTEGER,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (query_id) REFERENCES queries(id)
);

-- FTS index on document chunks stored in a flat table for BM25 search
CREATE TABLE IF NOT EXISTS document_chunks (
    id          TEXT PRIMARY KEY,
    doc_id      TEXT NOT NULL,
    content     TEXT NOT NULL,
    title       TEXT DEFAULT '',
    source      TEXT DEFAULT '',
    url         TEXT DEFAULT '',
    chunk_index INTEGER DEFAULT 0,
    FOREIGN KEY (doc_id) REFERENCES documents(id)
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
    content,
    title,
    source,
    content='document_chunks',
    content_rowid='rowid'
);

CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON document_chunks BEGIN
    INSERT INTO chunks_fts(rowid, content, title, source)
    VALUES (new.rowid, new.content, new.title, new.source);
END;

CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON document_chunks BEGIN
    INSERT INTO chunks_fts(chunks_fts, rowid, content, title, source)
    VALUES ('delete', old.rowid, old.content, old.title, old.source);
END;
"""


# ═══════════════════════════════════════════════════════════════════
#  Connection Management
# ═══════════════════════════════════════════════════════════════════

def get_db_path() -> Path:
    settings = get_settings()
    path = settings.sqlite_path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_connection() -> sqlite3.Connection:
    """Get a new SQLite connection with row factory."""
    conn = sqlite3.connect(str(get_db_path()))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables and indexes."""
    conn = get_connection()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════════════
#  Case CRUD Operations
# ═══════════════════════════════════════════════════════════════════

def create_case(case: CaseCreate) -> CaseRead:
    """Insert a new case into the casebase."""
    conn = get_connection()
    case_id = str(uuid4())
    now = datetime.utcnow()
    conn.execute(
        """INSERT INTO cases
           (id, problem, tool, operating_system, version, error_code,
            symptoms, attempted_steps, supporting_evidence, verified_solution,
            outcome, source_url, verification_status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            case_id, case.problem, case.tool, case.operating_system,
            case.version, case.error_code, case.symptoms, case.attempted_steps,
            case.supporting_evidence, case.verified_solution, case.outcome,
            case.source_url, case.verification_status, now,
        ),
    )
    conn.commit()
    conn.close()
    return CaseRead(id=case_id, created_at=now, **case.model_dump())


def get_case(case_id: str) -> Optional[CaseRead]:
    """Retrieve a single case by ID."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    return CaseRead(**dict(row))


def list_cases(
    tool: Optional[str] = None,
    operating_system: Optional[str] = None,
    verification_status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> list[CaseRead]:
    """List cases with optional filters."""
    conn = get_connection()
    query = "SELECT * FROM cases WHERE 1=1"
    params: list = []
    if tool:
        query += " AND tool = ?"
        params.append(tool)
    if operating_system:
        query += " AND operating_system = ?"
        params.append(operating_system)
    if verification_status:
        query += " AND verification_status = ?"
        params.append(verification_status)
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [CaseRead(**dict(row)) for row in rows]


def get_all_cases() -> list[CaseRead]:
    """Get all cases (for CBR retrieval)."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM cases").fetchall()
    conn.close()
    return [CaseRead(**dict(row)) for row in rows]


def delete_case(case_id: str) -> bool:
    """Delete a case by ID."""
    conn = get_connection()
    cursor = conn.execute("DELETE FROM cases WHERE id = ?", (case_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def count_cases() -> int:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
    conn.close()
    return count


def count_verified_cases() -> int:
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM cases WHERE verification_status = 'verified'"
    ).fetchone()[0]
    conn.close()
    return count


def cases_by_tool() -> dict[str, int]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT tool, COUNT(*) as cnt FROM cases WHERE tool != '' GROUP BY tool ORDER BY cnt DESC"
    ).fetchall()
    conn.close()
    return {row["tool"]: row["cnt"] for row in rows}


def cases_by_os() -> dict[str, int]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT operating_system, COUNT(*) as cnt FROM cases WHERE operating_system != '' GROUP BY operating_system ORDER BY cnt DESC"
    ).fetchall()
    conn.close()
    return {row["operating_system"]: row["cnt"] for row in rows}


# ═══════════════════════════════════════════════════════════════════
#  Document Metadata CRUD
# ═══════════════════════════════════════════════════════════════════

def create_document(doc: DocumentMeta) -> DocumentMeta:
    conn = get_connection()
    conn.execute(
        """INSERT INTO documents (id, title, source, url, chunk_count, ingested_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (doc.id, doc.title, doc.source, doc.url, doc.chunk_count, doc.ingested_at),
    )
    conn.commit()
    conn.close()
    return doc


def list_documents() -> list[DocumentMeta]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM documents ORDER BY ingested_at DESC").fetchall()
    conn.close()
    return [DocumentMeta(**dict(row)) for row in rows]


def delete_document(doc_id: str) -> bool:
    conn = get_connection()
    conn.execute("DELETE FROM document_chunks WHERE doc_id = ?", (doc_id,))
    cursor = conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def count_document_chunks() -> int:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM document_chunks").fetchone()[0]
    conn.close()
    return count


# ── Document chunk storage (for BM25) ─────────────────────────────

def store_document_chunk(
    chunk_id: str, doc_id: str, content: str,
    title: str, source: str, url: str, chunk_index: int,
):
    conn = get_connection()
    conn.execute(
        """INSERT INTO document_chunks (id, doc_id, content, title, source, url, chunk_index)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (chunk_id, doc_id, content, title, source, url, chunk_index),
    )
    conn.commit()
    conn.close()


def search_chunks_bm25(query: str, limit: int = 10) -> list[dict]:
    """BM25 search over document chunks using FTS5."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT dc.id, dc.content, dc.title, dc.source, dc.url,
                  rank AS score
           FROM chunks_fts
           JOIN document_chunks dc ON chunks_fts.rowid = dc.rowid
           WHERE chunks_fts MATCH ?
           ORDER BY rank
           LIMIT ?""",
        (query, limit),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def search_cases_bm25(query: str, limit: int = 10) -> list[dict]:
    """BM25 search over cases using FTS5."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT c.*, rank AS score
           FROM cases_fts
           JOIN cases c ON cases_fts.rowid = c.rowid
           WHERE cases_fts MATCH ?
           ORDER BY rank
           LIMIT ?""",
        (query, limit),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ═══════════════════════════════════════════════════════════════════
#  Query History CRUD
# ═══════════════════════════════════════════════════════════════════

def save_query(
    query_id: str, problem_text: str, tool: str, os_name: str,
    error_log: str, llm_provider: str, response: str,
    rag_results: list, cbr_results: list,
):
    conn = get_connection()
    conn.execute(
        """INSERT INTO queries
           (id, problem_text, tool, os, error_log, llm_provider, response, rag_results, cbr_results)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            query_id, problem_text, tool, os_name, error_log,
            llm_provider, response, json.dumps(rag_results), json.dumps(cbr_results),
        ),
    )
    conn.commit()
    conn.close()


def count_queries() -> int:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM queries").fetchone()[0]
    conn.close()
    return count


# ═══════════════════════════════════════════════════════════════════
#  Feedback CRUD
# ═══════════════════════════════════════════════════════════════════

def create_feedback(fb: FeedbackCreate) -> FeedbackRead:
    conn = get_connection()
    fb_id = str(uuid4())
    now = datetime.utcnow()
    conn.execute(
        """INSERT INTO feedback (id, query_id, resolved, corrected_solution, rating, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (fb_id, fb.query_id, fb.resolved, fb.corrected_solution, fb.rating, now),
    )
    conn.commit()
    conn.close()
    return FeedbackRead(
        id=fb_id, query_id=fb.query_id, resolved=fb.resolved,
        corrected_solution=fb.corrected_solution, rating=fb.rating, created_at=now,
    )


def get_feedback_for_query(query_id: str) -> list[FeedbackRead]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM feedback WHERE query_id = ? ORDER BY created_at DESC", (query_id,)
    ).fetchall()
    conn.close()
    return [FeedbackRead(**dict(row)) for row in rows]


def count_feedback() -> int:
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
    conn.close()
    return count


def positive_feedback_rate() -> float:
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
    if total == 0:
        return 0.0
    positive = conn.execute("SELECT COUNT(*) FROM feedback WHERE resolved = 1").fetchone()[0]
    conn.close()
    return round(positive / total, 4)


def average_rating() -> float:
    conn = get_connection()
    result = conn.execute("SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL").fetchone()[0]
    conn.close()
    return round(result, 2) if result else 0.0
