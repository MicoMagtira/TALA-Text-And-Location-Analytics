"""Text cleaning, tokenization and stopword handling.

Ports the preprocessing from NLP.ipynb: lowercase; strip URLs, @mentions,
#hashtags, digits, punctuation (Unicode-aware), underscores and extra
whitespace; whitespace tokenization; stopword removal against
English ∪ Tagalog (bundled lists) ∪ custom user stopwords. Taglish
content is supported by unioning the Filipino stopwords.

The English list is the same 318 words as ``sklearn.feature_extraction.text.
ENGLISH_STOP_WORDS``, shipped as data/english_stop_words.txt. sklearn defines it
as a static frozenset, so vendoring it is lossless and keeps sklearn off the
base import path.
"""
from __future__ import annotations

import re
from functools import lru_cache

from .data_loader import load_english_stopwords, load_tagalog_stopwords

_URL = re.compile(r"http\S+|www\.\S+")
_MENTION = re.compile(r"[@#]\w+")
_NON_WORD = re.compile(r"[^\w\s]", re.UNICODE)
_DIGITS = re.compile(r"\d+")
_UNDERSCORE = re.compile(r"_+")
_WS = re.compile(r"\s+")

MIN_TOKEN_LEN = 3


@lru_cache(maxsize=1)
def english_stopwords() -> frozenset[str]:
    return frozenset(load_english_stopwords())


@lru_cache(maxsize=1)
def base_stopwords() -> frozenset[str]:
    return english_stopwords() | frozenset(load_tagalog_stopwords())


def build_stopwords(custom: str | None = None, use_tagalog: bool = True) -> set[str]:
    words: set[str] = set(english_stopwords())
    if use_tagalog:
        words |= set(load_tagalog_stopwords())
    if custom:
        parts = re.split(r"[,\n]+", custom)
        words |= {w.strip().lower() for w in parts if w.strip()}
    return words


def clean_text(text: str) -> str:
    """Lowercase + strip URLs/mentions/hashtags/digits/punctuation/whitespace."""
    text = str(text).lower()
    text = _URL.sub(" ", text)
    text = _MENTION.sub(" ", text)
    text = _NON_WORD.sub(" ", text)
    text = _DIGITS.sub(" ", text)
    text = _UNDERSCORE.sub(" ", text)
    return _WS.sub(" ", text).strip()


def tokenize(text: str, stopwords: set[str] | None = None,
             min_len: int = MIN_TOKEN_LEN) -> list[str]:
    stopwords = stopwords if stopwords is not None else base_stopwords()
    return [t for t in clean_text(text).split()
            if len(t) > min_len - 1 and t not in stopwords]


def clean_corpus(texts, stopwords: set[str] | None = None) -> list[str]:
    """Return a list of cleaned, stopword-filtered joined strings (one per doc)."""
    stopwords = stopwords if stopwords is not None else base_stopwords()
    return [" ".join(tokenize(t, stopwords)) for t in texts]


def all_tokens(texts, stopwords: set[str] | None = None) -> list[str]:
    """Flatten a corpus into a single token list (for frequency counts)."""
    stopwords = stopwords if stopwords is not None else base_stopwords()
    out: list[str] = []
    for t in texts:
        out.extend(tokenize(t, stopwords))
    return out
