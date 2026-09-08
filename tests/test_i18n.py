"""Guards for the localization layer.

Two things have to stay true for five languages to be maintainable from one
codebase, and both are easy to break without noticing:

1. **The gate actually gates.** No page may render before a language is chosen,
   or a trainee sees the UI change language underneath them mid-load.
2. **Language never fragments the analysis caches.** Localization is a render
   concern. If a language code ever leaks into a ``geo.*_for()`` or
   ``nlp._lda_fit`` cache key, the cohort stops sharing layers and the ~1 GB
   container budget that the whole app is built around evaporates.

Run with either::

    python -m pytest tests/ -q
    python tests/test_i18n.py
"""
from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import i18n  # noqa: E402

LOCALES = Path(__file__).resolve().parent.parent / "locales"


# ---------------------------------------------------------------------------
# 1. Catalog integrity
# ---------------------------------------------------------------------------
def _catalog(lang: str) -> dict:
    path = LOCALES / f"ui.{lang}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def test_every_language_has_a_catalog():
    for lang in i18n.TRANSLATED:
        assert _catalog(lang), f"no catalog for {lang}"


def test_no_orphan_keys():
    """A translated key with no English source is dead weight and never renders."""
    english = _catalog("en")
    for lang in i18n.TRANSLATED:
        orphans = [k for k in _catalog(lang) if k not in english]
        assert not orphans, f"{lang} translates keys absent from English: {orphans}"


def test_placeholders_survive_translation():
    """{language}, {rows}, {title} are filled by the app — dropping one in a
    translation raises at render time, in that language only, which is exactly
    the bug that reaches production unnoticed."""
    import re

    english = _catalog("en")
    fields = lambda s: set(re.findall(r"\{(\w+)\}", s))
    for lang in i18n.TRANSLATED:
        for key, entry in _catalog(lang).items():
            text = entry["t"] if isinstance(entry, dict) else entry
            expected = fields(english.get(key, ""))
            assert fields(text) == expected, (
                f"{lang}:{key} placeholders {fields(text)} != English {expected}"
            )


def test_translations_record_their_source_hash():
    """Without src hashes, nothing can report what went stale after an edit."""
    for lang in i18n.TRANSLATED:
        for key, entry in _catalog(lang).items():
            assert isinstance(entry, dict) and entry.get("src"), (
                f"{lang}:{key} has no src hash — run tools/i18n_tool.py stamp"
            )


def test_missing_translation_falls_back_to_english():
    """The property that lets English ship ahead of its translations."""
    english = _catalog("en")
    fil = _catalog("fil")
    untranslated = [k for k in english if k not in fil]
    assert untranslated, "expected some keys to be intentionally English-only"
    for key in untranslated:
        assert i18n.t(key) == english[key]


# ---------------------------------------------------------------------------
# 2. Localization must not touch the analysis caches
# ---------------------------------------------------------------------------
def test_language_is_not_a_cache_key_anywhere():
    """The memory model depends on a whole cohort sharing one copy of each
    derived layer regardless of the language they read it in."""
    from core import geo, nlp

    cached = [("geo", n, f) for n, f in vars(geo).items() if callable(f)]
    cached += [("nlp", n, f) for n, f in vars(nlp).items() if callable(f)]
    for mod, name, fn in cached:
        try:
            params = set(inspect.signature(fn).parameters)
        except (TypeError, ValueError):
            continue
        leaked = params & {"lang", "language", "locale"}
        assert not leaked, (
            f"{mod}.{name} takes {leaked} — localization must not fragment "
            f"the shared analysis caches"
        )


def test_i18n_does_not_import_heavy_modules():
    """i18n is on the base import path, so it must stay as cheap as ui/viz."""
    source = (Path(__file__).resolve().parent.parent / "core" / "i18n.py").read_text(
        encoding="utf-8")
    for heavy in ("import pandas", "import numpy", "import sklearn",
                  "import geopandas", "import matplotlib"):
        assert heavy not in source, f"core/i18n.py must not {heavy}"


def _run_standalone() -> int:
    tests = [(n, v) for n, v in sorted(globals().items())
             if n.startswith("test_") and callable(v)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"  FAIL  {name}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} i18n guards pass")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_standalone())
