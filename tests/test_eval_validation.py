import pytest

from rusemanticsearch.data.schemas import Document, EvalQuery, Qrel
from rusemanticsearch.eval.validation import validate_eval_data


def _documents() -> list[Document]:
    return [
        Document(id="doc-1", title="First", text="First document"),
        Document(id="doc-2", title="Second", text="Second document"),
    ]


def _queries() -> list[EvalQuery]:
    return [
        EvalQuery(qid="q-1", query="first query"),
        EvalQuery(qid="q-2", query="second query"),
    ]


def test_validate_eval_data_accepts_consistent_data() -> None:
    qrels = [
        Qrel(qid="q-1", doc_id="doc-1", rel=2),
        Qrel(qid="q-2", doc_id="doc-2", rel=1),
    ]

    validate_eval_data(documents=_documents(), queries=_queries(), qrels=qrels)


def test_validate_eval_data_rejects_unknown_qid() -> None:
    qrels = [
        Qrel(qid="q-1", doc_id="doc-1", rel=2),
        Qrel(qid="q-404", doc_id="doc-2", rel=1),
    ]

    with pytest.raises(ValueError, match="Unknown qid"):
        validate_eval_data(documents=_documents(), queries=_queries(), qrels=qrels)


def test_validate_eval_data_rejects_unknown_doc_id() -> None:
    qrels = [
        Qrel(qid="q-1", doc_id="doc-1", rel=2),
        Qrel(qid="q-2", doc_id="doc-404", rel=1),
    ]

    with pytest.raises(ValueError, match="Unknown doc_id"):
        validate_eval_data(documents=_documents(), queries=_queries(), qrels=qrels)


def test_validate_eval_data_rejects_invalid_relevance_value() -> None:
    qrels = [
        Qrel(qid="q-1", doc_id="doc-1", rel=2),
        Qrel(qid="q-2", doc_id="doc-2", rel=3),
    ]

    with pytest.raises(ValueError, match="Invalid relevance value"):
        validate_eval_data(documents=_documents(), queries=_queries(), qrels=qrels)


def test_validate_eval_data_rejects_duplicate_qrel_pair() -> None:
    qrels = [
        Qrel(qid="q-1", doc_id="doc-1", rel=2),
        Qrel(qid="q-1", doc_id="doc-1", rel=1),
        Qrel(qid="q-2", doc_id="doc-2", rel=1),
    ]

    with pytest.raises(ValueError, match="Duplicate qrel"):
        validate_eval_data(documents=_documents(), queries=_queries(), qrels=qrels)


def test_validate_eval_data_rejects_query_without_qrels() -> None:
    qrels = [
        Qrel(qid="q-1", doc_id="doc-1", rel=2),
    ]

    with pytest.raises(ValueError, match="Queries without qrels: q-2"):
        validate_eval_data(documents=_documents(), queries=_queries(), qrels=qrels)
