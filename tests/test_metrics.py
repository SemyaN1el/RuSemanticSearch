import pytest

from rusemanticsearch.data.schemas import Document, EvalQuery, Qrel, SearchResult
from rusemanticsearch.eval.metrics import (
    evaluate_run,
    mrr_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


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


class _StaticRetriever:
    def search(self, query: str, top_k: int) -> list[SearchResult]:
        return [_result("doc-a", 1)]


def test_evaluate_run_rejects_query_without_positive_qrels() -> None:
    queries = [EvalQuery(qid="q-1", query="first query")]
    qrels = [Qrel(qid="q-1", doc_id="doc-a", rel=0)]

    with pytest.raises(ValueError, match="Query has no positive qrels: q-1"):
        evaluate_run(retriever=_StaticRetriever(), queries=queries, qrels=qrels, k=1)
