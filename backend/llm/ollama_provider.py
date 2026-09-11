"""
ResolveAI — Ollama LLM Provider

Connects to a local Ollama server for inference with models like Qwen3.
Uses the Ollama HTTP API directly via httpx for full control.
"""

from __future__ import annotations

import logging
import time

import httpx

from config import get_settings
from db.models import LLMResponse
from llm.base import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Local LLM provider via Ollama HTTP API."""

    def __init__(self):
        settings = get_settings()
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        """Generate a response using Ollama's /api/generate endpoint."""
        start = time.time()

        # For Qwen3 thinking models, use /no_think tag to control output
        if "qwen" in self.model.lower():
            prompt = f"{prompt}\n/no_think"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

            content = data.get("response", "")
            latency = (time.time() - start) * 1000

            logger.info(
                f"Ollama generate: model={self.model}, "
                f"tokens={data.get('eval_count', '?')}, "
                f"latency={latency:.0f}ms"
            )

            return LLMResponse(
                content=content,
                model=self.model,
                provider="ollama",
                tokens_used=data.get("eval_count"),
                latency_ms=round(latency, 2),
            )

        except httpx.ConnectError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Is Ollama running? Start it with: ollama serve"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e.response.status_code}")
            raise RuntimeError(f"Ollama error: {e.response.text}")

    async def health_check(self) -> bool:
        """Check if Ollama is running and the model is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    # Check if our model (or a variant) is loaded
                    model_base = self.model.split(":")[0]
                    return any(model_base in m for m in models)
            return False
        except Exception:
            return False

    async def is_model_loaded(self) -> bool:
        """Check if the specific model is available."""
        return await self.health_check()

    def get_provider_name(self) -> str:
        return "ollama"

    def get_model_name(self) -> str:
        return self.model
