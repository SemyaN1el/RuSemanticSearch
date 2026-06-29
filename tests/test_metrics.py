from rusemanticsearch.data.schemas import Document, SearchResult
from rusemanticsearch.eval.metrics import mrr_at_k, ndcg_at_k, precision_at_k, recall_at_k


def _result(doc_id: str, rank: int) -> SearchResult:
    document = Document(id=doc_id, title=doc_id, text=doc_id)
    return SearchResult(doc_id=doc_id, score=1.0 / rank, rank=rank, document=document)


def test_ranking_metrics() -> None:
    results = [_result("doc-a", 1), _result("doc-b", 2), _result("doc-c", 3)]
    relevance = {"doc-b": 2, "doc-c": 1}

    assert precision_at_k(results, relevance, k=2) == 0.5
    assert recall_at_k(results, relevance, k=2) == 0.5
    assert mrr_at_k(results, relevance, k=3) == 0.5
    assert 0.0 < ndcg_at_k(results, relevance, k=3) < 1.0
