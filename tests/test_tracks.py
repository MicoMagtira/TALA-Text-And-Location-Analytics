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
    assert tracks.position("text_1_data") == ("text", 1, 8)
    assert tracks.position("geo_5_nlp") == ("geo", 5, 5)
    assert tracks.position("home") is None
    assert tracks.neighbours("text_1_data") == (None, "text_2_wordcloud")
    assert tracks.neighbours("text_8_themes") == ("text_7_metrics", None)
    assert tracks.neighbours("home") == (None, None)


def test_every_page_has_a_signature_and_a_view():
    root = Path(__file__).resolve().parent.parent
    for pages in tracks.TRACKS.values():
        for p in pages:
            assert p in tracks.SIGNATURE
            assert (root / tracks.path_of(p)).exists()


def test_area_for():
    assert tracks.area_for("") == "home"
    assert tracks.area_for("text_3_sentiment") == "text"
    assert tracks.area_for("geo_4_map") == "geo"


def test_mark_done_is_idempotent(sounds):
    assert tracks.mark_done("text_1_data") is None
    assert tracks.mark_done("text_1_data") is None
    assert tracks.done_pages() == {"text_1_data"}
    assert sounds == [("cue", "step")]
    assert st.session_state[tracks.SS_DONE] == ["text_1_data"]


def test_track_celebrated_once_and_full_sky_once(sounds):
    for p in tracks.TRACKS["text"]:
        done = tracks.mark_done(p)
    assert done == "text"
    assert tracks.mark_done(tracks.TRACKS["text"][-1]) is None
    assert sounds.count(("special", "trackDone")) == 1
    assert ("special", "fullSky") not in sounds
    for p in tracks.TRACKS["geo"]:
        done = tracks.mark_done(p)
    assert done == "geo"
    assert sounds.count(("special", "fullSky")) == 1
    assert sounds.count(("special", "trackDone")) == 1
    assert sorted(st.session_state[tracks.SS_CELEBRATED]) == ["geo", "sky", "text"]


def test_first_todo(sounds):
    assert tracks.first_todo("text") == "text_1_data"
    tracks.mark_done("text_1_data")
    assert tracks.first_todo("text") == "text_2_wordcloud"
