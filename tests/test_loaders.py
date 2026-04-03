from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from gov_writer_agent.loaders import load_knowledge_chunks, parse_front_matter, split_into_chunks


class LoaderTests(unittest.TestCase):
    def test_parse_front_matter(self) -> None:
        text = """---
title: 示例标题
doc_type: 工作进展汇报
tags: 进展, 汇报
---

正文内容
"""
        metadata, body = parse_front_matter(text)
        self.assertEqual(metadata["title"], "示例标题")
        self.assertEqual(metadata["doc_type"], "工作进展汇报")
        self.assertEqual(metadata["tags"], ["进展", "汇报"])
        self.assertEqual(body, "正文内容")

    def test_split_into_chunks(self) -> None:
        text = "第一段\n\n第二段\n\n第三段"
        chunks = split_into_chunks(text, max_chars=5)
        self.assertGreaterEqual(len(chunks), 2)

    def test_load_knowledge_chunks(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            standards = root / "standards"
            standards.mkdir(parents=True)
            (standards / "sample.md").write_text(
                "---\ntitle: 样例\n---\n\n这是一个用于测试的规范文件。",
                encoding="utf-8",
            )

            chunks = load_knowledge_chunks(root, max_chars_per_chunk=20)
            self.assertEqual(len(chunks), 1)
            self.assertEqual(chunks[0].source_type, "standards")


if __name__ == "__main__":
    unittest.main()
