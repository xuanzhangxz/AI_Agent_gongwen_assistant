import unittest
from pathlib import Path

from gov_writer_agent.models import KnowledgeChunk
from gov_writer_agent.retrieval import KnowledgeRetriever, tokenize_mixed


class RetrievalTests(unittest.TestCase):
    def test_tokenize_mixed_handles_chinese(self) -> None:
        tokens = tokenize_mixed("工作进展汇报")
        self.assertIn("工", tokens)
        self.assertIn("工作", tokens)
        self.assertIn("进展", tokens)

    def test_retriever_prefers_relevant_standard(self) -> None:
        chunks = [
            KnowledgeChunk(
                chunk_id="1",
                source_path=Path("knowledge/standards/a.md"),
                source_type="standards",
                title="工作进展汇报规范",
                text="工作进展汇报应包含主要进展、存在问题和下一步工作。",
            ),
            KnowledgeChunk(
                chunk_id="2",
                source_path=Path("knowledge/exemplars/b.md"),
                source_type="exemplars",
                title="会议通知",
                text="请各单位按时参加会议。",
            ),
        ]
        retriever = KnowledgeRetriever(chunks)
        results = retriever.retrieve("请改写一份工作进展汇报", limit=1)
        self.assertEqual(results[0].chunk.chunk_id, "1")


if __name__ == "__main__":
    unittest.main()
