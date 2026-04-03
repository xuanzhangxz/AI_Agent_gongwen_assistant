# 使用说明

## 一、环境要求

- Python 3.11 及以上版本
- 可用的 OpenAI API Key
- 可访问模型接口的网络环境

## 二、安装步骤

在项目根目录执行：

```bash
python3 -m pip install -e .
```

安装完成后，可使用 `gov-writer-agent` 命令调用本项目。

## 三、配置说明

在项目根目录创建 `.env` 文件，参考 [`.env.example`](/Users/zhangxuan/AI_Agent/.env.example) 配置以下参数：

```env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-5.4
OPENAI_REASONING_EFFORT=medium
GOV_WRITER_KNOWLEDGE_DIR=knowledge
GOV_WRITER_MAX_CHARS_PER_CHUNK=900
```

参数说明如下：

- `OPENAI_API_KEY`：模型调用密钥。
- `OPENAI_BASE_URL`：模型接口地址，默认 OpenAI 官方地址。
- `OPENAI_MODEL`：调用模型名称。
- `OPENAI_REASONING_EFFORT`：推理强度，通常可选 `low`、`medium`、`high`。
- `GOV_WRITER_KNOWLEDGE_DIR`：知识库目录。
- `GOV_WRITER_MAX_CHARS_PER_CHUNK`：知识切片最大字符数。

## 四、知识库准备

### 1. 目录要求

知识库默认使用以下目录：

- [knowledge/standards](/Users/zhangxuan/AI_Agent/knowledge/standards)
- [knowledge/exemplars](/Users/zhangxuan/AI_Agent/knowledge/exemplars)
- [knowledge/templates](/Users/zhangxuan/AI_Agent/knowledge/templates)

### 2. 文件格式

支持以下文件格式：

- `.md`
- `.txt`
- `.docx`

### 3. 推荐文件头

建议为资料文件增加头部信息，以提高召回准确度：

```yaml
---
title: 关于重点项目推进情况的汇报
doc_type: 工作进展汇报
audience: 局领导
tags: 项目推进, 风险问题, 下一步工作
---
```

### 4. 整理建议

- 规范文件尽量明确“必须遵守的规则”和“常见错误示例”。
- 模板文件尽量体现标准结构。
- 优秀案例尽量选用已被领导认可的正式成稿。
- 同一份文件只承载一种角色，避免把规范和案例混在一起。

## 五、使用方式

### 1. 查看知识库

```bash
gov-writer-agent @list-knowledge
```

也支持：

```bash
gov-writer-agent list-knowledge
gov-writer-agent @公文助手 list-knowledge
```

### 2. 执行改写

```bash
gov-writer-agent @rewrite \
  --draft drafts/sample_draft.md \
  --output outputs/final_report.md \
  --report outputs/final_report.review.md \
  --doc-type 工作进展汇报 \
  --audience 局领导 \
  --goal 提交一版可直接审阅的正式汇报稿
```

### 3. 参数说明

- `--draft`：待处理粗稿路径。
- `--output`：正式成稿输出路径。
- `--report`：复审报告输出路径，可选。
- `--doc-type`：文种名称，例如“工作进展汇报”。
- `--audience`：目标受众，例如“局领导”。
- `--goal`：写作目标，例如“形成正式报送稿”。
- `--notes`：附加说明，例如“注意问题部分要客观审慎”。

### 4. 示例输入

可参考 [drafts/sample_draft.md](/Users/zhangxuan/AI_Agent/drafts/sample_draft.md)。

### 5. 输出结果

系统可输出两类结果：

- 正式稿：保存到 `--output` 指定路径。
- 校核报告：保存到 `--report` 指定路径。

校核报告中会包含：

- 草稿信息
- 复审结论
- 问题摘要
- 检索依据片段

## 六、推荐操作流程

建议按以下流程使用：

1. 先整理规范、模板和优秀案例。
2. 先运行一次 `@list-knowledge`，确认资料已正确加载。
3. 再提交粗稿并执行 `@rewrite`。
4. 查看成稿和复审报告，确认是否需要人工补充事实信息。
5. 将高质量成稿继续回灌为优秀案例，持续优化知识库。

## 七、常见问题

### 1. 为什么模型没有补足具体数据？

当前版本默认遵循“不得编造事实”的约束，因此不会主动补造数据、会议结论或领导指示。

### 2. 为什么某些资料没有被正确命中？

可能原因包括：

- 资料放错目录
- 文件格式不受支持
- 文件头缺少文种、受众等关键信息
- 资料内容与当前草稿场景差异较大

### 3. 是否支持 PDF？

当前版本暂不内建 PDF 解析，建议先转换为 `.docx`、`.md` 或 `.txt`。

### 4. `@公文助手` 是不是 Codex CLI 原生命令？

不是。当前的 `@` 写法是本项目命令行对参数做的本地兼容包装，目的是让调用方式更贴近日常使用习惯。

## 八、维护建议

- 定期更新规范文件和优秀案例。
- 对不同领导、不同场景建立独立标签或独立子目录。
- 对经常修改的表述单独整理成“高频用语规范”。
- 在正式报送前保留人工复核环节。
