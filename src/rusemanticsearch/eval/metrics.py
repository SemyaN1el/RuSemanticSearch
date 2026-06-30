from __future__ import annotations

import math
from collections import defaultdict

from rusemanticsearch.data.schemas import EvalQuery, Qrel, SearchResult
from rusemanticsearch.retrieval.base import Retriever


def qrels_by_query(qrels: list[Qrel]) -> dict[str, dict[str, int]]:
    grouped: dict[str, dict[str, int]] = defaultdict(dict)
    for qrel in qrels:
        grouped[qrel.qid][qrel.doc_id] = qrel.rel
    return dict(grouped)


def has_positive_relevance(relevance: dict[str, int]) -> bool:
    return any(rel > 0 for rel in relevance.values())


def precision_at_k(results: list[SearchResult], relevance: dict[str, int], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")
    if not results:
        return 0.0

    hits = sum(1 for result in results[:k] if relevance.get(result.doc_id, 0) > 0)
    return hits / k


def recall_at_k(results: list[SearchResult], relevance: dict[str, int], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")

    relevant_doc_ids = {doc_id for doc_id, rel in relevance.items() if rel > 0}
    if not relevant_doc_ids:
        return 0.0

    retrieved_doc_ids = {result.doc_id for result in results[:k]}
    return len(relevant_doc_ids & retrieved_doc_ids) / len(relevant_doc_ids)


def mrr_at_k(results: list[SearchResult], relevance: dict[str, int], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")

    for rank, result in enumerate(results[:k], start=1):
        if relevance.get(result.doc_id, 0) > 0:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(results: list[SearchResult], relevance: dict[str, int], k: int) -> float:
    if k <= 0:
        raise ValueError("k must be positive")

    def gain(rel: int) -> float:
        return (2.0**rel) - 1.0

    dcg = 0.0
    for rank, result in enumerate(results[:k], start=1):
        rel = relevance.get(result.doc_id, 0)
        dcg += gain(rel) / math.log2(rank + 1)

    ideal_rels = sorted((rel for rel in relevance.values() if rel > 0), reverse=True)[:k]
    ideal_dcg = sum(gain(rel) / math.log2(rank + 1) for rank, rel in enumerate(ideal_rels, start=1))
    if ideal_dcg == 0:
        return 0.0
    return dcg / ideal_dcg


def evaluate_run(
    retriever: Retriever,
    queries: list[EvalQuery],
    qrels: list[Qrel],
    k: int,
) -> dict[str, float]:
    if k <= 0:
        raise ValueError("k must be positive")
    if not queries:
        raise ValueError("Evaluation requires at least one query")

    grouped_qrels = qrels_by_query(qrels)
    totals = {
        "precision": 0.0,
        "recall": 0.0,
        "mrr": 0.0,
        "ndcg": 0.0,
    }

    for query in queries:
        relevance = grouped_qrels.get(query.qid, {})
        if not has_positive_relevance(relevance):
            raise ValueError(f"Query has no positive qrels: {query.qid}")

        results = retriever.search(query.query, top_k=k)
        totals["precision"] += precision_at_k(results, relevance, k)
        totals["recall"] += recall_at_k(results, relevance, k)
        totals["mrr"] += mrr_at_k(results, relevance, k)
        totals["ndcg"] += ndcg_at_k(results, relevance, k)

    query_count = len(queries)
    return {
        f"Precision@{k}": totals["precision"] / query_count,
        f"Recall@{k}": totals["recall"] / query_count,
        f"MRR@{k}": totals["mrr"] / query_count,
        f"nDCG@{k}": totals["ndcg"] / query_count,
    }
