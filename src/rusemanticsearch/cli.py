from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rusemanticsearch.data.io import load_documents, load_eval_queries, load_qrels
from rusemanticsearch.eval.metrics import evaluate_run
from rusemanticsearch.retrieval.bm25 import BM25Retriever
from rusemanticsearch.text.normalize import RussianTextNormalizer

DEFAULT_DOCUMENTS_PATH = Path("data/documents.jsonl")
DEFAULT_EVAL_QUERIES_PATH = Path("data/eval_queries.jsonl")
DEFAULT_QRELS_PATH = Path("data/qrels.jsonl")


def build_bm25(documents_path: Path, lemmatize: bool) -> BM25Retriever:
    documents = load_documents(documents_path)
    normalizer = RussianTextNormalizer(lemmatize=lemmatize)
    return BM25Retriever(documents=documents, normalizer=normalizer)


def search_bm25(args: argparse.Namespace) -> None:
    retriever = build_bm25(args.documents, lemmatize=not args.no_lemmatize)
    results = retriever.search(args.query, top_k=args.top_k)

    for result in results:
        print(f"{result.rank}. {result.document.title} [{result.doc_id}] score={result.score:.4f}")
        print(f"   {result.document.text}")
        print(f"   source={result.document.source}")


def eval_bm25(args: argparse.Namespace) -> None:
    retriever = build_bm25(args.documents, lemmatize=not args.no_lemmatize)
    queries = load_eval_queries(args.eval_queries)
    qrels = load_qrels(args.qrels)
    metrics = evaluate_run(retriever=retriever, queries=queries, qrels=qrels, k=args.k)

    for metric_name, value in metrics.items():
        print(f"{metric_name}: {value:.4f}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(prog="rusearch")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search-bm25", help="Run BM25 search for one query")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--documents", type=Path, default=DEFAULT_DOCUMENTS_PATH)
    search_parser.add_argument("--top-k", type=int, default=5)
    search_parser.add_argument("--no-lemmatize", action="store_true")
    search_parser.set_defaults(func=search_bm25)

    eval_parser = subparsers.add_parser("eval-bm25", help="Evaluate BM25 on qrels")
    eval_parser.add_argument("--documents", type=Path, default=DEFAULT_DOCUMENTS_PATH)
    eval_parser.add_argument("--eval-queries", type=Path, default=DEFAULT_EVAL_QUERIES_PATH)
    eval_parser.add_argument("--qrels", type=Path, default=DEFAULT_QRELS_PATH)
    eval_parser.add_argument("-k", type=int, default=5)
    eval_parser.add_argument("--no-lemmatize", action="store_true")
    eval_parser.set_defaults(func=eval_bm25)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
