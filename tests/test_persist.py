"""Save/resume cookie: round trip, size cap, and rejection of bad data."""
from __future__ import annotations

import json
import base64

import pandas as pd
import pytest
import streamlit as st

from core import audio, data_loader as dl, i18n, persist, tracks, ui


@pytest.fixture(autouse=True)
def _fresh_state():
    st.session_state.clear()
    yield
    st.session_state.clear()


def _cookie(d: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")


def test_round_trip():
    i18n.set_lang("fil")
    st.session_state[audio.SS_MUSIC_VOLUME] = 40
    st.session_state[audio.SS_SFX_ON] = False
    st.session_state[ui.SS_CUSTOM_SW] = "clinic, ospital"
    st.session_state[tracks.SS_DONE] = ["p1_data", "p4_apart"]
    st.session_state[tracks.SS_LAST_PAGE] = "p4_apart"
    dl.ensure_loaded()
    st.session_state[dl.SS_CLUSTER_PARAMS] = (12000.0, 8)   # after: set_active resets the chain
    payload = persist.decode(persist.encode(persist.collect()))
    st.session_state.clear()
    persist.apply(payload)
    ss = st.session_state
    assert i18n.is_set() and i18n.current() == "fil"
    assert ss[audio.SS_MUSIC_VOLUME] == 40 and ss[audio.SS_SFX_ON] is False
    assert ss[ui.SS_CUSTOM_SW] == "clinic, ospital"
    assert ss[tracks.SS_DONE] == ["p1_data", "p4_apart"]
    assert ss[tracks.SS_LAST_PAGE] == "p4_apart"
    assert ss[dl.SS_CLUSTER_PARAMS] == (12000.0, 8)
    assert ss[dl.SS_SOURCE_KEY] == dl.BUNDLED_KEY


def test_size_cap_drops_custom_stopwords():
    payload = {"v": 1, "lang": "en", "custom_sw": "x" * 1000, "done": ["p1_data"] * 1}
    big = dict(payload, custom_sw="".join(chr(0x4E00 + i) for i in range(1000)))
    assert len(persist.encode(big)) <= persist.MAX_COOKIE_BYTES
    assert "custom_sw" not in persist.decode(persist.encode(big))


@pytest.mark.parametrize("value", [None, "", "!!!notbase64", _cookie({"v": 99}), _cookie([1, 2])])
def test_corrupt_cookie_ignored(value):
    assert persist.decode(value) is None


def test_bad_fields_ignored():
    persist.apply({"v": 1, "lang": "xx", "music_vol": 9999, "sfx_on": "yes", "style": "nope",
                   "pal": "nope", "cluster": ["a", 1], "done": ["../evil", "p1_data"],
                   "last": "nope"})
    ss = st.session_state
    assert not i18n.is_set()
    assert audio.SS_MUSIC_VOLUME not in ss and audio.SS_SFX_ON not in ss
    assert audio.SS_MUSIC_STYLE not in ss and ui.SS_PALETTE not in ss
    assert dl.SS_CLUSTER_PARAMS not in ss
    assert ss[tracks.SS_DONE] == ["p1_data"]
    assert tracks.SS_LAST_PAGE not in ss


def test_evicted_upload_falls_back_to_bundled():
    persist.apply({"v": 1, "src": "upload:deadbeef:gone.csv", "text": "x"})
    assert dl.SS_SOURCE_KEY not in st.session_state     # nothing half-applied
    dl.ensure_loaded()
    assert st.session_state[dl.SS_SOURCE_KEY] == dl.BUNDLED_KEY


def test_saved_upload_restores_dataset():
    df = pd.DataFrame({"comment": ["a"], "lng": [1.0], "latitude": [2.0]})
    key = dl.register_upload(df.to_csv(index=False).encode(), "t.csv")
    persist.apply({"v": 1, "src": key, "text": "comment", "lon": "lng", "lat": "bogus"})
    ss = st.session_state
    assert ss[dl.SS_SOURCE_KEY] == key and ss[dl.SS_TEXT_COL] == "comment"
    assert ss[dl.SS_LON_COL] == "lng" and ss[dl.SS_LAT_COL] is None


def test_no_dataframes_in_payload():
    dl.ensure_loaded()
    payload = persist.collect()
    json.dumps(payload)                                  # plain JSON only
    assert not any(isinstance(v, pd.DataFrame) for v in payload.values())


def test_old_journey_pages_are_migrated_away():
    """A cookie from the two-track release must not break or pollute the new journey."""
    persist.apply({"v": 1, "done": ["text_1_data", "geo_2_cluster", "p2_textgps"],
                   "last": "text_5_topics"})
    ss = st.session_state
    assert ss[tracks.SS_DONE] == ["p2_textgps"]
    assert tracks.SS_LAST_PAGE not in ss                 # unknown last page: Home

    st.session_state.clear()
    persist.apply({"v": 1, "done": ["text_1_data"], "last": "geo_4_map"})
    assert st.session_state[tracks.SS_DONE] == []
    assert tracks.SS_LAST_PAGE not in st.session_state
