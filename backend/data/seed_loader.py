"""
ResolveAI — Seed Data Loader

Loads seed cases from JSON and seed documentation from markdown files
into the database and vector store.

Usage:
    cd backend
    python -m data.seed_loader
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

# Add parent directory to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_settings
from db.database import init_db, create_case, count_cases, count_document_chunks
from db.models import CaseCreate
from rag.ingestion import ingest_directory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("seed_loader")


def load_seed_cases():
    """Load seed cases from JSON file into the casebase."""
    seed_file = Path(__file__).parent / "seed" / "cases_seed.json"

    if not seed_file.exists():
        logger.error(f"Seed file not found: {seed_file}")
        return

    from db.database import get_all_cases
    existing = get_all_cases()
    existing_problems = {c.problem.lower().strip() for c in existing}

    with open(seed_file, "r", encoding="utf-8") as f:
        cases_data = json.load(f)

    logger.info(f"Checking {len(cases_data)} seed cases (already have {len(existing)})...")

    new_count = 0
    for i, case_data in enumerate(cases_data, 1):
        if case_data.get("problem", "").lower().strip() in existing_problems:
            continue
        try:
            case = CaseCreate(**case_data)
            create_case(case)
            existing_problems.add(case.problem.lower().strip())
            new_count += 1
            logger.info(f"  [+{new_count}] ✓ {case.problem[:60]}...")
        except Exception as e:
            logger.error(f"  Failed to insert case: {e}")

    logger.info(f"Added {new_count} new cases. Total casebase size: {count_cases()}")


def load_seed_documents():
    """Ingest seed documentation into the RAG corpus."""
    docs_dir = Path(__file__).parent / "seed" / "docs"

    if not docs_dir.exists():
        logger.error(f"Seed docs directory not found: {docs_dir}")
        return

    existing_chunks = count_document_chunks()
    if existing_chunks > 0:
        logger.info(f"RAG corpus already has {existing_chunks} chunks. Skipping doc ingestion.")
        logger.info("To reload, delete ChromaDB: rm -rf data/chroma_db")
        return

    logger.info(f"Ingesting documents from {docs_dir}...")
    docs = ingest_directory(docs_dir)
    logger.info(f"Ingested {len(docs)} documents ({count_document_chunks()} total chunks)")


def main():
    """Load all seed data."""
    logger.info("=" * 60)
    logger.info("  ResolveAI — Seed Data Loader")
    logger.info("=" * 60)

    # Initialize database
    init_db()
    logger.info("✓ Database initialized")

    # Load cases
    logger.info("\n--- Loading Seed Cases ---")
    load_seed_cases()

    # Load documents
    logger.info("\n--- Ingesting Seed Documents ---")
    load_seed_documents()

    logger.info("\n" + "=" * 60)
    logger.info("  Seed data loading complete!")
    logger.info(f"  Cases: {count_cases()}")
    logger.info(f"  Document chunks: {count_document_chunks()}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
