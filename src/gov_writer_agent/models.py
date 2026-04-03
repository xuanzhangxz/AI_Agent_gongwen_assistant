from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class KnowledgeChunk:
    chunk_id: str
    source_path: Path
    source_type: str
    title: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RetrievedChunk:
    chunk: KnowledgeChunk
    score: float


@dataclass(slots=True)
class RewriteRequest:
    draft_path: Path
    draft_text: str
    doc_type: str | None = None
    audience: str | None = None
    goal: str | None = None
    notes: str | None = None


@dataclass(slots=True)
class ReviewIssue:
    severity: str
    issue_type: str
    description: str
    fix_hint: str


@dataclass(slots=True)
class RewriteResult:
    final_document: str
    first_pass_document: str
    review_summary: str
    review_passed: bool
    review_issues: list[ReviewIssue]
    retrieved_chunks: list[RetrievedChunk]
