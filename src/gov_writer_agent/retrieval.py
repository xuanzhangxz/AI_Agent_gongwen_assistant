from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from gov_writer_agent.models import KnowledgeChunk, RetrievedChunk

ASCII_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")
CHINESE_CHAR_RE = re.compile(r"[\u4e00-\u9fff]")


def tokenize_mixed(text: str) -> list[str]:
    ascii_tokens = [match.group(0).lower() for match in ASCII_TOKEN_RE.finditer(text)]
    chinese_chars = [char for char in text if CHINESE_CHAR_RE.fullmatch(char)]

    tokens = list(ascii_tokens)
    tokens.extend(chinese_chars)
    tokens.extend(
        "".join(chinese_chars[index : index + 2])
        for index in range(len(chinese_chars) - 1)
    )
    return tokens


@dataclass(slots=True)
class IndexedChunk:
    chunk: KnowledgeChunk
    term_freq: Counter[str]
    length: int


class KnowledgeRetriever:
    def __init__(self, chunks: list[KnowledgeChunk]) -> None:
        self.chunks = chunks
        self.indexed_chunks: list[IndexedChunk] = []
        self.doc_freq: Counter[str] = Counter()

        for chunk in chunks:
            tokens = tokenize_mixed(chunk.text)
            term_freq = Counter(tokens)
            self.indexed_chunks.append(
                IndexedChunk(chunk=chunk, term_freq=term_freq, length=max(len(tokens), 1))
            )
            self.doc_freq.update(term_freq.keys())

        self.avg_doc_len = (
            sum(item.length for item in self.indexed_chunks) / len(self.indexed_chunks)
            if self.indexed_chunks
            else 1.0
        )

    def idf(self, token: str) -> float:
        doc_count = len(self.indexed_chunks)
        frequency = self.doc_freq.get(token, 0)
        return math.log(1 + (doc_count - frequency + 0.5) / (frequency + 0.5))

    def score(
        self,
        indexed_chunk: IndexedChunk,
        query_tokens: list[str],
        doc_type: str | None = None,
        audience: str | None = None,
    ) -> float:
        if not query_tokens:
            return 0.0

        k1 = 1.5
        b = 0.75
        score = 0.0

        for token in query_tokens:
            frequency = indexed_chunk.term_freq.get(token)
            if not frequency:
                continue
            numerator = frequency * (k1 + 1)
            denominator = frequency + k1 * (
                1 - b + b * indexed_chunk.length / self.avg_doc_len
            )
            score += self.idf(token) * numerator / denominator

        source_type = indexed_chunk.chunk.source_type
        if source_type == "standards":
            score *= 1.25
        elif source_type == "templates":
            score *= 1.15

        metadata_blob = " ".join(
            [indexed_chunk.chunk.title]
            + [str(value) for value in indexed_chunk.chunk.metadata.values()]
        )
        if doc_type and doc_type in metadata_blob:
            score *= 1.2
        if audience and audience in metadata_blob:
            score *= 1.1

        return score

    def retrieve(
        self,
        query: str,
        *,
        limit: int = 5,
        source_type: str | None = None,
        doc_type: str | None = None,
        audience: str | None = None,
    ) -> list[RetrievedChunk]:
        query_tokens = tokenize_mixed(query)
        results: list[RetrievedChunk] = []

        for indexed_chunk in self.indexed_chunks:
            if source_type and indexed_chunk.chunk.source_type != source_type:
                continue
            score = self.score(indexed_chunk, query_tokens, doc_type=doc_type, audience=audience)
            if score <= 0:
                continue
            results.append(RetrievedChunk(chunk=indexed_chunk.chunk, score=score))

        results.sort(key=lambda item: item.score, reverse=True)
        return results[:limit]
