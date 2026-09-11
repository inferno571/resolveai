"""
ResolveAI — Hybrid RAG Retriever

Combines dense (ChromaDB) and sparse (BM25/FTS5) retrieval using
Reciprocal Rank Fusion (RRF) for the best of both worlds.
"""

from __future__ import annotations

import logging
from typing import Optional

from db.database import search_chunks_bm25
from db.models import RetrievedChunk
from rag.embeddings import embed_text
from rag.ingestion import get_collection

logger = logging.getLogger(__name__)


def retrieve_dense(query: str, top_k: int = 10) -> list[RetrievedChunk]:
    """Dense retrieval from ChromaDB using embedding similarity."""
    query_embedding = embed_text(query)
    collection = get_collection()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    if results["ids"] and results["ids"][0]:
        for i, chunk_id in enumerate(results["ids"][0]):
            # ChromaDB returns distances; for cosine, similarity = 1 - distance
            distance = results["distances"][0][i] if results["distances"] else 0
            score = 1.0 - distance  # Convert distance to similarity

            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            content = results["documents"][0][i] if results["documents"] else ""

            chunks.append(RetrievedChunk(
                chunk_id=chunk_id,
                content=content,
                source=metadata.get("source", ""),
                title=metadata.get("title", ""),
                url=metadata.get("url", ""),
                score=round(score, 4),
                retrieval_method="dense",
            ))

    return chunks


def retrieve_sparse(query: str, top_k: int = 10) -> list[RetrievedChunk]:
    """Sparse retrieval using SQLite FTS5 / BM25."""
    # Clean query for FTS5 syntax (remove special chars)
    clean_query = " ".join(
        word for word in query.split()
        if not any(c in word for c in "(){}[]\"'*")
    )

    if not clean_query.strip():
        return []

    try:
        results = search_chunks_bm25(clean_query, limit=top_k)
    except Exception as e:
        logger.warning(f"BM25 search failed: {e}")
        return []

    chunks = []
    for row in results:
        # FTS5 rank is negative (more negative = better match)
        # Normalize to 0-1 range approximately
        raw_score = abs(row.get("score", 0))
        normalized = min(raw_score / 25.0, 1.0)  # rough normalization

        chunks.append(RetrievedChunk(
            chunk_id=row.get("id", ""),
            content=row.get("content", ""),
            source=row.get("source", ""),
            title=row.get("title", ""),
            url=row.get("url", ""),
            score=round(normalized, 4),
            retrieval_method="sparse",
        ))

    return chunks


def reciprocal_rank_fusion(
    result_lists: list[list[RetrievedChunk]],
    k: int = 60,
) -> list[RetrievedChunk]:
    """
    Merge multiple ranked lists using Reciprocal Rank Fusion (RRF).

    RRF score = Σ 1 / (k + rank_i) for each list where the item appears.
    Default k=60 following the original RRF paper.
    """
    # Map chunk_id → (best chunk object, cumulative RRF score)
    fusion_scores: dict[str, tuple[RetrievedChunk, float]] = {}

    for result_list in result_lists:
        for rank, chunk in enumerate(result_list):
            rrf_score = 1.0 / (k + rank + 1)  # rank is 0-indexed

            if chunk.chunk_id in fusion_scores:
                existing_chunk, existing_score = fusion_scores[chunk.chunk_id]
                fusion_scores[chunk.chunk_id] = (existing_chunk, existing_score + rrf_score)
            else:
                fusion_scores[chunk.chunk_id] = (chunk, rrf_score)

    # Sort by RRF score descending
    sorted_results = sorted(fusion_scores.values(), key=lambda x: x[1], reverse=True)

    # Update scores and mark as hybrid
    fused_chunks = []
    for chunk, rrf_score in sorted_results:
        fused_chunk = RetrievedChunk(
            chunk_id=chunk.chunk_id,
            content=chunk.content,
            source=chunk.source,
            title=chunk.title,
            url=chunk.url,
            score=round(rrf_score, 4),
            retrieval_method="hybrid",
        )
        fused_chunks.append(fused_chunk)

    return fused_chunks


def retrieve_hybrid(
    query: str,
    top_k: int = 5,
    dense_k: int = 10,
    sparse_k: int = 10,
) -> list[RetrievedChunk]:
    """
    Hybrid retrieval: dense + sparse fused with RRF.

    1. Get top-N from dense (ChromaDB)
    2. Get top-N from sparse (BM25)
    3. Fuse with RRF
    4. Return top-k
    """
    logger.info(f"Hybrid retrieval: query='{query[:80]}...' top_k={top_k}")

    dense_results = retrieve_dense(query, top_k=dense_k)
    sparse_results = retrieve_sparse(query, top_k=sparse_k)

    logger.info(f"  Dense results: {len(dense_results)}, Sparse results: {len(sparse_results)}")

    if not dense_results and not sparse_results:
        return []

    fused = reciprocal_rank_fusion([dense_results, sparse_results])

    return fused[:top_k]
