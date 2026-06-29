from rusemanticsearch.text.normalize import RussianTextNormalizer


def test_normalizer_tokenizes_mixed_text() -> None:
    normalizer = RussianTextNormalizer(lemmatize=False)

    assert normalizer.tokens("BM25 + поиск документов!") == ["bm25", "поиск", "документов"]


def test_normalizer_lemmatizes_russian_tokens() -> None:
    normalizer = RussianTextNormalizer(lemmatize=True)

    assert "документ" in normalizer.tokens("документов")
