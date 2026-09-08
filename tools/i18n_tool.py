"""Translation maintenance for TALA. Three commands, one job each.

The problem this exists to solve: TALA ships in five languages but is still
being improved. Without tooling, every English edit silently invalidates up to
four translations and nobody can tell which. That is exactly how a multilingual
app rots into "the English one is right, the others are whatever they were".

    python tools/i18n_tool.py stamp    # draft -> catalog, recording English hashes
    python tools/i18n_tool.py check    # what drifted since it was translated?
    python tools/i18n_tool.py export   # reviewer workbook (.xlsx) for native speakers

Workflow
--------
1. Write a translation into ``locales/ui.<lang>.draft.json`` (plain key -> text)
   or ``locales/pages/<lang>/<page>.md``.
2. ``stamp`` copies it into the live catalog, tagging each unit with a hash of
   the *English it was translated from*.
3. Later, someone improves an English string. ``check`` reports precisely which
   units in which languages no longer match their source. Nothing else changed;
   the app keeps working, because a missing or drifted unit just renders the
   translation it has (and a missing one renders English).
4. ``export`` produces one workbook for native reviewers, with everything
   flagged as uncertain gathered on a single sheet up front.

Only ``export`` touches pandas/openpyxl, and both are already app dependencies.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.i18n import (  # noqa: E402
    DEFAULT_LANG, LANGS, LOCALES, TRANSLATED, _parse_blocks, source_hash,
)

NOTES_FILE = LOCALES / "review_notes.json"


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _english_ui() -> dict:
    return _load_json(LOCALES / f"ui.{DEFAULT_LANG}.json")


def _page_names() -> list[str]:
    d = LOCALES / "pages" / DEFAULT_LANG
    return sorted(p.stem for p in d.glob("*.md")) if d.exists() else []


def _english_page(page: str) -> dict:
    path = LOCALES / "pages" / DEFAULT_LANG / f"{page}.md"
    return _parse_blocks(path.read_text(encoding="utf-8")) if path.exists() else {}


def _translated_page(lang: str, page: str) -> dict:
    path = LOCALES / "pages" / lang / f"{page}.md"
    return _parse_blocks(path.read_text(encoding="utf-8")) if path.exists() else {}


# ---------------------------------------------------------------------------
# stamp
# ---------------------------------------------------------------------------
def cmd_stamp() -> int:
    """Promote every ``*.draft.json`` into its live catalog with source hashes."""
    english = _english_ui()
    if not english:
        print("! no English catalog found — nothing to stamp against")
        return 1

    total = 0
    for lang in TRANSLATED:
        draft = LOCALES / f"ui.{lang}.draft.json"
        if not draft.exists():
            continue
        data = _load_json(draft)
        stamped, unknown = {}, []
        for key, text in data.items():
            if key not in english:
                unknown.append(key)
                continue
            stamped[key] = {"t": text, "src": source_hash(english[key])}
        out = LOCALES / f"ui.{lang}.json"
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(stamped, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
        total += len(stamped)
        note = f"  ({len(unknown)} unknown key(s) skipped: {', '.join(unknown[:3])})" if unknown else ""
        print(f"  {lang}: {len(stamped):3} strings stamped{note}")

    print(f"\nstamped {total} unit(s) across {len(TRANSLATED)} language(s)")
    return 0


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------
def cmd_check() -> int:
    """Report units that drifted from, or are missing against, the English source."""
    english = _english_ui()
    rows: list[tuple[str, str, str, str]] = []   # lang, kind, key, status

    for lang in TRANSLATED:
        cat = _load_json(LOCALES / f"ui.{lang}.json")
        for key, en_text in english.items():
            entry = cat.get(key)
            if entry is None:
                rows.append((lang, "ui", key, "missing"))
            elif isinstance(entry, dict) and entry.get("src") != source_hash(en_text):
                rows.append((lang, "ui", key, "STALE"))
        for key in cat:
            if key not in english:
                rows.append((lang, "ui", key, "orphan"))

        for page in _page_names():
            en_blocks = _english_page(page)
            tr_blocks = _translated_page(lang, page)
            for key, en in en_blocks.items():
                entry = tr_blocks.get(key)
                if entry is None:
                    rows.append((lang, page, key, "missing"))
                elif entry.get("src") != source_hash(en["t"]):
                    rows.append((lang, page, key, "STALE"))

    stale = [r for r in rows if r[3] == "STALE"]
    missing = [r for r in rows if r[3] == "missing"]
    orphan = [r for r in rows if r[3] == "orphan"]

    if stale:
        print(f"\nSTALE — English changed after these were translated ({len(stale)}):")
        for lang, kind, key, _ in stale:
            print(f"  {lang:4} {kind:12} {key}")
    if missing:
        print(f"\nMISSING — falls back to English at runtime ({len(missing)}):")
        by_lang: dict[str, int] = {}
        for lang, _, _, _ in missing:
            by_lang[lang] = by_lang.get(lang, 0) + 1
        for lang, n in sorted(by_lang.items()):
            print(f"  {lang:4} {n} unit(s)")
    if orphan:
        print(f"\nORPHAN — translated but no longer in the English source ({len(orphan)}):")
        for lang, kind, key, _ in orphan:
            print(f"  {lang:4} {kind:12} {key}")

    if not rows:
        print("\nAll translations are current.")
    else:
        translated_units = len(english) * len(TRANSLATED)
        ok = translated_units - len(stale) - len(missing)
        print(f"\n{ok}/{translated_units} UI units current across "
              f"{len(TRANSLATED)} languages · {len(stale)} stale · {len(missing)} missing")
    return 1 if stale else 0


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------
def cmd_export(out: str = "TALA_translation_review.xlsx") -> int:
    """Build the consolidated reviewer workbook.

    Sheet 1 (``Priority Review``) is the point of the file: every unit flagged
    as uncertain, all four languages together, so a reviewer who speaks one of
    them can find their rows without opening four documents. The per-language
    sheets carry the full catalog behind it for context.

    A reviewer edits only the ``suggested_fix`` column; ``import`` reads that
    column back, so nobody needs to touch JSON or Python."""
    import pandas as pd

    english = _english_ui()
    notes = _load_json(NOTES_FILE)

    priority, per_lang = [], {}
    for lang in TRANSLATED:
        cat = _load_json(LOCALES / f"ui.{lang}.json")
        lang_rows = []
        for key, en_text in english.items():
            entry = cat.get(key)
            translated = entry.get("t") if isinstance(entry, dict) else entry
            note = notes.get(lang, {}).get(key, "")
            row = {
                "key": key,
                "english": en_text,
                "translation": translated or "(falls back to English)",
                "reviewer_note": note,
                "suggested_fix": "",
            }
            lang_rows.append(row)
            if note:
                priority.append({
                    "language": f'{LANGS[lang]["english"]} ({lang})',
                    **row,
                })

        for page in _page_names():
            en_blocks, tr_blocks = _english_page(page), _translated_page(lang, page)
            for key, en in en_blocks.items():
                entry = tr_blocks.get(key)
                note = notes.get(lang, {}).get(f"{page}:{key}", "")
                row = {
                    "key": f"{page}:{key}",
                    "english": en["t"],
                    "translation": (entry or {}).get("t") or "(falls back to English)",
                    "reviewer_note": note,
                    "suggested_fix": "",
                }
                lang_rows.append(row)
                if note:
                    priority.append({"language": f'{LANGS[lang]["english"]} ({lang})', **row})
        per_lang[lang] = pd.DataFrame(lang_rows)

    guide = pd.DataFrame({
        "How to use this workbook": [
            "1. Open the sheet for your language, or start with 'Priority Review'.",
            "2. 'Priority Review' lists only the items the translator was unsure "
            "about. If you have limited time, fix these first.",
            "3. Read the 'english' column for the intended meaning, then the "
            "'translation' column.",
            "4. If the translation is fine, leave 'suggested_fix' blank.",
            "5. If it is wrong or awkward, type the better wording in "
            "'suggested_fix'. Do not edit any other column.",
            "",
            "House style — please keep to it:",
            "· Everyday spoken register. Avoid deep, formal or literary words.",
            "· Technical terms stay in English: DBSCAN, cluster, sentiment, "
            "stopwords, corpus, token, dataset. Do not translate them.",
            "· Keep **bold**, *italic*, `code`, and {placeholders} exactly as they "
            "appear. {language}, {rows}, {title} are filled in by the app.",
            "· Keep emoji where they appear.",
            "· '(falls back to English)' means nothing was translated yet — the app "
            "shows English there. Write a translation if you can.",
        ]
    })

    path = ROOT / out
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        guide.to_excel(writer, sheet_name="Read me first", index=False)
        pri = pd.DataFrame(priority) if priority else pd.DataFrame(
            columns=["language", "key", "english", "translation",
                     "reviewer_note", "suggested_fix"])
        pri.to_excel(writer, sheet_name="Priority Review", index=False)
        for lang, df in per_lang.items():
            df.to_excel(writer, sheet_name=LANGS[lang]["english"][:31], index=False)

        widths = {"A": 26, "B": 60, "C": 60, "D": 46, "E": 46, "F": 30}
        for name, ws in writer.sheets.items():
            offset = 1 if name == "Priority Review" else 0
            for col, w in widths.items():
                idx = chr(ord(col) + offset)
                ws.column_dimensions[idx].width = w
            if name == "Priority Review":
                ws.column_dimensions["A"].width = 20
            if name == "Read me first":
                ws.column_dimensions["A"].width = 100
            ws.freeze_panes = "A2"

    print(f"wrote {path}")
    print(f"  {len(priority)} item(s) flagged for priority review")
    for lang, df in per_lang.items():
        print(f"  {LANGS[lang]['english']:12} {len(df):3} rows")
    return 0


def cmd_import(src: str = "TALA_translation_review.xlsx") -> int:
    """Read reviewer edits back out of the workbook into the draft files."""
    import pandas as pd

    path = ROOT / src
    if not path.exists():
        print(f"! {path} not found")
        return 1
    applied = 0
    for lang in TRANSLATED:
        sheet = LANGS[lang]["english"][:31]
        try:
            df = pd.read_excel(path, sheet_name=sheet)
        except Exception:
            continue
        fixes = df[df["suggested_fix"].notna() &
                   (df["suggested_fix"].astype(str).str.strip() != "")]
        if fixes.empty:
            continue
        draft_path = LOCALES / f"ui.{lang}.draft.json"
        draft = _load_json(draft_path)
        n = 0
        for _, r in fixes.iterrows():
            key = str(r["key"])
            if ":" in key:      # page block — reported, applied by hand
                print(f"  {lang}: page block '{key}' needs a manual edit "
                      f"in locales/pages/{lang}/")
                continue
            draft[key] = str(r["suggested_fix"]).strip()
            n += 1
        if n:
            with open(draft_path, "w", encoding="utf-8") as fh:
                json.dump(draft, fh, ensure_ascii=False, indent=2, sort_keys=True)
                fh.write("\n")
            print(f"  {lang}: {n} reviewer fix(es) applied to the draft")
            applied += n
    print(f"\n{applied} fix(es) applied — run 'stamp' to publish them")
    return 0


COMMANDS = {"stamp": cmd_stamp, "check": cmd_check,
            "export": cmd_export, "import": cmd_import}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd not in COMMANDS:
        print(f"usage: python tools/i18n_tool.py [{' | '.join(COMMANDS)}]")
        raise SystemExit(2)
    raise SystemExit(COMMANDS[cmd](*sys.argv[2:]))
