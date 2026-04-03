from __future__ import annotations

import argparse
from pathlib import Path
import sys

from gov_writer_agent.config import Settings
from gov_writer_agent.models import RewriteRequest
from gov_writer_agent.pipeline import GovWriterAgent, read_draft

AT_AGENT_ALIASES = {
    "@公文助手",
    "@gov-writer",
    "@govwriter",
}

AT_COMMAND_ALIASES = {
    "@rewrite": "rewrite",
    "@list-knowledge": "list-knowledge",
    "@help": "help",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gov writer agent starter",
        epilog=(
            "Examples:\n"
            "  gov-writer-agent @list-knowledge\n"
            "  gov-writer-agent @公文助手 list-knowledge\n"
            "  gov-writer-agent @rewrite --draft drafts/sample_draft.md --output outputs/final_report.md\n"
            "  gov-writer-agent @公文助手 rewrite --draft drafts/sample_draft.md --output outputs/final_report.md\n"
            "  gov-writer-agent rewrite --draft drafts/sample_draft.md --output outputs/final_report.md"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    rewrite_parser = subparsers.add_parser("rewrite", help="Polish a rough draft")
    rewrite_parser.add_argument("--draft", required=True, help="Path to the rough draft")
    rewrite_parser.add_argument("--output", required=True, help="Path to save the final document")
    rewrite_parser.add_argument("--report", help="Optional path to save the review report")
    rewrite_parser.add_argument("--doc-type", help="Document type, e.g. 工作进展汇报")
    rewrite_parser.add_argument("--audience", help="Target audience, e.g. 局领导")
    rewrite_parser.add_argument("--goal", help="Writing goal or delivery target")
    rewrite_parser.add_argument("--notes", help="Additional notes or constraints")

    subparsers.add_parser("list-knowledge", help="List loaded knowledge files")
    return parser


def normalize_argv(argv: list[str]) -> list[str]:
    if not argv:
        return argv

    first = argv[0]
    if first in AT_AGENT_ALIASES:
        if len(argv) == 1:
            return ["help"]

        second = argv[1]
        if second in AT_COMMAND_ALIASES:
            return [AT_COMMAND_ALIASES[second], *argv[2:]]
        return argv[1:]

    if first in AT_COMMAND_ALIASES:
        return [AT_COMMAND_ALIASES[first], *argv[1:]]

    return argv


def write_report(report_path: Path, result, request: RewriteRequest) -> None:
    lines = [
        "# 公文写作校核报告",
        "",
        f"- 草稿路径：{request.draft_path}",
        f"- 文种：{request.doc_type or '未指定'}",
        f"- 受众：{request.audience or '未指定'}",
        f"- 目标：{request.goal or '未指定'}",
        f"- 复审结论：{'通过' if result.review_passed else '需进一步关注'}",
        f"- 复审摘要：{result.review_summary}",
        "",
        "## 复审问题",
    ]

    if result.review_issues:
        for issue in result.review_issues:
            lines.append(
                f"- [{issue.severity}] {issue.issue_type}：{issue.description}；建议：{issue.fix_hint}"
            )
    else:
        lines.append("- 无明显问题")

    lines.extend(["", "## 检索到的依据片段"])
    for item in result.retrieved_chunks:
        lines.extend(
            [
                f"- 类型：{item.chunk.source_type}",
                f"  标题：{item.chunk.title}",
                f"  路径：{item.chunk.source_path}",
                f"  相关度：{item.score:.2f}",
            ]
        )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def command_rewrite(args: argparse.Namespace) -> int:
    settings = Settings.from_env(Path.cwd(), require_api_key=True)
    agent = GovWriterAgent(settings)

    draft_path = Path(args.draft)
    output_path = Path(args.output)
    draft_text = read_draft(draft_path)
    request = RewriteRequest(
        draft_path=draft_path,
        draft_text=draft_text,
        doc_type=args.doc_type,
        audience=args.audience,
        goal=args.goal,
        notes=args.notes,
    )

    result = agent.rewrite(request)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.final_document + "\n", encoding="utf-8")

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        write_report(report_path, result, request)

    print(f"Final document saved to: {output_path}")
    if args.report:
        print(f"Review report saved to: {args.report}")
    return 0


def command_list_knowledge() -> int:
    settings = Settings.from_env(Path.cwd(), require_api_key=False)
    agent = GovWriterAgent(settings)
    for source_type, source_path, title in agent.list_knowledge():
        print(f"[{source_type}] {title} -> {source_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    normalized_argv = normalize_argv(raw_argv)

    if normalized_argv and normalized_argv[0] == "help":
        parser.print_help()
        return 0

    args = parser.parse_args(normalized_argv)

    if args.command == "rewrite":
        return command_rewrite(args)
    if args.command == "list-knowledge":
        return command_list_knowledge()
    raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
