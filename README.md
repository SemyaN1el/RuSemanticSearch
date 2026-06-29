# RuSemanticSearch

RuSemanticSearch - учебный NLP/retrieval-проект для стажировки: гибридный поиск по русскоязычным и смешанным русско-английским текстам, который объединяет обычный keyword search, семантический поиск через embeddings и нейросетевое переранжирование.

Главная идея проекта: пользователь вводит запрос естественным языком, а система находит релевантные документы, фрагменты или похожие проекты даже тогда, когда слова в запросе и документе не совпадают буквально.

Главный риск проекта - не архитектура, а данные. Поэтому отдельно фиксируются:

- методология подготовки обучающих пар и eval-набора: [DATA_PIPELINE.md](DATA_PIPELINE.md);
- практичные источники документов: [docs/DOCUMENT_SOURCES.md](docs/DOCUMENT_SOURCES.md);
- критерии качества кода: [CODE_QUALITY.md](CODE_QUALITY.md).

Пример:

```text
Запрос:
хочу проект про поиск похожих документов на русском

Результаты:
1. Semantic Search over Russian Texts
2. Hybrid BM25 + Dense Retrieval
3. Cross Encoder Reranking for Document Search
```

## Цель проекта

Сделать production-like мини-поисковик, в котором есть не только готовая embedding-модель, но и полноценный retrieval pipeline:

```text
документы
-> очистка, нормализация и при необходимости чанкинг
-> BM25 baseline с русской нормализацией
-> dense retrieval через bi-encoder
-> hybrid search через RRF
-> cross-encoder reranker
-> top-k выдача
-> оценка качества
```

Проект должен показать следующие навыки:

- построение поисковой системы;
- работа с русскоязычными текстами;
- подготовка корпуса документов;
- подготовка train/eval данных без утечки;
- построение baseline-модели;
- fine-tuning bi-encoder модели;
- использование vector index: FAISS или Qdrant;
- объединение результатов через Reciprocal Rank Fusion;
- reranking результатов;
- оценка качества поиска через retrieval-метрики;
- оформление проекта как воспроизводимого ML/NLP pipeline.

## Что именно обучается

Не нужно обучать "поисковик целиком". Поисковик - это система из нескольких компонентов. Обучаемая часть - модель релевантности.

Основная обучаемая модель:

```text
bi-encoder
```

Она отдельно кодирует запрос и документ в векторы:

```text
query_encoder("проект про поиск похожих документов") -> query_vector
doc_encoder("semantic search over Russian texts") -> document_vector
```

Затем релевантность считается через близость векторов:

```text
score(query, document) = cosine_similarity(query_vector, document_vector)
```

Модель должна учиться делать так, чтобы:

```text
score(query, positive_document) > score(query, negative_document)
```

Важно: fine-tuning не обязан улучшить качество. Сильная готовая multilingual/russian embedding-модель уже может быть близка к потолку на небольшом корпусе. Поэтому цель этапа - не "обязательно побить baseline", а честно измерить, помогает ли дообучение на наших данных.

Дополнительная сильная часть:

```text
cross-encoder reranker
```

Он получает запрос и документ вместе:

```text
[query, document] -> relevance_score
```

Reranker работает медленнее bi-encoder, поэтому применяется не ко всему корпусу, а только к top-N кандидатам, найденным быстрым поиском.

## Почему не обучать модель с нуля

Обучать собственный Transformer, GPT-подобную модель или "аналог Алисы" с нуля не нужно.

Причины:

- это слишком дорого по данным и вычислениям;
- это не нужно для задачи retrieval;
- стажерский проект должен демонстрировать умение правильно использовать и дообучать существующие модели;
- в индустрии часто берут предобученную модель и адаптируют ее под домен.

Правильный подход:

```text
готовая multilingual/russian sentence-transformer модель
-> baseline-замер
-> fine-tuning на парах query/document
-> повторный замер
-> vector index
-> retrieval
-> reranking
```

## Архитектура

Планируемая архитектура системы:

```text
                     ┌────────────────────┐
                     │ User Query          │
                     └─────────┬──────────┘
                               │
             ┌─────────────────┴─────────────────┐
             │                                   │
             v                                   v
   ┌───────────────────┐              ┌────────────────────┐
   │ BM25 Retrieval     │              │ Dense Retrieval     │
   │ keyword search     │              │ bi-encoder + index  │
   └─────────┬─────────┘              └──────────┬─────────┘
             │                                   │
             └─────────────────┬─────────────────┘
                               v
                    ┌────────────────────┐
                    │ Result Fusion       │
                    │ hybrid candidates   │
                    └─────────┬──────────┘
                              v
                    ┌────────────────────┐
                    │ Cross-Encoder       │
                    │ Reranker            │
                    └─────────┬──────────┘
                              v
                    ┌────────────────────┐
                    │ Final Top-K Results │
                    └────────────────────┘
```

