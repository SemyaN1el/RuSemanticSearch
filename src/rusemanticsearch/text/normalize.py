from __future__ import annotations

import re
from typing import Any

TOKEN_RE = re.compile(r"[a-zа-яё0-9]+", re.IGNORECASE)
CYRILLIC_RE = re.compile(r"[а-яё]", re.IGNORECASE)


class RussianTextNormalizer:
    """Tokenize mixed Russian-English text and lemmatize Russian tokens."""

    def __init__(self, lemmatize: bool = True) -> None:
        self.lemmatize = lemmatize
        self._morph: Any | None = None
        self._token_cache: dict[str, str] = {}

    def tokens(self, text: str) -> list[str]:
        raw_tokens = TOKEN_RE.findall(text.lower())
        return [self.normalize_token(token) for token in raw_tokens]

    def normalize_token(self, token: str) -> str:
        token = token.lower()
        cached = self._token_cache.get(token)
        if cached is not None:
            return cached

        if not self.lemmatize or not CYRILLIC_RE.search(token):
            self._token_cache[token] = token
            return token

        morph = self._get_morph()
        parsed = morph.parse(token)
        if not parsed:
            self._token_cache[token] = token
            return token

        normal_form = str(parsed[0].normal_form)
        if len(self._token_cache) < 50_000:
            self._token_cache[token] = normal_form
        return normal_form

    def _get_morph(self) -> Any:
        if self._morph is None:
            import pymorphy3

            self._morph = pymorphy3.MorphAnalyzer()
        return self._morph
