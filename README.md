# 公文写作 Agent

## 项目简介

公文写作 Agent 是一个面向政务办公场景的智能写作辅助项目，目标是将“公文写作规范”“历史优秀案例”“固定模板”沉淀为可调用知识库，并基于大模型能力，对业务人员提交的粗稿进行规范化改写、结构优化和合规复审。

本项目适用于以下场景：

- 向局领导报送工作进展汇报、专题汇报、阶段性总结等材料。
- 对已有初稿进行正式化、规范化润色。
- 对公文写作标准进行沉淀与复用，降低人工反复修改成本。

## 建设目标

- 将分散的写作标准、领导偏好和优秀案例形成统一知识底座。
- 建立“粗稿输入、自动改写、自动复审、成稿输出”的标准化工作流。
- 在不编造事实的前提下，提高公文初稿质量与出稿效率。
- 为后续建设网页工具、内部服务或企业办公集成接口提供基础能力。

## 核心能力

- 支持加载 `.md`、`.txt`、`.docx` 三类资料文件。
- 支持按“规范、模板、案例”三类知识进行检索召回。
- 支持基于中文语料的轻量检索与片段相关性排序。
- 支持公文首轮改写、合规复审与必要时二次修订。
- 支持输出正式成稿与内部校核报告。
- 支持命令行原生命令和本地 `@` 风格调用。

## 工作机制

系统默认采用以下处理流程：

1. 读取用户提供的粗稿、文种、受众和目标信息。
2. 从知识库中分别召回相关规范、模板和优秀案例片段。
3. 依据“规范优先、模板约束、案例参考”的原则生成首轮成稿。
4. 对首轮成稿执行合规复审，重点检查格式、逻辑、措辞和事实风险。
5. 如复审未通过，则基于问题清单执行二次修订。
6. 输出正式稿，并可选输出校核报告。

## 快速开始

### 1. 安装项目

```bash
python3 -m pip install -e .
```

### 2. 配置环境变量

将 [`.env.example`](/Users/zhangxuan/AI_Agent/.env.example) 复制为 `.env`，并至少配置以下参数：

```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-5.4
OPENAI_REASONING_EFFORT=medium
```

### 3. 准备知识库资料

- 将公文规范、写作要求、禁忌要求放入 [knowledge/standards](/Users/zhangxuan/AI_Agent/knowledge/standards)
- 将优秀历史案例放入 [knowledge/exemplars](/Users/zhangxuan/AI_Agent/knowledge/exemplars)
- 将文种模板放入 [knowledge/templates](/Users/zhangxuan/AI_Agent/knowledge/templates)

资料整理要求见 [knowledge/README.md](/Users/zhangxuan/AI_Agent/knowledge/README.md)。

### 4. 执行命令

查看知识库：

```bash
gov-writer-agent @list-knowledge
```

执行改写：

```bash
gov-writer-agent @rewrite \
  --draft drafts/sample_draft.md \
  --output outputs/final_report.md \
  --report outputs/final_report.review.md \
  --doc-type 工作进展汇报 \
  --audience 局领导 \
  --goal 提交一版可直接审阅的正式汇报稿
```

也支持以下写法：

```bash
gov-writer-agent @公文助手 rewrite --draft drafts/sample_draft.md --output outputs/final_report.md
gov-writer-agent rewrite --draft drafts/sample_draft.md --output outputs/final_report.md
```

## 目录结构

```text
.
├── drafts/                     # 待处理粗稿
├── knowledge/
│   ├── standards/             # 写作规范、格式要求、禁忌清单
│   ├── exemplars/             # 优秀案例
│   ├── templates/             # 文种模板
│   └── README.md              # 知识库整理说明
├── outputs/                   # 成稿与复审报告
├── src/gov_writer_agent/      # 核心实现
└── tests/                     # 测试用例
```

## 文档导航

- 项目说明：[docs/PROJECT_OVERVIEW.md](/Users/zhangxuan/AI_Agent/docs/PROJECT_OVERVIEW.md)
- 使用说明：[docs/USER_GUIDE.md](/Users/zhangxuan/AI_Agent/docs/USER_GUIDE.md)
- 知识库整理说明：[knowledge/README.md](/Users/zhangxuan/AI_Agent/knowledge/README.md)

## 当前边界

- 当前版本不会擅自补造数据、领导指示、会议结论或政策依据。
- 对信息不充分的场景，系统优先采用审慎表述，而非虚构细节。
- 当前未内建 `.pdf` 解析，建议先转换为 `.docx`、`.md` 或 `.txt`。
- `@公文助手` 和 `@rewrite` 属于本地包装调用，不是 Codex CLI 原生内建语法。

## 后续建议

如需继续工程化，建议优先补充以下能力：

- 按文种拆分模板体系，例如请示、方案、总结、专报。
- 对优秀案例增加标签，例如场景、风格、受众、常用句式。
- 建设评测集，对输出稿件的规范性与可用性做持续评估。
- 对接网页端、办公机器人或内部服务接口。
