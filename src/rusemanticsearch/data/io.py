from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from rusemanticsearch.data.schemas import Document, EvalQuery, Qrel


def _read_jsonl[T](path: Path, parser: Callable[[dict[str, Any], int], T]) -> list[T]:
    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    rows: list[T] = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                raw = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSON at {path}:{line_number}") from error

            if not isinstance(raw, dict):
                raise ValueError(f"Expected JSON object at {path}:{line_number}")

            rows.append(parser(raw, line_number))

    return rows


def _require_str(raw: dict[str, Any], key: str, path: Path, line_number: int) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Expected non-empty string field '{key}' at {path}:{line_number}")
    return value.strip()


def _optional_str(raw: dict[str, Any], key: str, default: str) -> str:
    value = raw.get(key, default)
    if value is None:
        return default
    return str(value).strip()


def _optional_tags(raw: dict[str, Any]) -> tuple[str, ...]:
    value = raw.get("tags", [])
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError("Expected 'tags' to be a list")
    return tuple(str(item).strip() for item in value if str(item).strip())


def load_documents(path: Path | str) -> list[Document]:
    source_path = Path(path)

    def parse(raw: dict[str, Any], line_number: int) -> Document:
        try:
            return Document(
                id=_require_str(raw, "id", source_path, line_number),
                title=_require_str(raw, "title", source_path, line_number),
                text=_require_str(raw, "text", source_path, line_number),
                source=_optional_str(raw, "source", "unknown"),
                tags=_optional_tags(raw),
                url=_optional_str(raw, "url", ""),
            )
        except ValueError as error:
            raise ValueError(f"Invalid document at {source_path}:{line_number}: {error}") from error

    documents = _read_jsonl(source_path, parse)
    seen: set[str] = set()
    for document in documents:
        if document.id in seen:
            raise ValueError(f"Duplicate document id: {document.id}")
        seen.add(document.id)
    return documents


def load_eval_queries(path: Path | str) -> list[EvalQuery]:
    source_path = Path(path)

    def parse(raw: dict[str, Any], line_number: int) -> EvalQuery:
        return EvalQuery(
            qid=_require_str(raw, "qid", source_path, line_number),
            query=_require_str(raw, "query", source_path, line_number),
        )

    queries = _read_jsonl(source_path, parse)
    seen: set[str] = set()
    for query in queries:
        if query.qid in seen:
            raise ValueError(f"Duplicate query id: {query.qid}")
        seen.add(query.qid)
    return queries


def load_qrels(path: Path | str) -> list[Qrel]:
    source_path = Path(path)

    def parse(raw: dict[str, Any], line_number: int) -> Qrel:
        qid = _require_str(raw, "qid", source_path, line_number)
        doc_id = _require_str(raw, "doc_id", source_path, line_number)
        rel = raw.get("rel")
        if isinstance(rel, bool) or not isinstance(rel, int) or rel < 0:
            raise ValueError(
                f"Expected non-negative integer field 'rel' at {source_path}:{line_number}"
            )
        return Qrel(qid=qid, doc_id=doc_id, rel=rel)

    return _read_jsonl(source_path, parse)
