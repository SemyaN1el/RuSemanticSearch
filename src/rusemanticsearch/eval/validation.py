from __future__ import annotations

from rusemanticsearch.data.schemas import Document, EvalQuery, Qrel

VALID_RELEVANCE_VALUES = {0, 1, 2}


def validate_eval_data(
    documents: list[Document],
    queries: list[EvalQuery],
    qrels: list[Qrel],
) -> None:
    document_ids = {document.id for document in documents}
    query_ids = {query.qid for query in queries}
    qids_with_qrels: set[str] = set()
    qids_with_positive_qrels: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()

    for qrel in qrels:
        if qrel.qid not in query_ids:
            raise ValueError(f"Unknown qid in qrels: {qrel.qid}")

        if qrel.doc_id not in document_ids:
            raise ValueError(f"Unknown doc_id in qrels: {qrel.doc_id}")

        if qrel.rel not in VALID_RELEVANCE_VALUES:
            raise ValueError(
                f"Invalid relevance value for qid={qrel.qid}, doc_id={qrel.doc_id}: "
                f"{qrel.rel}. Expected one of {sorted(VALID_RELEVANCE_VALUES)}"
            )

        pair = (qrel.qid, qrel.doc_id)
        if pair in seen_pairs:
            raise ValueError(f"Duplicate qrel for qid={qrel.qid}, doc_id={qrel.doc_id}")

        seen_pairs.add(pair)
        qids_with_qrels.add(qrel.qid)
        if qrel.rel > 0:
            qids_with_positive_qrels.add(qrel.qid)

    queries_without_qrels = sorted(
        query.qid for query in queries if query.qid not in qids_with_qrels
    )
    if queries_without_qrels:
        raise ValueError(f"Queries without qrels: {', '.join(queries_without_qrels)}")

    queries_without_positive_qrels = sorted(
        query.qid for query in queries if query.qid not in qids_with_positive_qrels
    )
    if queries_without_positive_qrels:
        raise ValueError(
            f"Queries without positive qrels: {', '.join(queries_without_positive_qrels)}"
        )
