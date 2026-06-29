# Document Sources

This file describes where to get documents for the first real RuSemanticSearch corpus.

The goal is not to collect "any text". The corpus should contain documents that make sense for a retrieval portfolio project: project descriptions, README files, dataset cards, paper abstracts, and technical notes around NLP, search, embeddings, ranking, and Russian text processing.

## Recommended First Corpus

Start with 300-1000 short documents:

1. GitHub repository README files for NLP/search/ML projects.
2. Hugging Face dataset cards and selected text datasets.
3. arXiv paper titles and abstracts for retrieval, embeddings, ranking, IR, NLP, and Russian NLP.
4. Your own project notes, summaries, and manually written descriptions.

This is enough for BM25, dense baseline, and first eval. Do not start with massive crawling.

## Source 1: GitHub READMEs

Best first source for a portfolio-style search engine.

What to collect:

- repository name;
- description;
- README text;
- topics/tags;
- language;
- stars as optional metadata;
- license if available;
- repository URL.

Why useful:

- project README files look like the target domain;
- documents naturally contain mixed Russian/English technical text;
- easy to build queries like "проект про semantic search", "retrieval with reranking", "поиск похожих документов".

Recommended document shape:

```json
{
  "id": "github-owner-repo",
  "title": "owner/repo",
  "text": "repository description + README text",
  "source": "github",
  "tags": ["nlp", "retrieval"],
  "url": "https://github.com/owner/repo"
}
```

Use the GitHub REST API instead of scraping pages:

- repository search: https://docs.github.com/en/rest/search/search
- repository README/content: https://docs.github.com/en/rest/repos/contents

Practical search queries:

```text
semantic search language:Python topic:nlp
bm25 reranker language:Python
dense retrieval language:Python
russian nlp language:Python
sentence-transformers retrieval
```

Quality rules:

- keep only repositories with meaningful README text;
- store license metadata if available;
- deduplicate forks and near-empty READMEs;
- do not use private repositories;
- keep the original URL in `url`.

## Source 2: Hugging Face Datasets

Good source for dataset cards and optionally dataset rows.

What to collect first:

- dataset card title/description;
- task tags;
- language tags;
- dataset summary;
- source URL.

Later, selected rows can be sampled from text datasets, but start with dataset cards because they are concise and easier to inspect.

Useful APIs/docs:

- Hub Python API `list_datasets`: https://huggingface.co/docs/huggingface_hub/en/package_reference/hf_api
- Dataset Viewer API: https://huggingface.co/docs/dataset-viewer/index

Useful filters:

```python
api.list_datasets(filter=("language:ru", "task_categories:text-classification"))
api.list_datasets(filter=("language:ru", "task_ids:language-modeling"))
api.list_datasets(search="retrieval")
api.list_datasets(search="russian")
```

Quality rules:

- prefer datasets with clear license and dataset card;
- avoid huge raw dumps in the first iteration;
- sample small, inspect manually, and keep provenance;
- do not mix dataset rows into eval if they were used for training query generation.

## Source 3: arXiv Titles And Abstracts

Good source for technical documents around IR, embeddings, ranking, and NLP.

What to collect:

- paper id;
- title;
- abstract;
- categories;
- authors as optional metadata;
- arXiv URL.

Use the official arXiv API:

- API manual: https://info.arxiv.org/help/api/user-manual.html

Example query topics:

```text
cat:cs.IR AND all:retrieval
cat:cs.CL AND all:sentence embeddings
cat:cs.CL AND all:reranking
cat:cs.CL AND all:Russian
```

Recommended document shape:

```json
{
  "id": "arxiv-2401.12345",
  "title": "Paper title",
  "text": "Abstract text",
  "source": "arxiv",
  "tags": ["cs.IR", "retrieval"],
  "url": "https://arxiv.org/abs/2401.12345"
}
```

Quality rules:

- collect metadata and abstracts, not PDFs, in the first iteration;
- respect arXiv API delays and paging;
- avoid overloading the API;
- keep categories as tags.

## Source 4: Manual Project Descriptions

For eval quality, manual data is often better than more scraped data.

Write 50-100 short project descriptions yourself:

```text
Hybrid semantic search over Russian documents with BM25, e5 embeddings, FAISS, and cross-encoder reranking.
```

Why useful:

- you control the domain;
- you can create clean eval queries;
- it avoids licensing ambiguity;
- it gives known positives for early evaluation.

## What Not To Use First

Avoid these at the beginning:

- random web scraping;
- news websites;
- social media posts;
- massive Wikipedia dumps;
- PDF parsing at scale;
- unlabeled raw text with unclear license;
- corpora where documents are too long before chunking exists.

These can be useful later, but they add noise and legal/processing complexity before the retrieval core is stable.

## First Collection Plan

Recommended first real dataset:

```text
200 GitHub README documents
100 Hugging Face dataset cards
100 arXiv abstracts
50 manual project descriptions
```

Then build:

```text
documents.jsonl
eval_queries.jsonl
qrels.jsonl
```

Only after that:

```text
train_pairs.jsonl
hard negatives
fine-tuning
```

## Acceptance Criteria For Documents

Every document should have:

- stable `id`;
- non-empty `title`;
- useful `text`;
- `source`;
- `url` when available;
- optional `tags`;
- clear enough licensing/provenance for portfolio use.

Bad documents should be dropped early. A smaller clean corpus is better than a large noisy one.
