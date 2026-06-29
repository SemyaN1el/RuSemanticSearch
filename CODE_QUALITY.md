# Code Quality

This project is developed in small reviewable steps. Each step should be easy to inspect, run, and compare against previous behavior.

## Review Goals

When reviewing code, check four things:

1. Correctness: the code returns expected results and edge cases fail clearly.
2. Simplicity: the implementation solves the current step without adding future-only abstractions.
3. Extensibility: BM25, dense retrieval, hybrid retrieval, and reranking can be added without rewriting unrelated modules.
4. Measurability: retrieval changes should be evaluated with the same `eval_queries.jsonl` and `qrels.jsonl`.

## Quality Gates

Run these before accepting a step:

```powershell
uv run ruff check .
uv run pytest
uv run rusearch eval-bm25 -k 5
```

Optional formatting check:

```powershell
uv run ruff format --check .
```

## Current Design Rules

- Data schemas live in `src/rusemanticsearch/data/`.
- Text preprocessing lives in `src/rusemanticsearch/text/`.
- Retrieval implementations live in `src/rusemanticsearch/retrieval/`.
- Evaluation code lives in `src/rusemanticsearch/eval/`.
- CLI is a thin layer over package code.
- Tests cover loaders, normalization, retrieval behavior, and metric formulas.

## What To Watch Closely

- No metric should depend on a specific retrieval implementation.
- No loader should silently accept malformed JSONL.
- No retriever should mutate documents.
- BM25 should use Russian normalization by default.
- Future dense retrievers should respect model-specific input formats, for example `query:` and `passage:` for e5 models.
- Fine-tuning must not use eval queries or qrels.

## First Iteration Acceptance Criteria

The first implementation is acceptable when:

- `data/documents.jsonl`, `data/eval_queries.jsonl`, and `data/qrels.jsonl` load correctly.
- BM25 search runs from CLI.
- Evaluation prints `Precision@K`, `Recall@K`, `MRR@K`, and `nDCG@K`.
- Tests pass.
- Lint passes.

The sample corpus is intentionally small. Its purpose is to verify the pipeline, not to prove retrieval quality.
