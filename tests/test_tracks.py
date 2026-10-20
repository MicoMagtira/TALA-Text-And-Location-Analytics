"""Guards for the guided-track bookkeeping in core/tracks.py (no browser needed)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402
import streamlit as st  # noqa: E402

from core import tracks  # noqa: E402


@pytest.fixture
def sounds(monkeypatch):
    """A plain-dict session and a recorder in place of the audio cues."""
    monkeypatch.setattr(st, "session_state", {})
    played: list[tuple] = []
    monkeypatch.setattr(tracks.audio, "cue", lambda *a, **k: played.append(("cue", *a)))
    monkeypatch.setattr(tracks.audio, "special", lambda n: played.append(("special", n)))
    return played


def test_position_and_neighbours():
    assert tracks.position("p1_data") == ("where", 1, 3)
    assert tracks.position("p9_report") == ("what", 6, 6)
    assert tracks.position("home") is None
    assert tracks.neighbours("p1_data") == (None, "p2_textgps")
    assert tracks.neighbours("p3_places") == ("p2_textgps", None)
    assert tracks.neighbours("p4_apart") == (None, "p5_feel")
    assert tracks.neighbours("home") == (None, None)


def test_every_page_has_a_signature_and_a_view():
    root = Path(__file__).resolve().parent.parent
    engine = (root / "core" / "sound_engine.js").read_text(encoding="utf-8")
    assert len(tracks.ALL_PAGES) == 9
    for pages in tracks.CHAPTERS.values():
        for p in pages:
            assert p in tracks.SIGNATURE and p in tracks.NAV_EN
            assert f"  {tracks.SIGNATURE[p]}()" in engine
            assert (root / tracks.path_of(p)).exists()
    assert (root / "views" / "learn.py").exists()


def test_chapter_of():
    assert tracks.chapter_of("p5_feel") == "what"
    assert tracks.chapter_of("p2_textgps") == "where"
    assert tracks.chapter_of("learn") is None


def test_area_for():
    assert tracks.area_for("") == "home"
    assert tracks.area_for("learn") == "home"
    assert tracks.area_for("p2_textgps") == "geo"
    assert tracks.area_for("p5_feel") == "text"


def test_skipped_upstream():
    assert tracks.skipped_upstream("p1_data", set()) == []
    assert tracks.skipped_upstream("p3_places", set()) == ["p1_data", "p2_textgps"]
    assert tracks.skipped_upstream("p3_places", {"p1_data"}) == ["p2_textgps"]
    assert tracks.skipped_upstream("p5_feel", set()) == ["p1_data", "p2_textgps", "p3_places"]
    assert tracks.skipped_upstream("p5_feel", {"p1_data", "p2_textgps", "p3_places"}) == []
    # Chapter 2 is unordered: other "what" pages are never upstream.
    assert tracks.skipped_upstream("p9_report", set(tracks.CHAPTERS["where"])) == []
    assert tracks.skipped_upstream("home", set()) == []


def test_mark_done_is_idempotent(sounds):
    assert tracks.mark_done("p1_data") is None
    assert tracks.mark_done("p1_data") is None
    assert tracks.done_pages() == {"p1_data"}
    assert sounds == [("cue", "step")]
    assert st.session_state[tracks.SS_DONE] == ["p1_data"]


def test_chapter_celebrated_once_and_full_sky_once(sounds):
    for p in tracks.CHAPTERS["what"]:
        done = tracks.mark_done(p)
    assert done == "what"
    assert tracks.mark_done(tracks.CHAPTERS["what"][-1]) is None
    assert sounds.count(("special", "trackDone")) == 1
    assert ("special", "fullSky") not in sounds
    for p in tracks.CHAPTERS["where"]:
        done = tracks.mark_done(p)
    assert done == "where"
    assert sounds.count(("special", "fullSky")) == 1
    assert sounds.count(("special", "trackDone")) == 1
    assert sorted(st.session_state[tracks.SS_CELEBRATED]) == ["sky", "what", "where"]


def test_first_todo_and_done_count(sounds):
    assert tracks.first_todo("where") == "p1_data"
    tracks.mark_done("p1_data")
    assert tracks.first_todo("where") == "p2_textgps"
    assert tracks.chapter_done_count("where") == (1, 3)


def test_step_ranges():
    from core import ui
    assert ui._step_ranges(["p2_textgps", "p3_places"]) == "2–3"
    assert ui._step_ranges(["p1_data", "p3_places"]) == "1, 3"
