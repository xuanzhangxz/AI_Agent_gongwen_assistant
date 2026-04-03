# 公文写作 Agent Starter

这是一个从 0 到 1 的起步版项目，目标是把你的两类核心资产沉淀为可调用的知识库：

1. 公文写作标准、格式规范、禁忌要求。
2. 领导认可的优秀历史公文案例。

你后续只需要提供一份粗稿，Agent 就会先检索最相关的规范和案例，再调用大模型完成两轮处理：

1. 依据规范与案例进行正式改写。
2. 依据检查清单进行合规复审，必要时自动二次修订。

当前版本的特点：

- 支持直接读取 `.md`、`.txt`、`.docx` 资料。
- 针对中文做了轻量检索，适合“工作进展汇报”等公文场景。
- 默认走 OpenAI `Responses API`，便于后续继续扩展为工具型 Agent。
- 输出既可以是提交版公文，也可以附带一份内部校核报告。

## 目录结构

```text
.
├── drafts/                     # 你的待润色粗稿
├── knowledge/
│   ├── standards/             # 公文规范、写作标准、禁忌
│   ├── exemplars/             # 优秀案例
│   ├── templates/             # 常用文种模板
│   └── README.md              # 资料整理说明
├── outputs/                   # 成稿与校核报告
├── src/gov_writer_agent/      # 核心代码
└── tests/                     # 基础单测
```

## 快速开始

1. 安装本项目

```bash
python3 -m pip install -e .
```

2. 配置环境变量

   把 [`.env.example`](/Users/zhangxuan/AI_Agent/.env.example) 复制为 `.env`，填入你的 `OPENAI_API_KEY`。

3. 准备资料

   把你的规范文件放入 [knowledge/standards](/Users/zhangxuan/AI_Agent/knowledge/standards)。
   把高质量案例放入 [knowledge/exemplars](/Users/zhangxuan/AI_Agent/knowledge/exemplars)。
   把固定模板放入 [knowledge/templates](/Users/zhangxuan/AI_Agent/knowledge/templates)。

4. 准备初稿

   参考 [drafts/sample_draft.md](/Users/zhangxuan/AI_Agent/drafts/sample_draft.md) 的形式放入待处理草稿。

5. 执行改写

```bash
gov-writer-agent @rewrite \
  --draft drafts/sample_draft.md \
  --output outputs/final_report.md \
  --report outputs/final_report.review.md \
  --doc-type 工作进展汇报 \
  --audience 局领导 \
  --goal 提交一版可直接审阅的正式汇报稿
```

6. 查看知识库加载情况

```bash
gov-writer-agent @list-knowledge
```

如果你更喜欢“先 @ Agent，再下命令”的风格，也支持：

```bash
gov-writer-agent @公文助手 rewrite --draft drafts/sample_draft.md --output outputs/final_report.md
gov-writer-agent @公文助手 list-knowledge
```

也兼容原始命令写法：

```bash
gov-writer-agent rewrite --draft drafts/sample_draft.md --output outputs/final_report.md
gov-writer-agent list-knowledge
```

## 推荐资料整理方式

建议每份资料都放一个简短头部，便于后续精确召回：

```yaml
---
title: 关于重点项目推进情况的汇报
doc_type: 工作进展汇报
audience: 局领导
tags: 项目推进, 重点工作, 风险问题
---
```

头部不是必填；没有头部也可以用。

## 当前工作流

### 1. 知识沉淀

- 标准规范优先级最高，用于约束格式、逻辑、语气和禁忌。
- 模板用于约束文种结构。
- 优秀案例用于学习措辞、段落组织和汇报节奏。

### 2. 检索召回

- 系统会从草稿、文种、受众、目标中提取查询线索。
- 针对中文做分词近似和双字切分，提高召回效果。
- 会对 `standards`、`templates`、`exemplars` 分别取高相关片段。

### 3. 两轮生成

- 第一轮：把粗稿改写为正式公文。
- 第二轮：按检查清单复审，不达标就自动修订。

### 4. 输出控制

- `--output` 输出提交版公文。
- `--report` 输出内部校核报告，便于你和同事快速看修改依据。

## 下一步最值得做的增强

如果你确认这个方向对，可以继续叠加三层能力：

1. 把“不同文种”拆成独立模板，例如请示、汇报、方案、总结。
2. 对优秀案例做标签化，例如“领导偏好用语”“问题风险表述”“下一步工作写法”。
3. 引入评测集，对 Agent 的输出做自动打分，持续优化提示词和资料组织。

## 注意事项

- 当前版本不会凭空编造数据、会议纪要或领导指示；信息不全时会优先使用审慎表述。
- `.pdf` 暂未内建解析，建议先转成 `.docx`、`.md` 或 `.txt` 再放入知识库。
- 若你后续要做成网页工具或企业内部服务，这个 starter 可以直接作为后端核心流程继续扩展。
- `@公文助手` 和 `@rewrite` 这种是本地包装调用，目的是提供接近 at mention 的使用体验；它不会注册为 Codex CLI 内建的原生 `@...` 语法。
