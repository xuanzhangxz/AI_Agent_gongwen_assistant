from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(slots=True)
class Settings:
    api_key: str
    base_url: str
    model: str
    reasoning_effort: str
    knowledge_dir: Path
    max_chars_per_chunk: int = 900

    @classmethod
    def from_env(cls, cwd: Path | None = None, *, require_api_key: bool = False) -> "Settings":
        current = cwd or Path.cwd()
        load_dotenv(current / ".env")

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if require_api_key and not api_key:
            raise ValueError("Missing OPENAI_API_KEY. Please create a .env file first.")

        knowledge_dir = Path(
            os.getenv("GOV_WRITER_KNOWLEDGE_DIR", current / "knowledge")
        )
        if not knowledge_dir.is_absolute():
            knowledge_dir = current / knowledge_dir

        return cls(
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/"),
            model=os.getenv("OPENAI_MODEL", "gpt-5.4"),
            reasoning_effort=os.getenv("OPENAI_REASONING_EFFORT", "medium"),
            knowledge_dir=knowledge_dir,
            max_chars_per_chunk=int(os.getenv("GOV_WRITER_MAX_CHARS_PER_CHUNK", "900")),
        )
