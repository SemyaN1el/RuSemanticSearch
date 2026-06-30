# Project Plan

Этот файл - долговременная память проекта RuSemanticSearch. Его нужно обновлять после важных решений, завершенных этапов и смены ближайших задач, чтобы не терять контекст при сжатии чата.

## Текущий статус

Проект уже имеет минимальный working baseline:

```text
documents.jsonl
-> RussianTextNormalizer
-> BM25Retriever
-> SearchResult
-> evaluate_run
-> Precision / Recall / MRR / nDCG
```

Репозиторий GitHub:

```text
https://github.com/SemyaN1el/RuSemanticSearch.git
```

Основная ветка:

```text
main
```

Последний опубликованный коммит:

```text
92cbfcb Add eval data validation
```

## Что уже реализовано

- Python-пакет `rusemanticsearch`.
- Управление окружением через `uv`.
- CLI-команда `rusearch`.
- JSONL-форматы:
  - `data/documents.jsonl`;
  - `data/eval_queries.jsonl`;
  - `data/qrels.jsonl`.
- Схемы:
  - `Document`;
  - `EvalQuery`;
  - `Qrel`;
  - `SearchResult`.
- Загрузчики JSONL с базовой валидацией.
- Русская нормализация через `pymorphy3`.
- BM25 baseline через `rank-bm25`.
- Метрики:
  - `Precision@K`;
  - `Recall@K`;
  - `MRR@K`;
  - `nDCG@K`.
- Валидация eval-данных.
- Тесты.
- Quality gates через `ruff` и `pytest`.

## Текущие незакоммиченные изменения

После ревью были внесены правки, которые пока не закоммичены:

- `evaluate_run()` больше не молча усредняет запросы без позитивных qrels.
- `validate_eval_data()` требует хотя бы один `rel > 0` для каждого eval-запроса.
- `load_qrels()` отклоняет `rel: true`, потому что `bool` в Python является подклассом `int`.
- `BM25Retriever.search()` возвращает `[]` для пустого запроса.
- `Retriever.search()` получил default `top_k=10`.
- Добавлены негативные тесты загрузчиков.
- Тест BM25 больше не завязан на конкретный sample-документ `doc-6`.

Состояние на 2026-07-01: рабочее дерево не закоммичено, но последние локальные проверки зеленые:

```text
ruff: OK
pytest: 21 passed
eval-bm25: OK
```

Предложенный commit message:

```text
Harden eval validation and document roadmap
```

Перед коммитом нужно выполнить:

```powershell
uv run ruff check .
uv run pytest
uv run rusearch eval-bm25 -k 5
```

Если хотя бы один gate красный, коммит не делать: сначала починить код или тесты, затем повторить проверки.

## Команды разработки

Установить/обновить окружение:

```powershell
uv sync
```

Запустить BM25-поиск:

```powershell
uv run rusearch search-bm25 "лемматизация русского bm25" --top-k 3
```

Посчитать метрики:

```powershell
uv run rusearch eval-bm25 -k 5
```

Проверить стиль и потенциальные ошибки:

```powershell
uv run ruff check .
```

Запустить тесты:

```powershell
uv run pytest
```

Автоисправить безопасные замечания `ruff`:

```powershell
uv run ruff check . --fix
uv run ruff format .
```

## Важные проектные решения

### 1. JSONL вместо JSON

Документы и разметка хранятся в JSONL, потому что корпус удобно читать построчно, валидировать с номерами строк и расширять без загрузки всего файла в память.

### 2. BM25 сначала

BM25 нужен как lexical baseline. Dense retrieval и reranker должны сравниваться с ним, а не заменять его без измерений.

### 3. Русская лемматизация

`pymorphy3` применяется только к кириллическим токенам. Английские технические токены пока оставляются как есть.

### 4. Eval важнее обучения

До fine-tuning должен быть фиксированный eval-набор. Иначе нельзя понять, улучшилось качество или модель переобучилась под синтетические запросы.

### 5. Fine-tuning не обязан улучшить качество

Сильная готовая embedding-модель может быть лучше дообученной на маленькой синтетике. Цель fine-tuning этапа - измерить эффект, а не гарантированно повысить метрики.

### 6. Hybrid через RRF

Для объединения BM25 и dense retrieval планируется Reciprocal Rank Fusion, а не сложение raw scores. BM25 score и cosine similarity находятся в разных шкалах.

### 7. e5 требует префиксы

Если используется e5-подобная модель, нужно соблюдать формат:

```text
query: <текст запроса>
passage: <текст документа>
```

## Ближайший roadmap

### Этап A. Закрыть hardening baseline

Статус: локальные quality gates зеленые, но этап еще не закрыт, потому что изменения не закоммичены и не запушены.

Задачи:

- прогнать `ruff`, `pytest`, `eval-bm25`;
- если gate красный - починить и повторить проверки;
- закоммитить hardening-правки;
- запушить в `origin/main`;
- держать `PROJECT_PLAN.md` синхронизированным с фактическим состоянием проекта.

### Этап A.1. CI на GitHub Actions

Цель: чтобы GitHub сам проверял pull request / push.

Минимальный workflow:

```text
uv sync
uv run ruff check .
uv run pytest
uv run rusearch eval-bm25 -k 5
```

Почему это нужно: локальные проверки легко забыть, а CI делает quality gates видимыми в GitHub.

### Этап B. Сбор реального корпуса

Цель: заменить игрушечный sample-корпус на первый реальный корпус.

Рекомендуемый первый источник:

```text
GitHub README files
```

Почему:

