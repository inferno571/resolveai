"""
ResolveAI — LLM Orchestrator

Builds structured prompts, manages provider switching, and parses
LLM output into the structured resolution format.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional

from config import get_settings
from db.models import (
    CaseSimilarityResult,
    Citation,
    LLMResponse,
    ResolveResponse,
    ResolutionStep,
    RetrievedChunk,
)
from llm.base import LLMProvider
from llm.gemini_provider import GeminiProvider
from llm.ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)


# ── System Prompt ─────────────────────────────────────────────────

SYSTEM_PROMPT = """You are ResolveAI, an expert technical troubleshooting assistant specializing in Python, pip, virtual environments, and Git.

Your role is to diagnose technical problems and provide step-by-step resolutions based on the evidence provided.

RULES:
1. Base your answer ONLY on the provided documentation evidence and similar cases. Do NOT fabricate information.
2. If the evidence is insufficient, say so clearly with a "low" confidence rating.
3. Always cite which documentation or case informed each step.
4. Never suggest running commands that could damage the system. Add warnings for potentially destructive actions.
5. Be specific: include exact commands, file paths, and version numbers when known.
6. If multiple solutions exist, order them from safest/simplest to most complex.

OUTPUT FORMAT:
You must respond in valid JSON with this exact structure:
{
    "diagnosis": "A clear 1-2 sentence diagnosis of the root cause",
    "confidence": "high" | "medium" | "low",
    "steps": [
        {
            "step_number": 1,
            "instruction": "Clear description of what to do",
            "code": "optional command or code snippet",
            "warning": "optional safety warning"
        }
    ],
    "citations": [
        {
            "source": "document or case source name",
            "title": "title of the referenced material",
            "relevant_text": "the specific text that supports this step"
        }
    ],
    "warnings": ["any general safety warnings or caveats"]
}"""


def _build_prompt(
    problem: str,
    error_log: Optional[str],
    tool: Optional[str],
    operating_system: Optional[str],
    rag_chunks: list[RetrievedChunk],
    similar_cases: list[CaseSimilarityResult],
) -> str:
    """Build the full prompt with retrieved evidence and cases."""
    sections = []

    # ── User's problem ─────────────────────────────────────────
    sections.append("## USER'S PROBLEM")
    sections.append(f"**Description:** {problem}")
    if tool:
        sections.append(f"**Tool:** {tool}")
    if operating_system:
        sections.append(f"**Operating System:** {operating_system}")
    if error_log:
        sections.append(f"**Error Log:**\n```\n{error_log[:2000]}\n```")

    # ── Retrieved documentation (RAG) ──────────────────────────
    if rag_chunks:
        sections.append("\n## DOCUMENTATION EVIDENCE")
        sections.append("The following passages were retrieved from official documentation:")
        for i, chunk in enumerate(rag_chunks[:5], 1):
            sections.append(
                f"\n### Document {i}: {chunk.title} (source: {chunk.source})"
                f"\nRelevance score: {chunk.score:.4f}"
                f"\n{chunk.content[:800]}"
            )

    # ── Similar cases (CBR) ────────────────────────────────────
    if similar_cases:
        sections.append("\n## SIMILAR PREVIOUSLY SOLVED CASES")
        sections.append("These cases were solved before and may be relevant:")
        for i, result in enumerate(similar_cases[:3], 1):
            c = result.case
            sections.append(
                f"\n### Case {i} (similarity: {result.total_score:.4f})"
                f"\n- **Match reason:** {result.match_explanation}"
                f"\n- **Problem:** {c.problem[:300]}"
                f"\n- **Tool:** {c.tool} | **OS:** {c.operating_system}"
                f"\n- **Error:** {c.error_code[:200]}"
                f"\n- **Verified Solution:** {c.verified_solution[:500]}"
                f"\n- **Outcome:** {c.outcome}"
            )

    # ── Instructions ───────────────────────────────────────────
    sections.append("\n## YOUR TASK")
    sections.append(
        "Based on the documentation evidence and similar cases above, "
        "provide a diagnosis and step-by-step resolution. "
        "Respond in the JSON format specified in your system instructions."
    )

    return "\n\n".join(sections)


def _parse_llm_output(content: str) -> dict:
    """Parse LLM output, extracting JSON even if wrapped in markdown."""
    # Try direct JSON parse
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding JSON object in the text
    brace_match = re.search(r"\{.*\}", content, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group())
        except json.JSONDecodeError:
            pass

    # Fallback: return the raw text as diagnosis
    logger.warning("Could not parse LLM output as JSON, using raw text")
    return {
        "diagnosis": content[:500],
        "confidence": "low",
        "steps": [
            {
                "step_number": 1,
                "instruction": content,
            }
        ],
        "citations": [],
        "warnings": ["Note: The LLM response could not be parsed into structured format."],
    }


# ── Provider Management ───────────────────────────────────────────

_providers: dict[str, LLMProvider] = {}


def get_provider(provider_name: str | None = None) -> LLMProvider:
    """Get or create an LLM provider instance."""
    if provider_name is None:
        provider_name = get_settings().llm_provider

    if provider_name not in _providers:
        if provider_name == "ollama":
            _providers[provider_name] = OllamaProvider()
        elif provider_name == "gemini":
            _providers[provider_name] = GeminiProvider()
        else:
            raise ValueError(f"Unknown LLM provider: {provider_name}")

    return _providers[provider_name]


def reset_providers():
    """Reset provider cache (used when config changes)."""
    _providers.clear()


# ── Main Orchestration Function ───────────────────────────────────

async def generate_resolution(
    query_id: str,
    problem: str,
    error_log: Optional[str],
    tool: Optional[str],
    operating_system: Optional[str],
    rag_chunks: list[RetrievedChunk],
    similar_cases: list[CaseSimilarityResult],
    provider_name: str | None = None,
) -> ResolveResponse:
    """
    Generate a full resolution by:
    1. Building a structured prompt with evidence
    2. Calling the selected LLM provider
    3. Parsing the structured output
    4. Returning a ResolveResponse
    """
    # Build prompt
    prompt = _build_prompt(
        problem=problem,
        error_log=error_log,
        tool=tool,
        operating_system=operating_system,
        rag_chunks=rag_chunks,
        similar_cases=similar_cases,
    )

    # Get provider
    provider = get_provider(provider_name)
    logger.info(f"Using LLM provider: {provider.get_provider_name()} ({provider.get_model_name()})")

    # Generate
    llm_response: LLMResponse = await provider.generate(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
    )

    # Parse output
    parsed = _parse_llm_output(llm_response.content)

    # Build response
    steps = []
    for step_data in parsed.get("steps", []):
        steps.append(ResolutionStep(
            step_number=step_data.get("step_number", len(steps) + 1),
            instruction=step_data.get("instruction", ""),
            code=step_data.get("code"),
            warning=step_data.get("warning"),
        ))

    citations = []
    for cite_data in parsed.get("citations", []):
        citations.append(Citation(
            source=cite_data.get("source", ""),
            title=cite_data.get("title", ""),
            url=cite_data.get("url", ""),
            relevant_text=cite_data.get("relevant_text", ""),
        ))

    # Build retrieval metadata for transparency
    retrieval_metadata = {
        "rag_chunks_used": len(rag_chunks),
        "cbr_cases_used": len(similar_cases),
        "top_rag_score": rag_chunks[0].score if rag_chunks else 0,
        "top_cbr_score": similar_cases[0].total_score if similar_cases else 0,
        "llm_latency_ms": llm_response.latency_ms,
        "llm_tokens": llm_response.tokens_used,
    }

    return ResolveResponse(
        query_id=query_id,
        diagnosis=parsed.get("diagnosis", "Unable to determine diagnosis"),
        confidence=parsed.get("confidence", "low"),
        steps=steps,
        citations=citations,
        similar_cases=similar_cases[:3],
        warnings=parsed.get("warnings", []),
        llm_provider_used=f"{provider.get_provider_name()} ({provider.get_model_name()})",
        retrieval_metadata=retrieval_metadata,
    )


async def generate_llm_only(
    query_id: str,
    problem: str,
    error_log: Optional[str],
    tool: Optional[str],
    operating_system: Optional[str],
    provider_name: str | None = None,
) -> ResolveResponse:
    """Generate resolution with LLM only (no RAG, no CBR) — for ablation."""
    return await generate_resolution(
        query_id=query_id,
        problem=problem,
        error_log=error_log,
        tool=tool,
        operating_system=operating_system,
        rag_chunks=[],
        similar_cases=[],
        provider_name=provider_name,
    )
