from pathlib import Path

from rusemanticsearch.data.io import load_documents
from rusemanticsearch.retrieval.bm25 import BM25Retriever
from rusemanticsearch.text.normalize import RussianTextNormalizer


def test_bm25_returns_relevant_document_first() -> None:
    documents = load_documents(Path("data/documents.jsonl"))
    retriever = BM25Retriever(
        documents=documents,
        normalizer=RussianTextNormalizer(lemmatize=True),
    )

    results = retriever.search("лемматизация русского bm25", top_k=3)

    assert results[0].doc_id == "doc-6"
    assert results[0].rank == 1
