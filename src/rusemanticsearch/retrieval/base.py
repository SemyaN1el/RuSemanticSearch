from __future__ import annotations

from typing import Protocol

from rusemanticsearch.data.schemas import SearchResult


class Retriever(Protocol):
    def search(self, query: str, top_k: int = 10) -> list[SearchResult]: ...
