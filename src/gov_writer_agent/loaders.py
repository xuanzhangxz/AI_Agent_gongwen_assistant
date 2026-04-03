from __future__ import annotations

import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from gov_writer_agent.models import KnowledgeChunk

SUPPORTED_SUFFIXES = {".md", ".txt", ".docx"}
SUPPORTED_SOURCE_TYPES = {"standards", "exemplars", "templates"}
WORD_NAMESPACE = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def parse_front_matter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text.strip()

    marker = "\n---\n"
    end_index = text.find(marker, 4)
    if end_index == -1:
        return {}, text.strip()

    raw_header = text[4:end_index]
    body = text[end_index + len(marker) :].strip()
    metadata: dict[str, object] = {}

    for raw_line in raw_header.splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed = value.strip()
        if "," in parsed:
            metadata[key.strip()] = [item.strip() for item in parsed.split(",") if item.strip()]
        else:
            metadata[key.strip()] = parsed

    return metadata, body


def read_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return read_docx(path)
    return path.read_text(encoding="utf-8")


def read_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml_content = archive.read("word/document.xml")

    root = ElementTree.fromstring(xml_content)
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", WORD_NAMESPACE):
        text_bits = [node.text for node in paragraph.findall(".//w:t", WORD_NAMESPACE) if node.text]
        merged = "".join(text_bits).strip()
        if merged:
            paragraphs.append(merged)
    return "\n\n".join(paragraphs)


def split_into_chunks(text: str, max_chars: int) -> list[str]:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    if not blocks:
        return []

    chunks: list[str] = []
    buffer = ""

    for block in blocks:
        candidate = block if not buffer else f"{buffer}\n\n{block}"
        if len(candidate) <= max_chars:
            buffer = candidate
            continue

        if buffer:
            chunks.append(buffer.strip())
        if len(block) <= max_chars:
            buffer = block
            continue

        cursor = 0
        while cursor < len(block):
            part = block[cursor : cursor + max_chars]
            chunks.append(part.strip())
            cursor += max_chars
        buffer = ""

    if buffer:
        chunks.append(buffer.strip())

    return chunks


def infer_source_type(path: Path, root: Path) -> str:
    relative = path.relative_to(root)
    if relative.parts:
        return relative.parts[0]
    return "unknown"


def load_knowledge_chunks(root: Path, max_chars_per_chunk: int = 900) -> list[KnowledgeChunk]:
    if not root.exists():
        return []

    chunks: list[KnowledgeChunk] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue

        raw_text = read_document(path)
        metadata, body = parse_front_matter(raw_text)
        title = str(metadata.get("title") or path.stem)
        source_type = infer_source_type(path, root)
        if source_type not in SUPPORTED_SOURCE_TYPES:
            continue

        for index, chunk_text in enumerate(split_into_chunks(body, max_chars=max_chars_per_chunk), start=1):
            chunks.append(
                KnowledgeChunk(
                    chunk_id=f"{path.stem}-{index}",
                    source_path=path,
                    source_type=source_type,
                    title=title,
                    text=chunk_text,
                    metadata=metadata.copy(),
                )
            )

    return chunks
