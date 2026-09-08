"""Localization for TALA — one codebase, five languages.

TALA is training material for a Philippine audience, so the app ships in
English, Filipino, Cebuano, Ilocano and Hiligaynon. The obvious implementation
— five copies of ``views/`` — was rejected on sight: this app is still being
iterated on, and a fix to one page would then have to be re-applied four more
times by hand, forever. Instead there is exactly one set of views, and the
prose they render is data.

The contract
------------
* **English is canonical.** Every key exists in English first; the other four
  are translations *of a keyed unit*, never independent documents.
* **Missing translations fall back to English**, silently and per unit. That is
  what lets an English improvement ship today and be translated next week
  without breaking the other four languages or blocking the edit.
* **Every translated unit records the hash of the English it came from**
  (``src:``). When the English moves, ``tools/i18n_check.py`` reports exactly
  which units drifted, so nobody has to remember what went stale. A drifted
  unit still renders its translation — silently reverting a trainee to English
  mid-workshop because someone fixed a typo would be the worse failure.
* **Granularity is the paragraph**, not the page. Editing one paragraph of a
  Learn essay invalidates one block in four languages, not four whole essays.

Two stores, because the two kinds of text want different editors:

``locales/ui.<lang>.json``
    Short strings — buttons, labels, captions, spinner and error messages.
    Flat key -> text.

``locales/pages/<lang>/<page>.md``
    Long-form Learn prose. Markdown with ``--- key: <name>`` block separators,
    so it stays readable and diffable instead of becoming a wall of escaped
    newlines inside JSON.

Register
--------
Translations use everyday spoken register, not formal or literary vocabulary,
and technical terms stay in English inline (DBSCAN, cluster, sentiment,
stopwords, corpus). That is deliberate and it is how the audience actually
speaks: a coined Tagalog equivalent for "clustering" is harder for a Filipino
data-science trainee to read than the English word they already use, and it
would leave them unable to follow the English documentation this course is
preparing them for.

Cost note
---------
Catalogs are small (tens of KB) and load behind ``cache_resource``, so a whole
cohort shares one copy per language and only the languages actually in use are
resident. Critically, **the active language never enters an analysis cache
key**: ``geo.points_for``, ``geo.clusters_for`` and ``nlp._lda_fit`` stay
language-agnostic, so a Cebuano trainee and a Tagalog trainee still share the
same 14 MB clustered layer. Localization is a render-layer concern only.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import streamlit as st

LOCALES = Path(__file__).resolve().parent.parent / "locales"

DEFAULT_LANG = "en"
SS_LANG = "tala_lang"
SS_PICK = "tala_lang_pick"   # highlighted-but-not-yet-started choice on the gate

# Ordered as shown on the language gate. ``endonym`` is what the language calls
# itself — a picker labelling Cebuano as "Cebuano" rather than "Bisaya" reads
# like a form, not like an invitation. ``hello`` is the native greeting printed
# on each card, so the choice is recognisable before any UI text has changed.
LANGS: dict[str, dict[str, str]] = {
    "en":  {"endonym": "English",  "english": "English",    "hello": "Hello"},
    "fil": {"endonym": "Filipino", "english": "Filipino",   "hello": "Kumusta"},
    "ceb": {"endonym": "Bisaya",   "english": "Cebuano",    "hello": "Kumusta"},
    "ilo": {"endonym": "Ilokano",  "english": "Ilocano",    "hello": "Kumusta"},
    "hil": {"endonym": "Ilonggo",  "english": "Hiligaynon", "hello": "Kamusta"},
}

TRANSLATED = [c for c in LANGS if c != DEFAULT_LANG]


# ---------------------------------------------------------------------------
# Source hashing (staleness tracking)
# ---------------------------------------------------------------------------
def source_hash(text: str) -> str:
    """Short digest of an English unit, stored alongside its translations.

    Whitespace-normalised, so a rewrap of the English source does not falsely
    mark four translations stale."""
    normalized = " ".join(str(text).split())
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:10]


# ---------------------------------------------------------------------------
# Catalog loading
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _ui_catalog(lang: str) -> dict:
    """Short-string catalog for one language. Shared across the cohort."""
    path = LOCALES / f"ui.{lang}.json"
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


_BLOCK_RE = re.compile(r"^---\s*key:\s*(\S+)(?:\s+src:\s*(\S+))?\s*$", re.M)


def _parse_blocks(text: str) -> dict[str, dict[str, str]]:
    """Split a block-markdown file into ``{key: {"t": body, "src": hash}}``."""
    out: dict[str, dict[str, str]] = {}
    marks = list(_BLOCK_RE.finditer(text))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out[m.group(1)] = {"t": text[m.end():end].strip(), "src": m.group(2) or ""}
    return out


@st.cache_resource(show_spinner=False)
def _page_catalog(lang: str, page: str) -> dict:
    """Long-form Learn prose for one page in one language."""
    path = LOCALES / "pages" / lang / f"{page}.md"
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return _parse_blocks(fh.read())
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Active language
# ---------------------------------------------------------------------------
def current() -> str:
    return st.session_state.get(SS_LANG, DEFAULT_LANG)


def is_set() -> bool:
    """Has this session chosen a language? Gates the app behind the splash."""
    return SS_LANG in st.session_state


def set_lang(code: str) -> None:
    if code in LANGS:
        st.session_state[SS_LANG] = code


def label(code: str) -> str:
    """'Filipino' / 'Bisaya (Cebuano)' — the sidebar switcher's option text."""
    meta = LANGS[code]
    if meta["endonym"] == meta["english"]:
        return meta["endonym"]
    return f'{meta["endonym"]} ({meta["english"]})'


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------
def t(key: str, **fmt) -> str:
    """A short UI string in the active language, falling back to English.

    ``**fmt`` is applied with ``str.format`` so a translation can reorder its
    placeholders — word order differs across these five languages, and building
    a sentence by concatenation would not survive translation."""
    value = None
    lang = current()
    if lang != DEFAULT_LANG:
        entry = _ui_catalog(lang).get(key)
        if isinstance(entry, dict):
            value = entry.get("t")
        elif isinstance(entry, str):
            value = entry
    if not value:
        entry = _ui_catalog(DEFAULT_LANG).get(key)
        value = entry if isinstance(entry, str) else (entry or {}).get("t")
    if not value:
        return key          # loud but harmless: an unkeyed string shows its key
    try:
        return value.format(**fmt) if fmt else value
    except (KeyError, IndexError):
        return value


