"""
ResolveAI — Embedding Module

Loads and caches the sentence-transformer embedding model.
Provides single and batch embedding functions.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Union

import numpy as np
from sentence_transformers import SentenceTransformer

from config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_model() -> SentenceTransformer:
    """Load and cache the embedding model."""
    settings = get_settings()
    model_name = settings.embedding_model
    logger.info(f"Loading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    logger.info(f"Embedding model loaded. Dimension: {model.get_sentence_embedding_dimension()}")
    return model


def embed_text(text: str) -> list[float]:
    """Embed a single text string → vector."""
    model = _load_model()
    # BGE models benefit from the "Represent this sentence:" prefix for retrieval
    if "bge" in get_settings().embedding_model.lower():
        text = f"Represent this sentence for searching relevant passages: {text}"
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_batch(texts: list[str], show_progress: bool = False) -> list[list[float]]:
    """Embed a batch of texts → list of vectors."""
    model = _load_model()
    prefix = ""
    if "bge" in get_settings().embedding_model.lower():
        prefix = "Represent this sentence for searching relevant passages: "
    prefixed = [f"{prefix}{t}" for t in texts]
    embeddings = model.encode(
        prefixed,
        normalize_embeddings=True,
        show_progress_bar=show_progress,
        batch_size=32,
    )
    return embeddings.tolist()


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def get_embedding_dimension() -> int:
    """Return the embedding dimension of the loaded model."""
    model = _load_model()
    return model.get_sentence_embedding_dimension()
