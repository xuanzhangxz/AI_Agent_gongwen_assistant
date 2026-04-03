from __future__ import annotations

from gov_writer_agent.models import RetrievedChunk, RewriteRequest, ReviewIssue


SYSTEM_INSTRUCTIONS = """你是一个专门服务政务场景的“公文写作 Agent”。

你的任务不是自由发挥，而是把用户提供的粗稿，严格对齐已有规范、优秀案例和模板，产出一版可以提交领导审阅的正式公文。

必须遵守以下规则：
1. 规范文件优先级最高，案例文件次之，模板用于约束结构。
2. 不得编造数字、政策依据、会议结论、领导指示、完成时限或事实细节。
3. 信息不充分时，优先使用审慎、边界清晰的表述，必要时保留“待进一步核实”“拟于近期推进”等稳妥写法。
4. 语言风格必须正式、准确、克制、简洁，避免口号化、网络化、文学化表达。
5. 优先保证逻辑清晰、层次分明、措辞合规，再追求文采。
"""


def build_query(request: RewriteRequest) -> str:
    parts = [
        request.doc_type or "",
        request.audience or "",
        request.goal or "",
        request.notes or "",
        request.draft_text,
    ]
    return "\n".join(part for part in parts if part.strip())


def format_context(label: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return f"【{label}】\n无"

    lines = [f"【{label}】"]
    for item in chunks:
        metadata = item.chunk.metadata
        doc_type = metadata.get("doc_type", "")
        audience = metadata.get("audience", "")
        lines.append(
            "\n".join(
                [
                    f"来源标题：{item.chunk.title}",
                    f"来源路径：{item.chunk.source_path}",
                    f"文种：{doc_type or '未标注'}",
                    f"受众：{audience or '未标注'}",
                    f"相关度：{item.score:.2f}",
                    "片段内容：",
                    item.chunk.text,
                ]
            )
        )
    return "\n\n".join(lines)


def build_rewrite_prompt(
    request: RewriteRequest,
    standards: list[RetrievedChunk],
    templates: list[RetrievedChunk],
    exemplars: list[RetrievedChunk],
) -> str:
    return f"""请根据以下资料，将粗稿改写成正式公文。

【任务信息】
文种：{request.doc_type or "未指定，请自行判断最稳妥的汇报文种"}
受众：{request.audience or "局领导或类似行政管理受众"}
目标：{request.goal or "输出一版可直接审阅的正式稿"}
补充说明：{request.notes or "无"}

{format_context("规范要求", standards)}

{format_context("文种模板", templates)}

{format_context("优秀案例", exemplars)}

【用户粗稿】
{request.draft_text}

【输出要求】
1. 只输出最终公文正文，不要解释说明，不要添加代码块。
2. 若粗稿没有正式标题，请补出一个规范标题。
3. 若内容适合分层级表达，请使用“一、（一）1.”等公文常见结构。
4. 尽量保留原稿真实意图和事实边界，不擅自新增未提供的具体事实。
5. 如果关键信息缺失，不要乱补，可以用审慎表述过渡。
"""


def build_review_prompt(
    request: RewriteRequest,
    polished_document: str,
    standards: list[RetrievedChunk],
    templates: list[RetrievedChunk],
) -> str:
    return f"""请从“格式是否合规、逻辑是否顺畅、措辞是否正式、信息是否稳妥”四个维度，对下面成稿做一次严格复审。

{format_context("复审依据-规范要求", standards)}

{format_context("复审依据-文种模板", templates)}

【任务信息】
文种：{request.doc_type or "未指定"}
受众：{request.audience or "未指定"}
目标：{request.goal or "未指定"}

【待复审成稿】
{polished_document}

请只返回严格 JSON，不要附加任何解释，不要使用 Markdown 代码块。格式如下：
{{
  "pass": true,
  "summary": "一句话总结复审结论",
  "issues": [
    {{
      "severity": "high|medium|low",
      "issue_type": "格式|逻辑|措辞|事实风险",
      "description": "问题描述",
      "fix_hint": "修订建议"
    }}
  ]
}}
"""


def build_revision_prompt(
    request: RewriteRequest,
    first_pass_document: str,
    review_issues: list[ReviewIssue],
    standards: list[RetrievedChunk],
    templates: list[RetrievedChunk],
    exemplars: list[RetrievedChunk],
) -> str:
    issue_lines = []
    for issue in review_issues:
        issue_lines.append(
            f"- 严重程度：{issue.severity}；类型：{issue.issue_type}；问题：{issue.description}；建议：{issue.fix_hint}"
        )
    issue_text = "\n".join(issue_lines) if issue_lines else "- 无"

    return f"""请根据复审意见，对以下公文进行最终修订。

【任务信息】
文种：{request.doc_type or "未指定"}
受众：{request.audience or "未指定"}
目标：{request.goal or "输出一版可直接审阅的正式稿"}
补充说明：{request.notes or "无"}

{format_context("规范要求", standards)}

{format_context("文种模板", templates)}

{format_context("优秀案例", exemplars)}

【首轮成稿】
{first_pass_document}

【复审问题】
{issue_text}

【输出要求】
1. 只输出最终修订后的公文正文。
2. 必须逐项吸收复审问题，但不得编造事实。
3. 保持整体正式、克制、逻辑清晰。
"""
