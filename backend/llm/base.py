"""
ResolveAI — Abstract LLM Provider

Base class for all LLM backends (Ollama, Gemini, etc.)
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from db.models import LLMResponse


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is available and ready."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name (e.g., 'ollama', 'gemini')."""
        ...

    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model name being used."""
        ...