## Этапы разработки

### Этап 1. BM25 baseline

Сначала реализуется lexical search:

```text
documents.jsonl -> Russian normalization -> BM25 -> top-k results
```

Зачем:

- быстро получить рабочий поиск;
- зафиксировать формат документов;
- получить baseline для будущего сравнения;
- проверить, что корпус, CLI/API и ранжирование работают.

Почему не начинать сразу с embeddings:

- без baseline непонятно, стало ли лучше;
- ошибки в корпусе и пайплайне проще найти на BM25;
- embeddings и FAISS добавляют сложность, которую лучше вводить после рабочего минимума.

Для русского языка BM25 нельзя оставлять совсем примитивным. Из-за падежей, склонений и форм слов простой whitespace-tokenizer даст искусственно слабый baseline. Минимально нужен regex-tokenizer + нормализация слов: `pymorphy3` для лемматизации или Snowball stemmer как более простой вариант.

### Этап 2. Корпус документов

Документы хранятся в JSONL-формате:

```json
{"id":"doc-1","title":"Semantic Search over Russian Texts","text":"Проект про семантический поиск русскоязычных документов.","source":"sample"}
```

Базовые поля:

- `id` - стабильный идентификатор документа;
- `title` - заголовок для выдачи;
- `text` - основной текст для поиска;
- `source` - источник документа;
- `tags` - опциональные теги;
- `url` - опциональная ссылка на источник.

Почему JSONL:

- удобно читать построчно;
- легко добавлять новые документы;
- подходит для ML pipeline;
- проще CSV, но гибче для текстов и метаданных.

Для коротких документов вида `title + text` чанкинг не нужен. Он понадобится позже, если в корпус войдут длинные README, статьи или документация.

Отдельно от корпуса готовятся два набора:

```text
train_pairs.jsonl   # большой обучающий набор, можно синтетический
eval_queries.jsonl  # маленький набор запросов для оценки
qrels.jsonl         # ручная разметка релевантности
```

Train и eval не должны пересекаться.

### Этап 3. Dense retrieval

После BM25 добавляется семантический поиск:

```text
document text -> embedding model -> vector
query -> embedding model -> vector
FAISS/Qdrant -> nearest neighbors
```

Первый вариант dense retrieval использует готовую модель без обучения. Это нужно, чтобы сравнить:

```text
BM25
vs
готовая embedding model
```

Если используется семейство `e5`, важно соблюдать формат входа:

```text
query: <текст запроса>
passage: <текст документа>
```

Без этих префиксов качество e5-моделей может заметно падать.

### Этап 4. Fine-tuning bi-encoder

После baseline и готовой embedding-модели добавляется обучение bi-encoder.

Перед обучением должен быть уже собран eval-набор. Иначе нельзя понять, помогло обучение или модель просто переобучилась под синтетический стиль запросов.

Формат данных:

```text
query
positive_document
negative_document
```

Или для `MultipleNegativesRankingLoss`:

```text
(query, positive_document)
```

Пример:

```text
query:
проект про поиск похожих документов

positive:
Hybrid semantic search over Russian text with BM25 and dense retrieval

negative:
Sentiment classification for product reviews
```

Особенно важны hard negatives:

```text
query:
поиск похожих проектов

hard negative:
поиск похожих изображений
```

Такой negative похож по словам, но не подходит по смыслу. Это помогает модели учиться точнее.

Подходящие loss-функции:

- `MultipleNegativesRankingLoss`;
- `TripletLoss`;
- `ContrastiveLoss`.

Для первой версии fine-tuning наиболее практичен `MultipleNegativesRankingLoss`.

Практичный способ получить данные:

```text
1. LLM генерирует несколько естественных запросов к каждому документу.
2. Пара query -> source_document считается positive.
3. BM25 достает похожие, но неправильные документы.
4. Эти документы используются как hard negatives.
5. Отдельный eval-набор из 50-100 запросов проверяется руками.
```

### Этап 5. Hybrid search

После BM25 и dense retrieval результаты объединяются:

```text
BM25 top-N + vector top-N -> Reciprocal Rank Fusion -> top candidates
```

Зачем hybrid search:

- BM25 хорошо находит точные совпадения;
- dense retrieval хорошо находит смысловые совпадения;
- вместе они обычно устойчивее, чем каждый подход отдельно.