- README похожи на целевой домен проекта;
- удобно искать NLP/search/retrieval проекты;
- есть URL, описание, topics, language, stars, license;
- легко получить документы через GitHub API.

План:

```text
scripts/collect_github_readmes.py
-> GitHub API search
-> README download
-> normalize metadata
-> data/documents.jsonl
```

Начальный объем:

```text
100-300 README documents
```

После сбора:

- проверить дубликаты;
- удалить пустые/мусорные README;
- вручную просмотреть часть корпуса;
- зафиксировать, какие license/TOS ограничения есть у источника;
- не сохранять приватные или явно чувствительные данные;
- хранить `source_url`, чтобы происхождение документа было проверяемым;
- обновить `docs/DOCUMENT_SOURCES.md`, если подход изменился.

### Этап C. Нормальный eval-набор

Цель: сделать не игрушечные, а полезные метрики.

Минимум:

```text
30-50 документов
10-15 eval-запросов
qrels с ручной проверкой
```

Лучше:

```text
300+ документов
50 eval-запросов
pooling из BM25 и будущего dense baseline
rel = 0 / 1 / 2
```

Важно:

- eval-запросы не использовать для обучения;
- каждый eval-запрос должен иметь хотя бы один `rel > 0`;
- qrels должны ссылаться только на существующие `qid` и `doc_id`.

### Этап D. Dense retrieval baseline

После корпуса и eval:

```text
sentence-transformers / e5
-> document embeddings
-> vector index
-> search
-> same eval metrics
```

Возможные варианты:

- сначала локальный FAISS;
- затем Qdrant как векторная БД.

FAISS проще для первого dense baseline. Qdrant полезен позже, чтобы показать работу с production-like vector DB.

Технические задачи:

```text
scripts/build_dense_index.py
-> read data/documents.jsonl
-> encode passages
-> save artifacts/indexes/<index-name>
-> write index metadata
```

Индекс должен быть воспроизводимым: в metadata сохранить модель, дату сборки, количество документов и параметры чанкинга.

### Этап E. Hybrid retrieval

Объединить BM25 и dense results через RRF:

```text
BM25 top-N + dense top-N -> RRF -> final candidates
```

Метрики:

- `Recall@50`;
- `Recall@100`;
- `nDCG@10`;
- `MRR@10`.

### Этап F. Reranker

После hybrid:

```text
hybrid top-50/top-100
-> cross-encoder
-> reranked top-10
```

Цель reranker:

- улучшить порядок выдачи;
- поднять `nDCG@10`;
- поднять `MRR@10`;
- возможно улучшить `Precision@10`.

### Этап G. Генерация train_pairs.jsonl

Только после понятного корпуса и отдельного eval.

Цель: подготовить обучающие пары без загрязнения eval-набора.

План:

```text
documents.jsonl
-> LLM query generation
-> positives: source document
-> hard negatives: BM25 top results excluding positive doc
-> data/train_pairs.jsonl
```

Важно:

- eval-запросы не использовать для train-pairs;
- hard-negative mining должен быть воспроизводимым;
- часть синтетики нужно просмотреть руками, иначе fine-tuning может учиться на мусоре.

### Этап H. Fine-tuning bi-encoder

Только после стабильного eval:

```text
train_pairs.jsonl
-> MultipleNegativesRankingLoss
-> fine-tuned bi-encoder
-> compare against base embedding model
```

Ожидание:

- fine-tuning может улучшить качество;
- может не улучшить;
- оба результата валидны, если измерены честно.

## Что читать при возврате к проекту

1. `PROJECT_PLAN.md` - текущий roadmap и состояние.
2. `README.md` - общая архитектура.
3. `DATA_PIPELINE.md` - методология train/eval данных.
4. `CODE_QUALITY.md` - правила ревью и проверки.
5. `docs/DOCUMENT_SOURCES.md` - источники документов.
6. `src/rusemanticsearch/data/schemas.py` - основные структуры.
7. `src/rusemanticsearch/data/io.py` - загрузка JSONL.
8. `src/rusemanticsearch/text/normalize.py` - токенизация и лемматизация.
9. `src/rusemanticsearch/retrieval/bm25.py` - baseline retrieval.
10. `src/rusemanticsearch/eval/metrics.py` - формулы метрик.
11. `src/rusemanticsearch/eval/validation.py` - проверка eval-разметки.
12. `src/rusemanticsearch/cli.py` - запуск pipeline.
13. `tests/test_eval_validation.py` - правила качества eval-разметки.
14. `tests/test_metrics.py` - ожидаемое поведение метрик.

## Definition of Done для этапов

Этап считается завершенным только если:

- код реализован и покрыт релевантными тестами;
- `uv run ruff check .` проходит;
- `uv run pytest` проходит;
- для retrieval/eval изменений проходит `uv run rusearch eval-bm25 -k 5`;
- документация обновлена, если изменился workflow или архитектура;
- изменения закоммичены понятным маленьким коммитом;
- при необходимости изменения запушены в GitHub.

## Правила коммитов

- Перед коммитом запускать:

```powershell
uv run ruff check .
uv run pytest
```

- Для retrieval/eval изменений также запускать:

```powershell
uv run rusearch eval-bm25 -k 5
```

- Коммитить маленькими логическими шагами.
- Перед push проверять:

```powershell
git status --short --branch
git log --oneline -3
```

## Следующее рекомендуемое действие

Закоммитить текущие hardening-правки и `PROJECT_PLAN.md`.

Вариант commit message:

```text
Harden eval validation and document roadmap
```

После этого перейти к сборщику GitHub README.
