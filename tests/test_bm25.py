from pathlib import Path

from rusemanticsearch.data.io import load_documents
from rusemanticsearch.data.schemas import Document
from rusemanticsearch.retrieval.bm25 import BM25Retriever
from rusemanticsearch.text.normalize import RussianTextNormalizer


def test_bm25_returns_relevant_document_first() -> None:
    documents = [
        Document(
            id="doc-russian-normalization",
            title="Russian Lemmatization",
            text="Лемматизация русского текста улучшает BM25 поиск по документам.",
        ),
        Document(
            id="doc-image-search",
            title="Image Search",
            text="Поиск похожих изображений через векторные признаки.",
        ),
    ]
    retriever = BM25Retriever(
        documents=documents,
        normalizer=RussianTextNormalizer(lemmatize=True),
    )

    results = retriever.search("лемматизация русского bm25", top_k=3)

    assert results[0].doc_id == "doc-russian-normalization"
    assert results[0].rank == 1


def test_bm25_returns_empty_results_for_empty_query() -> None:
    documents = load_documents(Path("data/documents.jsonl"))
    retriever = BM25Retriever(
        documents=documents,
        normalizer=RussianTextNormalizer(lemmatize=True),
    )

    assert retriever.search("?!", top_k=3) == []
