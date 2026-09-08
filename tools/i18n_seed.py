"""Write translated Learn essays into locales/pages/<lang>/ with source stamps.

Translations arrive as a plain ``{page: {block: text}}`` mapping — the shape a
person actually writes in — and this turns them into the block-markdown the app
reads, stamping each block with the hash of the English it was translated from
so ``i18n_tool.py check`` can report drift later.

Blocks absent from the mapping are simply not written, which leaves them falling
back to English at runtime. That is the intended way to ship a partially
translated page rather than a reason to block on completeness.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.i18n import LOCALES, _parse_blocks, source_hash  # noqa: E402


def english(page: str) -> dict:
    path = LOCALES / "pages" / "en" / f"{page}.md"
    return _parse_blocks(path.read_text(encoding="utf-8")) if path.exists() else {}


def write(lang: str, data: dict[str, dict[str, str]], quiet: bool = False) -> int:
    """Emit one .md per page for ``lang``. Returns the number of blocks written."""
    out_dir = LOCALES / "pages" / lang
    out_dir.mkdir(parents=True, exist_ok=True)
    total = 0
    for page, blocks in data.items():
        en = english(page)
        missing = [k for k in blocks if k not in en]
        if missing:
            print(f"  ! {lang}/{page}: unknown block(s) {missing} — skipped")
        chunks = []
        for key in en:                      # English order is the canonical order
            if key not in blocks:
                continue
            text = blocks[key].strip()
            if not text:
                continue
            chunks.append(f"--- key: {key} src: {source_hash(en[key]['t'])}\n{text}\n")
            total += 1
        (out_dir / f"{page}.md").write_text("\n".join(chunks), encoding="utf-8")
        if not quiet:
            covered = sum(1 for k in en if k in blocks)
            print(f"  {lang}/{page:20} {covered}/{len(en)} blocks")
    return total
