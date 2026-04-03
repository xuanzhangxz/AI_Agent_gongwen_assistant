from __future__ import annotations

from pathlib import Path

from gov_writer_agent.config import Settings
from gov_writer_agent.loaders import load_knowledge_chunks
from gov_writer_agent.models import ReviewIssue, RewriteRequest, RewriteResult
from gov_writer_agent.openai_client import OpenAIResponsesClient
from gov_writer_agent.prompts import (
    SYSTEM_INSTRUCTIONS,
    build_query,
    build_review_prompt,
    build_rewrite_prompt,
    build_revision_prompt,
)
from gov_writer_agent.retrieval import KnowledgeRetriever


class GovWriterAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAIResponsesClient(settings) if settings.api_key else None
        self.knowledge_chunks = load_knowledge_chunks(
            settings.knowledge_dir, max_chars_per_chunk=settings.max_chars_per_chunk
        )
        if not self.knowledge_chunks:
            raise ValueError(
                f"No knowledge files were found in {settings.knowledge_dir}. "
                "Please add standards, exemplars, or templates first."
            )
        self.retriever = KnowledgeRetriever(self.knowledge_chunks)

    def rewrite(self, request: RewriteRequest) -> RewriteResult:
        if self.client is None:
            raise ValueError("OPENAI_API_KEY is required for rewrite.")

        query = build_query(request)
        standards = self.retriever.retrieve(
            query,
            limit=4,
            source_type="standards",
            doc_type=request.doc_type,
            audience=request.audience,
        )
        templates = self.retriever.retrieve(
            query,
            limit=2,
            source_type="templates",
            doc_type=request.doc_type,
            audience=request.audience,
        )
        exemplars = self.retriever.retrieve(
            query,
            limit=4,
            source_type="exemplars",
            doc_type=request.doc_type,
            audience=request.audience,
        )

        first_pass = self.client.generate_text(
            instructions=SYSTEM_INSTRUCTIONS,
            prompt=build_rewrite_prompt(request, standards, templates, exemplars),
            max_output_tokens=4000,
        )

        review_raw = self.client.generate_json(
            instructions=SYSTEM_INSTRUCTIONS,
            prompt=build_review_prompt(request, first_pass, standards, templates),
            max_output_tokens=1500,
        )
        issues = self._parse_issues(review_raw.get("issues", []))
        review_passed = bool(review_raw.get("pass", False)) and not any(
            issue.severity == "high" for issue in issues
        )
        review_summary = str(review_raw.get("summary", "未返回复审结论"))

        if review_passed:
            final_document = first_pass
        else:
            final_document = self.client.generate_text(
                instructions=SYSTEM_INSTRUCTIONS,
                prompt=build_revision_prompt(
                    request=request,
                    first_pass_document=first_pass,
                    review_issues=issues,
                    standards=standards,
                    templates=templates,
                    exemplars=exemplars,
                ),
                max_output_tokens=4000,
            )

        return RewriteResult(
            final_document=final_document.strip(),
            first_pass_document=first_pass.strip(),
            review_summary=review_summary,
            review_passed=review_passed,
            review_issues=issues,
            retrieved_chunks=standards + templates + exemplars,
        )

    def list_knowledge(self) -> list[tuple[str, Path, str]]:
        seen: set[Path] = set()
        items: list[tuple[str, Path, str]] = []
        for chunk in self.knowledge_chunks:
            if chunk.source_path in seen:
                continue
            seen.add(chunk.source_path)
            items.append((chunk.source_type, chunk.source_path, chunk.title))
        return items

    @staticmethod
    def _parse_issues(raw_items: object) -> list[ReviewIssue]:
        issues: list[ReviewIssue] = []
        if not isinstance(raw_items, list):
            return issues

        for item in raw_items:
            if not isinstance(item, dict):
                continue
            issues.append(
                ReviewIssue(
                    severity=str(item.get("severity", "medium")),
                    issue_type=str(item.get("issue_type", "未知")),
                    description=str(item.get("description", "")).strip(),
                    fix_hint=str(item.get("fix_hint", "")).strip(),
                )
            )
        return issues


def read_draft(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()