Для первой версии лучше использовать Reciprocal Rank Fusion, а не нормализацию скорингов. Причина: BM25 score и cosine similarity находятся в разных шкалах, поэтому их прямое сложение или min-max normalization легко дает нестабильный результат.

### Этап 6. Reranker

Reranker применяется после быстрого поиска:

```text
query + candidate_document -> relevance_score
```

Схема:

```text
BM25 + dense retrieval -> top-50/top-100 candidates -> cross-encoder -> final top-10
```

Зачем:

- bi-encoder быстрый, но менее точный;
- cross-encoder медленный, но точнее оценивает пару query/document;
- reranker улучшает порядок финальной выдачи.

### Этап 7. Demo и API

После ядра поиска можно добавить:

- CLI для локальной проверки;
- FastAPI backend;
- простой веб-интерфейс;
- выдачу top-k результатов;
- объяснение результата: какие слова совпали, какие теги или темы повлияли;
- ссылки на источники.

## Метрики качества

Качество поиска нужно измерять, а не оценивать на глаз.

Eval-набор должен быть создан до fine-tuning и заморожен. Хороший минимум: 50-100 запросов, к каждому запросу пул кандидатов из нескольких систем, ручная разметка `rel = 0/1/2`.

Основные метрики:

- `Recall@K` - нашел ли поиск релевантный документ в top-K;
- `MRR` - насколько высоко находится первый релевантный результат;
- `nDCG@K` - насколько хорошо отсортирована выдача с учетом graded relevance;
- `Precision@K` - сколько релевантных документов среди top-K.

Сравнивать нужно несколько вариантов:

```text
BM25
готовая embedding model
fine-tuned bi-encoder
hybrid BM25 + dense retrieval
hybrid + reranker
```

Все варианты сравниваются на одних и тех же `eval_queries.jsonl` и `qrels.jsonl`, с одинаковым `K`. Иначе сравнение будет нечестным.

## Минимальный план реализации

Первая рабочая версия:

```text
1. Создать структуру проекта
2. Добавить data/documents.jsonl
3. Добавить небольшой eval_queries.jsonl и qrels.jsonl
4. Реализовать загрузку документов
5. Реализовать русский tokenizer/normalizer
6. Реализовать BM25 search
7. Добавить CLI-команду
8. Посчитать первые метрики
```

Дальше:

```text
9. Добавить тесты
10. Добавить dense retrieval
11. Добавить FAISS/Qdrant index
12. Подготовить train_pairs.jsonl
13. Дообучить bi-encoder
14. Сравнить fine-tuned модель с baseline
15. Добавить hybrid search через RRF
16. Добавить reranker
17. Добавить API/demo
```

## Предлагаемая структура проекта

```text
RuSemanticSearch/
  data/
    documents.jsonl
    train_pairs.jsonl
    eval_queries.jsonl
    qrels.jsonl
  src/
    rusemanticsearch/
      __init__.py
      corpus.py
      tokenize.py
      bm25.py
      dense.py
      hybrid.py
      rerank.py
      evaluate.py
      cli.py
  tests/
    test_corpus.py
    test_tokenize.py
    test_bm25.py
  configs/
    baseline.yaml
    dense.yaml
    training.yaml
  scripts/
    build_bm25.py
    build_dense_index.py
    train_biencoder.py
    evaluate.py
  artifacts/
    indexes/
    models/
  pyproject.toml
  README.md
  DATA_PIPELINE.md
  CODE_QUALITY.md
  docs/
    DOCUMENT_SOURCES.md
```

## Что не входит в первую версию

На старте не делаем:

- собственный большой Transformer с нуля;
- генеративную модель;
- полноценный аналог Алисы;
- сложный frontend;
- production database;
- распределенный индекс;
- автоматический web crawler.

Эти вещи могут быть добавлены позже, но первая цель - рабочий и измеримый retrieval pipeline.

## Короткая формулировка проекта

RuSemanticSearch - это гибридная NLP-система для семантического поиска по русскоязычным текстам. Проект сравнивает BM25, готовые embedding-модели, дообученный bi-encoder и cross-encoder reranker. Основная ML-часть проекта - fine-tuning bi-encoder модели, которая учится сближать запросы с релевантными документами и отдалять нерелевантные.

## Текущий принцип разработки

Проект разрабатывается постепенно:

```text
сначала простой baseline
-> затем embeddings
-> затем обучение
-> затем reranking
-> затем demo/API
```

Каждый этап должен давать работающий результат, который можно запустить, проверить и сравнить с предыдущим.
