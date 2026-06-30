from __future__ import annotations

from rank_bm25 import BM25Okapi

from rusemanticsearch.data.schemas import Document, SearchResult
from rusemanticsearch.text.normalize import RussianTextNormalizer


class BM25Retriever:
    def __init__(
        self,
        documents: list[Document],
        normalizer: RussianTextNormalizer | None = None,
    ) -> None:
        if not documents:
            raise ValueError("BM25Retriever requires at least one document")

        self.documents = documents
        self.normalizer = normalizer or RussianTextNormalizer()
        self._tokenized_corpus = [
            self.normalizer.tokens(document.searchable_text) for document in documents
        ]
        self._bm25 = BM25Okapi(self._tokenized_corpus)

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        if top_k <= 0:
            raise ValueError("top_k must be positive")

        query_tokens = self.normalizer.tokens(query)
        if not query_tokens:
            return []

        scores = self._bm25.get_scores(query_tokens)
        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: float(scores[index]),
            reverse=True,
        )

        results: list[SearchResult] = []
        for rank, index in enumerate(ranked_indices[:top_k], start=1):
            document = self.documents[index]
            results.append(
                SearchResult(
                    doc_id=document.id,
                    score=float(scores[index]),
                    rank=rank,
                    document=document,
                )
            )
        return results
