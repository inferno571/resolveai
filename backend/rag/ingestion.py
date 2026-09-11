"""
ResolveAI — Document Ingestion Pipeline

Handles the full ingestion workflow:
1. Accept files (.md, .txt) or raw text
2. Extract text content
3. Chunk into overlapping segments
4. Embed and store in ChromaDB (dense) + SQLite (BM25/sparse)
5. Store metadata in SQLite documents table
"""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

import chromadb

from config import get_settings
from db.database import create_document, store_document_chunk
from db.models import DocumentMeta
from rag.chunker import Chunk, chunk_text
from rag.embeddings import embed_batch

logger = logging.getLogger(__name__)

# ── ChromaDB Client ───────────────────────────────────────────────

_chroma_client: chromadb.ClientAPI | None = None


def get_chroma_client() -> chromadb.ClientAPI:
    """Get or create the persistent ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        settings = get_settings()
        settings.chroma_path.mkdir(parents=True, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(
            path=str(settings.chroma_path)
        )
    return _chroma_client


def get_collection(name: str = "resolveai_docs") -> chromadb.Collection:
    """Get or create the document chunks collection."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


# ── Ingestion Functions ───────────────────────────────────────────

def ingest_text(
    text: str,
    title: str,
    source: str = "",
    url: str = "",
) -> DocumentMeta:
    """
    Ingest raw text into the RAG corpus.

    Steps:
    1. Chunk the text
    2. Embed all chunks
    3. Store in ChromaDB (dense retrieval)
    4. Store in SQLite document_chunks (BM25 retrieval)
    5. Store document metadata
    """
    doc_id = str(uuid4())

    # Step 1: Chunk
    chunks = chunk_text(
        text=text,
        title=title,
        source=source,
        url=url,
        doc_id=doc_id,
    )

    if not chunks:
        logger.warning(f"No chunks produced for document: {title}")
        return DocumentMeta(id=doc_id, title=title, source=source, url=url, chunk_count=0)

    logger.info(f"Chunked '{title}' into {len(chunks)} chunks")

    # Step 2: Embed
    texts = [c.content for c in chunks]
    embeddings = embed_batch(texts, show_progress=len(texts) > 50)

    # Step 3: Store in ChromaDB
    collection = get_collection()
    collection.add(
        ids=[c.chunk_id for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {
                "doc_id": doc_id,
                "title": c.title,
                "source": source,
                "url": url,
                "chunk_index": c.chunk_index,
            }
            for c in chunks
        ],
    )

    # Step 4: Store parent document metadata first (for foreign key integrity)
    doc = DocumentMeta(
        id=doc_id,
        title=title,
        source=source,
        url=url,
        chunk_count=len(chunks),
    )
    create_document(doc)

    # Step 5: Store chunks in SQLite for BM25
    for chunk in chunks:
        store_document_chunk(
            chunk_id=chunk.chunk_id,
            doc_id=doc_id,
            content=chunk.content,
            title=chunk.title,
            source=source,
            url=url,
            chunk_index=chunk.chunk_index,
        )

    logger.info(f"Ingested '{title}': {len(chunks)} chunks stored in ChromaDB + SQLite")
    return doc


def ingest_file(file_path: str | Path) -> DocumentMeta:
    """Ingest a single file (.md or .txt)."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    text = path.read_text(encoding="utf-8", errors="ignore")
    title = path.stem.replace("_", " ").replace("-", " ").title()

    # Determine source from parent directory name
    source = path.parent.name if path.parent.name != "seed" else "seed-docs"

    return ingest_text(text=text, title=title, source=source)


def ingest_directory(dir_path: str | Path) -> list[DocumentMeta]:
    """Ingest all .md and .txt files in a directory."""
    path = Path(dir_path)
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")

    docs = []
    for file_path in sorted(path.glob("**/*.md")) + sorted(path.glob("**/*.txt")):
        try:
            doc = ingest_file(file_path)
            docs.append(doc)
            logger.info(f"  ✓ Ingested: {file_path.name}")
        except Exception as e:
            logger.error(f"  ✗ Failed to ingest {file_path.name}: {e}")

    logger.info(f"Ingested {len(docs)} documents from {path}")
    return docs


def delete_document_from_chroma(doc_id: str):
    """Remove all chunks for a document from ChromaDB."""
    collection = get_collection()
    # Get all chunk IDs for this document
    results = collection.get(where={"doc_id": doc_id})
    if results["ids"]:
        collection.delete(ids=results["ids"])
        logger.info(f"Deleted {len(results['ids'])} chunks from ChromaDB for doc {doc_id}")


def get_chroma_count() -> int:
    """Get total number of chunks in ChromaDB."""
    try:
        collection = get_collection()
        return collection.count()
    except Exception:
        return 0
