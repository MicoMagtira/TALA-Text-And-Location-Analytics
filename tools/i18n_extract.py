"""One-shot extraction of the Learn essays from views/ into locales/pages/en/.

Run once to move the long-form teaching prose out of the Python files and into
the translation catalogs. Kept in the repo afterwards as the record of how the
English source was produced — and because it is the safe way to re-do the split
if the block boundaries ever need revisiting.

Reads each ``ui.learn(title, body, code=...)`` call via the AST rather than by
regex, so the implicit string concatenation the views use folds correctly and
nothing is lost or reflowed in transcription. The ``code=`` argument is
deliberately NOT extracted: code snippets stay English in every language.

Body paragraphs become one block each. That granularity is the point — editing
a single paragraph of an essay later marks one block stale in four languages
instead of invalidating the whole page.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIEWS = ROOT / "views"
OUT = ROOT / "locales" / "pages" / "en"


def extract(path: Path) -> tuple[str, list[str]] | None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and getattr(node.func, "attr", None) == "learn"
                and len(node.args) >= 2
                and all(isinstance(a, ast.Constant) for a in node.args[:2])):
            title = node.args[0].value
            body = node.args[1].value
            paras = [p.strip() for p in body.split("\n\n") if p.strip()]
            return title, paras
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    total_blocks = total_words = 0
    for path in sorted(VIEWS.glob("*.py")):
        got = extract(path)
        if not got:
            print(f"  {path.stem:22} no learn() call — skipped")
            continue
        title, paras = got
        lines = [f"--- key: title\n{title}\n"]
        for i, para in enumerate(paras, 1):
            lines.append(f"--- key: p{i}\n{para}\n")
        (OUT / f"{path.stem}.md").write_text("\n".join(lines), encoding="utf-8")
        words = len(title.split()) + sum(len(p.split()) for p in paras)
        total_blocks += 1 + len(paras)
        total_words += words
        print(f"  {path.stem:22} {len(paras) + 1:2} blocks, {words:4} words")
    print(f"\n{total_blocks} blocks, {total_words} words extracted to locales/pages/en/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
