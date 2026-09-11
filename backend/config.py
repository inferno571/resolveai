"""
ResolveAI — Central Configuration Module

All settings are loaded from environment variables / .env file.
Uses Pydantic Settings for validation and type coercion.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration loaded from .env"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── LLM Provider ───────────────────────────────────────────────
    llm_provider: Literal["ollama", "gemini"] = "ollama"

    # ── Ollama (Local LLM) ─────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:4b"

    # ── Gemini API ─────────────────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"

    # ── Embeddings ─────────────────────────────────────────────────
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # ── Storage Paths ──────────────────────────────────────────────
    chroma_persist_dir: str = "./data/chroma_db"
    sqlite_db_path: str = "./data/resolveai.db"

    # ── CBR Weights (must sum to 1.0) ──────────────────────────────
    cbr_weight_problem: float = 0.40
    cbr_weight_evidence: float = 0.25
    cbr_weight_entity: float = 0.20
    cbr_weight_environment: float = 0.15

    # ── Server ─────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str | list[str] = ["http://localhost:5173"]

    # ── Optional Features ──────────────────────────────────────────
    enable_reranker: bool = False

    # ── Derived helpers ────────────────────────────────────────────
    @property
    def cbr_weights(self) -> dict[str, float]:
        return {
            "problem": self.cbr_weight_problem,
            "evidence": self.cbr_weight_evidence,
            "entity": self.cbr_weight_entity,
            "environment": self.cbr_weight_environment,
        }

    @property
    def chroma_path(self) -> Path:
        return Path(self.chroma_persist_dir)

    @property
    def sqlite_path(self) -> Path:
        return Path(self.sqlite_db_path)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [origin.strip() for origin in v.split(",")]
        return v


# ── Singleton ──────────────────────────────────────────────────────
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the cached settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Force-reload settings from .env (used by admin config updates)."""
    global _settings
    _settings = Settings()
    return _settings