def tm(page: str, key: str) -> str:
    """A long-form Learn block in the active language, falling back to English."""
    lang = current()
    if lang != DEFAULT_LANG:
        entry = _page_catalog(lang, page).get(key)
        if entry and entry.get("t"):
            return entry["t"]
    entry = _page_catalog(DEFAULT_LANG, page).get(key)
    return entry["t"] if entry else ""


def page_blocks(page: str) -> list[str]:
    """Block keys for a page, in English source order."""
    return list(_page_catalog(DEFAULT_LANG, page))


# ---------------------------------------------------------------------------
# Localized spinners for cached work
# ---------------------------------------------------------------------------
def localized_spinner(key: str):
    """Wrap a cached function so its progress message follows the reader.

    Streamlit's own ``show_spinner="…"`` takes a literal evaluated when the
    module is imported — long before a language has been chosen — so every
    message would be frozen in English for every trainee. Resolving the message
    inside the call instead means the same cached function reports its work in
    whatever language the current session is reading.

    Applied *above* ``@st.cache_*`` so the spinner wraps the cache lookup::

        @i18n.localized_spinner("spin.dbscan")
        @st.cache_resource(show_spinner=False, ...)
        def clusters_for(...):

    The trade-off is that the spinner also flashes on a cache hit, where
    Streamlit's built-in one would not. On these functions a hit returns in
    microseconds, so it is invisible — and it never costs a recomputation.
    """
    import functools

    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with st.spinner(t(key)):
                return fn(*args, **kwargs)
        return wrapper
    return decorate
