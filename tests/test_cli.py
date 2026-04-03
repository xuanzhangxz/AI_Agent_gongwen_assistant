import unittest

from gov_writer_agent.cli import normalize_argv


class CliTests(unittest.TestCase):
    def test_normalize_at_rewrite(self) -> None:
        self.assertEqual(
            normalize_argv(["@rewrite", "--draft", "a.md"]),
            ["rewrite", "--draft", "a.md"],
        )

    def test_normalize_agent_then_rewrite(self) -> None:
        self.assertEqual(
            normalize_argv(["@公文助手", "rewrite", "--draft", "a.md"]),
            ["rewrite", "--draft", "a.md"],
        )

    def test_normalize_agent_then_at_command(self) -> None:
        self.assertEqual(
            normalize_argv(["@公文助手", "@list-knowledge"]),
            ["list-knowledge"],
        )

    def test_normalize_regular_command(self) -> None:
        self.assertEqual(
            normalize_argv(["rewrite", "--draft", "a.md"]),
            ["rewrite", "--draft", "a.md"],
        )


if __name__ == "__main__":
    unittest.main()
