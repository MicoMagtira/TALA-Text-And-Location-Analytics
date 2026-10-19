"""Guided tracks: which pages belong to a track, and what the trainee has finished.

TALA has two linear tracks (Text, 8 steps; Geo, 5 steps) that the progress strip,
the Back/Next footer and Home's "Continue" card all read from here, so the page
order lives in exactly one place. Session state holds only page *names*.

Per-page recipe (Tasks D and E follow this on every track page)::

    PAGE = "text_5_topics"
    ui.page_header(PAGE, "text")
    ui.learn_page(PAGE, code=...)

    @st.fragment
    def _controls_and_result():
        n = st.slider(...)
        with audio.result(tracks.SIGNATURE[PAGE], (n, ...)):
            res = nlp.lda_topics(...)
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

TRACKS: dict[str, list[str]] = {
    "text": ["text_1_data", "text_2_wordcloud", "text_3_sentiment", "text_4_ngrams",
             "text_5_topics", "text_6_keywords", "text_7_metrics", "text_8_themes"],
    "geo": ["geo_1_ingest", "geo_2_cluster", "geo_3_generalize", "geo_4_map", "geo_5_nlp"],
}

# Page -> the sound id its result plays (a key of the engine's ``S`` table).
SIGNATURE: dict[str, str] = {
    "text_1_data": "text1", "text_2_wordcloud": "text2", "text_3_sentiment": "text3",
    "text_4_ngrams": "text4", "text_5_topics": "text5", "text_6_keywords": "text6",
    "text_7_metrics": "text7", "text_8_themes": "text8",
    "geo_1_ingest": "geo1", "geo_2_cluster": "geo2", "geo_3_generalize": "geo3",
    "geo_4_map": "geo4", "geo_5_nlp": "geo5",
}

SS_DONE = "tala_done_pages"          # sorted list of page names (never a set: it is persisted)
SS_LAST_PAGE = "tala_last_page"
SS_CELEBRATED = "tala_celebrated"    # list of "text" / "geo" / "sky"
SS_JUST_COMPLETED = "_tala_just_completed"   # (page, track) of the last completion, for the card


def track_of(page: str) -> str | None:
    for name, pages in TRACKS.items():
        if page in pages:
            return name
    return None


def position(page: str) -> tuple[str, int, int] | None:
    """``(track, 1-based index, total)`` or None for Home and unknown pages."""
    track = track_of(page)
    if track is None:
        return None
    pages = TRACKS[track]
    return track, pages.index(page) + 1, len(pages)


def path_of(page: str) -> str:
    return f"views/{page}.py"


def neighbours(page: str) -> tuple[str | None, str | None]:
    """``(previous, next)`` page inside the track; None at either end."""
    track = track_of(page)
    if track is None:
        return None, None
    pages = TRACKS[track]
    i = pages.index(page)
    return (pages[i - 1] if i > 0 else None,
            pages[i + 1] if i + 1 < len(pages) else None)


def done_pages() -> set[str]:
    return set(st.session_state.get(SS_DONE, ()))


def track_complete(track: str) -> bool:
    return set(TRACKS[track]) <= done_pages()


def first_todo(track: str) -> str:
    """The first unfinished page of a track, or its first page when all are done."""
    done = done_pages()
    return next((p for p in TRACKS[track] if p not in done), TRACKS[track][0])


def area_for(url_path: str) -> str:
    """Which music area a page belongs to: ``'home'``, ``'text'`` or ``'geo'``."""
    if url_path.startswith("text_"):
        return "text"
    if url_path.startswith("geo_"):
        return "geo"
    return "home"


def mark_done(page: str) -> str | None:
    """Record a finished page. Only the first call per page does anything.

    Plays the ``step`` sound (delayed so it follows the page's own signature),
    and returns the track name if this call completed a track, else None.
    Completing a track plays ``trackDone`` once; completing the second track
    plays ``fullSky`` once *instead*, so two fanfares never overlap.
    """
    track = track_of(page)
    if track is None:
        return None
    done = done_pages()
    if page in done:
        return None
    done.add(page)
    st.session_state[SS_DONE] = sorted(done)
    audio.cue("step", delay_ms=700)

    if not track_complete(track):
        return None
    celebrated = list(st.session_state.get(SS_CELEBRATED, ()))
    if track in celebrated:
        return None
    celebrated.append(track)
    st.session_state[SS_JUST_COMPLETED] = (page, track)
    if all(track_complete(t) for t in TRACKS) and "sky" not in celebrated:
        celebrated.append("sky")
        audio.special("fullSky")
    else:
        audio.special("trackDone")
    st.session_state[SS_CELEBRATED] = celebrated
    return track
