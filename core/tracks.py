"""Guided journey: two chapters, nine steps, and what the trainee has finished.

TALA is place-first (docs/PLAN_PANEL.md). Chapter 1, **Lugar** ("Where are
people?"), has three steps that run in order: Data, Text vs GPS, Places. Chapter 2,
**Salita** ("What is each place saying?"), has six steps that can be opened in any
order; if Chapter 1 was never visited TALA runs it with defaults and the page says
so (:func:`skipped_upstream` feeds ``ui.auto_ran``). The sidebar, the progress
strip, the Back/Next footer and Home's "Continue" card all read the page order
from here, so it lives in exactly one place. Session state holds only page *names*.

Per-page recipe (every journey page follows this)::

    PAGE = "p5_feel"
    ui.page_header(PAGE, "what")          # section is the chapter key
    ui.auto_ran(PAGE)                     # only when earlier steps matter
    ui.learn_page(PAGE, code=...)

    @st.fragment
    def _controls_and_result():
        n = st.slider(...)
        with audio.result(tracks.SIGNATURE[PAGE], (n, ...)):
            res = compare.place_sentiment(...)
        ... render charts ...

    _controls_and_result()
    ui.page_done(PAGE)
    ui.track_footer(PAGE)

Use a fragment only when its widgets affect nothing outside it. Use ``ui.warn`` /
``ui.error`` instead of ``st.warning`` / ``st.error`` (they play a sound), and
``ui.locked(...)`` for a page that genuinely cannot run. There is no "next page"
nudge to write: the footer is it.

"""
from __future__ import annotations

import streamlit as st

from . import audio


CHAPTERS: dict[str, list[str]] = {
    "where": ["p1_data", "p2_textgps", "p3_places"],
    "what": ["p4_apart", "p5_feel", "p6_aspects", "p7_themes", "p8_hotspots", "p9_report"],
}

# Chapter 1 must be walked in order (each step feeds the next); chapter 2 is free.
ORDERED: dict[str, bool] = {"where": True, "what": False}

# Proper names, deliberately not translated (shown as small gold labels).
NAMES: dict[str, str] = {"where": "Lugar", "what": "Salita"}

# Page -> the sound id its result plays (a key of the engine's ``S`` table).
# Reuses existing cues: the journey adds no new sounds.
SIGNATURE: dict[str, str] = {
    "p1_data": "text1", "p2_textgps": "geo1", "p3_places": "geo2",
    "p4_apart": "text4", "p5_feel": "text3", "p6_aspects": "text6",
    "p7_themes": "text8", "p8_hotspots": "geo3", "p9_report": "geo4",
}

# English fallbacks for page names, used until the catalog carries ``<page>.nav``.
NAV_EN: dict[str, str] = {
    "p1_data": "Data", "p2_textgps": "Text vs GPS", "p3_places": "Places",
    "p4_apart": "What sets a place apart", "p5_feel": "How each place feels",
    "p6_aspects": "What they praise or fault", "p7_themes": "What they talk about",
    "p8_hotspots": "Where complaints cluster", "p9_report": "Place report",
}

ALL_PAGES: list[str] = [p for pages in CHAPTERS.values() for p in pages]

SS_DONE = "tala_done_pages"          # sorted list of page names (never a set: it is persisted)
SS_LAST_PAGE = "tala_last_page"
SS_CELEBRATED = "tala_celebrated"    # list of "where" / "what" / "sky"
SS_JUST_COMPLETED = "_tala_just_completed"   # (page, chapter) of the last completion, for the card


def chapter_of(page: str) -> str | None:
    for name, pages in CHAPTERS.items():
        if page in pages:
            return name
    return None


def other_chapter(chapter: str) -> str:
    return "what" if chapter == "where" else "where"


def step_number(page: str) -> int | None:
    """The page's 1-based number across the whole journey (1..9), or None."""
    return ALL_PAGES.index(page) + 1 if page in ALL_PAGES else None


def position(page: str) -> tuple[str, int, int] | None:
    """``(chapter, 1-based index inside it, chapter total)`` or None for Home and unknown pages."""
    chapter = chapter_of(page)
    if chapter is None:
        return None
    pages = CHAPTERS[chapter]
    return chapter, pages.index(page) + 1, len(pages)


def path_of(page: str) -> str:
    return f"views/{page}.py"


def neighbours(page: str) -> tuple[str | None, str | None]:
    """``(previous, next)`` page inside the chapter; None at either end."""
    chapter = chapter_of(page)
    if chapter is None:
        return None, None
    pages = CHAPTERS[chapter]
    i = pages.index(page)
    return (pages[i - 1] if i > 0 else None,
            pages[i + 1] if i + 1 < len(pages) else None)


def done_pages() -> set[str]:
    return set(st.session_state.get(SS_DONE, ()))


def chapter_done_count(chapter: str) -> tuple[int, int]:
    """``(finished steps, total steps)`` for a chapter, for Home's cards."""
    pages = CHAPTERS[chapter]
    done = done_pages()
    return sum(p in done for p in pages), len(pages)


def track_complete(chapter: str) -> bool:
    return set(CHAPTERS[chapter]) <= done_pages()


def first_todo(chapter: str) -> str:
    """The first unfinished page of a chapter, or its first page when all are done."""
    done = done_pages()
    return next((p for p in CHAPTERS[chapter] if p not in done), CHAPTERS[chapter][0])


def skipped_upstream(page: str, done: set[str] | None = None) -> list[str]:
    """Earlier steps this page depends on that were never opened, in journey order.

    A "what" page depends on all of chapter 1; an ordered "where" page on the
    "where" pages before it. Empty for Home and for unordered pages with no
    upstream. The page itself runs regardless: this only feeds the
    "TALA ran them with default settings" line."""
    chapter = chapter_of(page)
    if chapter is None:
        return []
    done = done_pages() if done is None else done
    if chapter == "what":
        upstream = CHAPTERS["where"]
    elif ORDERED[chapter]:
        upstream = CHAPTERS[chapter][:CHAPTERS[chapter].index(page)]
    else:
        upstream = []
    return [p for p in upstream if p not in done]


def area_for(url_path: str) -> str:
    """Which music area a page belongs to: ``'home'``, ``'text'`` or ``'geo'``.

    Chapter 1 (where) plays the ``geo`` music, chapter 2 (what) the ``text``
    music; Home and How TALA works keep the Home music."""
    chapter = chapter_of(url_path)
    if chapter == "where":
        return "geo"
    if chapter == "what":
        return "text"
    return "home"


def mark_done(page: str) -> str | None:
    """Record a finished page. Only the first call per page does anything.

    Plays the ``step`` sound (delayed so it follows the page's own signature),
    and returns the chapter name if this call completed a chapter, else None.
    Completing a chapter plays ``trackDone`` once; completing the second chapter
    plays ``fullSky`` once *instead*, so two fanfares never overlap.
    """
    chapter = chapter_of(page)
    if chapter is None:
        return None
    done = done_pages()
    if page in done:
        return None
    done.add(page)
    st.session_state[SS_DONE] = sorted(done)
    audio.cue("step", delay_ms=700)

    if not track_complete(chapter):
        return None
    celebrated = list(st.session_state.get(SS_CELEBRATED, ()))
    if chapter in celebrated:
        return None
    celebrated.append(chapter)
    st.session_state[SS_JUST_COMPLETED] = (page, chapter)
    if all(track_complete(c) for c in CHAPTERS) and "sky" not in celebrated:
        celebrated.append("sky")
        audio.special("fullSky")
    else:
        audio.special("trackDone")
    st.session_state[SS_CELEBRATED] = celebrated
    return chapter
