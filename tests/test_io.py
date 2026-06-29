from pathlib import Path

from rusemanticsearch.data.io import load_documents, load_eval_queries, load_qrels


def test_load_sample_documents() -> None:
    documents = load_documents(Path("data/documents.jsonl"))

    assert len(documents) == 10
    assert documents[0].id == "doc-1"
    assert documents[0].title
    assert "retrieval" in documents[0].tags


def test_load_sample_eval_files() -> None:
    queries = load_eval_queries(Path("data/eval_queries.jsonl"))
    qrels = load_qrels(Path("data/qrels.jsonl"))

    assert len(queries) == 5
    assert len(qrels) == 9
    assert {query.qid for query in queries} == {"q-1", "q-2", "q-3", "q-4", "q-5"}
