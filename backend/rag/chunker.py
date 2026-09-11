"""
ResolveAI — Text Chunker

Splits documents into overlapping chunks suitable for RAG retrieval.
Markdown-aware: respects headers, code blocks, and list boundaries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4


@dataclass
class Chunk:
    """A single text chunk with metadata."""
    chunk_id: str = field(default_factory=lambda: str(uuid4()))
    content: str = ""
    title: str = ""
    source: str = ""
    url: str = ""
    chunk_index: int = 0
    doc_id: str = ""


def _count_tokens_approx(text: str) -> int:
    """Approximate token count (words ≈ 0.75 tokens, but we use words as proxy)."""
    return len(text.split())


def _split_by_markdown_headers(text: str) -> list[dict]:
    """Split text into sections by markdown headers."""
    sections = []
    current_title = ""
    current_content = []

    for line in text.split("\n"):
        header_match = re.match(r"^(#{1,4})\s+(.+)$", line)
        if header_match:
            # Save previous section
            if current_content:
                sections.append({
                    "title": current_title,
                    "content": "\n".join(current_content).strip(),
                })
            current_title = header_match.group(2).strip()
            current_content = [line]
        else:
            current_content.append(line)

    # Save last section
    if current_content:
        sections.append({
            "title": current_title,
            "content": "\n".join(current_content).strip(),
        })

    return sections


def _split_into_paragraphs(text: str) -> list[str]:
    """Split text by double newlines (paragraph boundaries)."""
    paragraphs = re.split(r"\n\s*\n", text)
    return [p.strip() for p in paragraphs if p.strip()]


def chunk_text(
    text: str,
    max_tokens: int = 500,
    overlap_tokens: int = 50,
    title: str = "",
    source: str = "",
    url: str = "",
    doc_id: str = "",
) -> list[Chunk]:
    """
    Split text into overlapping chunks.

    Strategy:
    1. First split by markdown headers into sections
    2. For each section, split by paragraphs
    3. Merge paragraphs into chunks respecting max_tokens
    4. Add overlap from previous chunk
    """
    all_chunks: list[Chunk] = []
    chunk_index = 0

    sections = _split_by_markdown_headers(text)

    for section in sections:
        section_title = section["title"] or title
        paragraphs = _split_into_paragraphs(section["content"])

        current_paras: list[str] = []
        current_token_count = 0
        prev_overlap_text = ""

        for para in paragraphs:
            para_tokens = _count_tokens_approx(para)

            # If a single paragraph exceeds max_tokens, split it by sentences
            if para_tokens > max_tokens:
                # Flush current buffer first
                if current_paras:
                    chunk_content = prev_overlap_text + "\n\n".join(current_paras)
                    all_chunks.append(Chunk(
                        content=chunk_content.strip(),
                        title=section_title,
                        source=source,
                        url=url,
                        chunk_index=chunk_index,
                        doc_id=doc_id,
                    ))
                    chunk_index += 1
                    # Build overlap from end of current chunk
                    words = chunk_content.split()
                    prev_overlap_text = " ".join(words[-overlap_tokens:]) + "\n\n" if len(words) > overlap_tokens else ""
                    current_paras = []
                    current_token_count = 0

                # Split long paragraph by sentences
                sentences = re.split(r"(?<=[.!?])\s+", para)
                sent_buffer: list[str] = []
                sent_token_count = 0
                for sent in sentences:
                    sent_tokens = _count_tokens_approx(sent)
                    if sent_token_count + sent_tokens > max_tokens and sent_buffer:
                        chunk_content = prev_overlap_text + " ".join(sent_buffer)
                        all_chunks.append(Chunk(
                            content=chunk_content.strip(),
                            title=section_title,
                            source=source,
                            url=url,
                            chunk_index=chunk_index,
                            doc_id=doc_id,
                        ))
                        chunk_index += 1
                        words = chunk_content.split()
                        prev_overlap_text = " ".join(words[-overlap_tokens:]) + " " if len(words) > overlap_tokens else ""
                        sent_buffer = []
                        sent_token_count = 0
                    sent_buffer.append(sent)
                    sent_token_count += sent_tokens

                if sent_buffer:
                    chunk_content = prev_overlap_text + " ".join(sent_buffer)
                    all_chunks.append(Chunk(
                        content=chunk_content.strip(),
                        title=section_title,
                        source=source,
                        url=url,
                        chunk_index=chunk_index,
                        doc_id=doc_id,
                    ))
                    chunk_index += 1
                    words = chunk_content.split()
                    prev_overlap_text = " ".join(words[-overlap_tokens:]) + "\n\n" if len(words) > overlap_tokens else ""
                continue

            # Normal case: accumulate paragraphs
            if current_token_count + para_tokens > max_tokens and current_paras:
                chunk_content = prev_overlap_text + "\n\n".join(current_paras)
                all_chunks.append(Chunk(
                    content=chunk_content.strip(),
                    title=section_title,
                    source=source,
                    url=url,
                    chunk_index=chunk_index,
                    doc_id=doc_id,
                ))
                chunk_index += 1
                words = chunk_content.split()
                prev_overlap_text = " ".join(words[-overlap_tokens:]) + "\n\n" if len(words) > overlap_tokens else ""
                current_paras = []
                current_token_count = 0

            current_paras.append(para)
            current_token_count += para_tokens

        # Flush remaining paragraphs
        if current_paras:
            chunk_content = prev_overlap_text + "\n\n".join(current_paras)
            all_chunks.append(Chunk(
                content=chunk_content.strip(),
                title=section_title,
                source=source,
                url=url,
                chunk_index=chunk_index,
                doc_id=doc_id,
            ))
            chunk_index += 1

    # Edge case: empty text
    if not all_chunks and text.strip():
        all_chunks.append(Chunk(
            content=text.strip(),
            title=title,
            source=source,
            url=url,
            chunk_index=0,
            doc_id=doc_id,
        ))

    return all_chunks
