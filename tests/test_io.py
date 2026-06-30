from pathlib import Path

import pytest

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


def test_load_documents_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "documents.jsonl"
    path.write_text('{"id": "doc-1", "title": "Broken"', encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON"):
        load_documents(path)


def test_load_documents_rejects_missing_required_field(tmp_path: Path) -> None:
    path = tmp_path / "documents.jsonl"
    path.write_text('{"id": "doc-1", "text": "Missing title"}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="title"):
        load_documents(path)


def test_load_documents_rejects_duplicate_id(tmp_path: Path) -> None:
    path = tmp_path / "documents.jsonl"
    path.write_text(
        "\n".join(
            [
                '{"id": "doc-1", "title": "First", "text": "First text"}',
                '{"id": "doc-1", "title": "Second", "text": "Second text"}',
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate document id"):
        load_documents(path)


def test_load_eval_queries_rejects_duplicate_qid(tmp_path: Path) -> None:
    path = tmp_path / "eval_queries.jsonl"
    path.write_text(
        "\n".join(
            [
                '{"qid": "q-1", "query": "first"}',
                '{"qid": "q-1", "query": "second"}',
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate query id"):
        load_eval_queries(path)


def test_load_qrels_rejects_boolean_rel(tmp_path: Path) -> None:
    path = tmp_path / "qrels.jsonl"
    path.write_text('{"qid": "q-1", "doc_id": "doc-1", "rel": true}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="non-negative integer"):
        load_qrels(path)


def test_load_qrels_rejects_missing_file(tmp_path: Path) -> None:
    path = tmp_path / "missing_qrels.jsonl"

    with pytest.raises(FileNotFoundError):
        load_qrels(path)
