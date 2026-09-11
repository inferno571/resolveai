"""
ResolveAI — Gemini API Provider

Uses the official google-genai SDK for Gemini API access.
Supports configurable API key and model selection.
"""

from __future__ import annotations

import logging
import time

from db.models import LLMResponse
from llm.base import LLMProvider

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini API provider."""

    def __init__(self):
        from config import get_settings
        settings = get_settings()
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self._client = None

    def _get_client(self):
        """Lazy-initialize the Gemini client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "Gemini API key not configured. "
                    "Set GEMINI_API_KEY in your .env file. "
                    "Get a key from: https://aistudio.google.com/apikey"
                )
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate a response using Gemini API."""
        start = time.time()

        try:
            from google.genai import types

            client = self._get_client()

            config = types.GenerateContentConfig(
                system_instruction=system_prompt if system_prompt else None,
                temperature=temperature,
                max_output_tokens=max_tokens,
            )

            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )

            content = response.text or ""
            latency = (time.time() - start) * 1000

            # Extract token count if available
            tokens_used = None
            if response.usage_metadata:
                tokens_used = response.usage_metadata.candidates_token_count

            logger.info(
                f"Gemini generate: model={self.model}, "
                f"tokens={tokens_used or '?'}, "
                f"latency={latency:.0f}ms"
            )

            return LLMResponse(
                content=content,
                model=self.model,
                provider="gemini",
                tokens_used=tokens_used,
                latency_ms=round(latency, 2),
            )

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise RuntimeError(f"Gemini API error: {str(e)}")

    async def health_check(self) -> bool:
        """Check if Gemini API is configured and accessible."""
        if not self.api_key:
            return False
        try:
            client = self._get_client()
            # Quick test: list models
            models = client.models.list()
            return True
        except Exception as e:
            logger.warning(f"Gemini health check failed: {e}")
            return False

    def get_provider_name(self) -> str:
        return "gemini"

    def get_model_name(self) -> str:
        return self.model
