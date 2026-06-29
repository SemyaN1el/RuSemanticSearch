"""Data loading and schemas."""

from rusemanticsearch.data.io import load_documents, load_eval_queries, load_qrels
from rusemanticsearch.data.schemas import Document, EvalQuery, Qrel, SearchResult

__all__ = [
    "Document",
    "EvalQuery",
    "Qrel",
    "SearchResult",
    "load_documents",
    "load_eval_queries",
    "load_qrels",
]
