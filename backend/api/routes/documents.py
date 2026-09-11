"""
ResolveAI — Documents Endpoint

Handles document ingestion and management for the RAG corpus.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from db.database import list_documents, delete_document
from rag.ingestion import ingest_text, ingest_file, delete_document_from_chroma

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/documents")
async def get_documents():
    """List all ingested documents."""
    docs = list_documents()
    return [doc.model_dump() for doc in docs]


@router.post("/documents/ingest")
async def ingest_document(
    file: UploadFile = File(None),
    title: str = Form(""),
    source: str = Form(""),
    url: str = Form(""),
    text_content: str = Form(""),
):
    """
    Ingest a document into the RAG corpus.

    Either upload a file (.md, .txt) or provide text_content directly.
    """
    try:
        if file:
            # Save uploaded file temporarily and ingest
            suffix = Path(file.filename).suffix if file.filename else ".txt"
            if suffix not in (".md", ".txt", ".html"):
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {suffix}. Use .md, .txt, or .html"
                )

            content = await file.read()
            text = content.decode("utf-8", errors="ignore")
            doc_title = title or (file.filename or "Uploaded Document")

            doc = ingest_text(
                text=text,
                title=doc_title,
                source=source or "upload",
                url=url,
            )

        elif text_content:
            if not title:
                raise HTTPException(
                    status_code=400,
                    detail="Title is required when providing text_content"
                )
            doc = ingest_text(
                text=text_content,
                title=title,
                source=source or "manual",
                url=url,
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Provide either a file upload or text_content"
            )

        return {
            "message": "Document ingested successfully",
            "document": doc.model_dump(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{doc_id}")
async def remove_document(doc_id: str):
    """Remove a document and its chunks from both ChromaDB and SQLite."""
    try:
        # Delete from ChromaDB
        delete_document_from_chroma(doc_id)
        # Delete from SQLite
        deleted = delete_document(doc_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted", "id": doc_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
