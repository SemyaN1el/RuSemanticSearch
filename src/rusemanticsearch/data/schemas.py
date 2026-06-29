from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    text: str
    source: str = "unknown"
    tags: tuple[str, ...] = field(default_factory=tuple)
    url: str = ""

    @property
    def searchable_text(self) -> str:
        return f"{self.title}\n{self.text}"


@dataclass(frozen=True)
class EvalQuery:
    qid: str
    query: str


@dataclass(frozen=True)
class Qrel:
    qid: str
    doc_id: str
    rel: int


@dataclass(frozen=True)
class SearchResult:
    doc_id: str
    score: float
    rank: int
    document: Document
