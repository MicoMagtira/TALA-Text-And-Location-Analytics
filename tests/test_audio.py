"""Guards for TALA's browser-side synth sound layer.

Run with ``python tests/test_audio.py`` or ``python -m pytest tests/ -q``.
These verify the contract between the Python side and ``core/sound_engine.js``
without a browser; playback itself is left to the visitor's audio policy.
"""
from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import audio  # noqa: E402


ROOT = Path(__file__).resolve().parent.parent
ENGINE = ROOT / "core" / "sound_engine.js"

# The 48 rated soundboard cards minus 5 music-* and 5 scene-* cards.
SOUND_IDS = [
    "click", "select", "toggleOn", "toggleOff", "nav", "learnOpen", "learnClose",
    "slider", "copy", "upload", "download", "locked",
    "run", "ready", "cached", "step", "progress", "warn", "error",
    "twinkle", "language", "start", "bootReady", "trackDone", "fullSky",
    "text1", "text2", "text3", "text4", "text5", "text6", "text7", "text8",
    "geo1", "geo2", "geo3", "geo4", "geo5",
]
SONG_IDS = ["gabi", "buwan", "bituin", "harana", "kuliglig"]


class FakeState(dict):
    """Session state stand-in: a dict that also allows attribute access."""


def _patch_streamlit(monkeypatch_target=None):
    """Swap session_state and st.html for fakes; return (state, html_calls, undo)."""
    state = FakeState()
    calls: list[str] = []
    saved = (audio.st.session_state, audio.st.html)
    audio.st.session_state = state
    audio.st.html = lambda body, **kw: calls.append(body)

    def undo():
        audio.st.session_state, audio.st.html = saved

    return state, calls, undo


def _decode(body: str) -> str:
    return base64.b64decode(re.search(r'atob\("([A-Za-z0-9+/=]+)"\)', body).group(1)).decode("utf-8")


def test_engine_contains_every_approved_sound_and_song():
    source = ENGINE.read_text(encoding="utf-8")
    assert len(SOUND_IDS) == 38
    for sid in SOUND_IDS:
        assert re.search(rf"(^|\n)  {sid}\(", source), f"sound {sid} missing from sound_engine.js"
    for song in SONG_IDS:
        assert re.search(rf"(^|\n)  {song}: \{{", source), f"song {song} missing"
    assert "window.__talaSound" in source
    for fn in ("unlock", "setPrefs", "area", "play", "special", "bootTimeline", "startPressed"):
        assert re.search(rf"\b{fn}\(", source), fn


def test_engine_matches_the_soundboard_sources():
    """Sounds are copied verbatim: every S line of the board appears in the engine."""
    board = (ROOT / "docs" / "sound" / "soundboard.html").read_text(encoding="utf-8")
    engine = ENGINE.read_text(encoding="utf-8")
    s_block = board[board.index("const S = {"):board.index("/* ============================== MUSIC")]
    for line in s_block.splitlines():
        if line.strip():
            assert line in engine, f"soundboard line drifted: {line[:60]}"


def test_no_mp3_files_and_static_serving_off():
    assert not list(ROOT.rglob("*.mp3")) or all(".venv" in p.parts for p in ROOT.rglob("*.mp3"))
    assert not (ROOT / "static" / "audio").exists()
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert "enableStaticServing = false" in config
    source = (ROOT / "core" / "audio.py").read_text(encoding="utf-8")
    assert "AUDIO_URLS" not in source and "<audio" not in source
    assert "(0, eval)" not in source and "components.html" not in source


def test_engine_is_sent_once_per_session():
    state, calls, undo = _patch_streamlit()
    try:
        audio.mount("home")
        audio.mount("text")
        audio.mount("geo")
    finally:
        undo()
    assert len(calls) == 3
    first, second = _decode(calls[0]), _decode(calls[1])
    assert "window.__talaSound = api" in first
    assert 'area("home")' in first
    assert "window.__talaSound = api" not in second
    assert 'area("text")' in second and len(second) < 500
    assert state["_tala_engine_sent"] is True


def test_cue_is_unique_per_call_and_has_hidden_marker():
    state, calls, undo = _patch_streamlit()
    try:
        audio.cue("step", delay_ms=700)
        audio.cue("step", delay_ms=700)
        audio.special("trackDone")
    finally:
        undo()
    assert 'play("step", null, 700)' in _decode(calls[0])
    assert calls[0] != calls[1], "identical cues must differ so Streamlit re-executes them"
    assert 'class="tala-cue"' in calls[0]
    assert 'special("trackDone")' in _decode(calls[2])


def _run_result(monkeypatch_time, elapsed, params, state):
    cues: list[str] = []
    orig_cue, orig_state, orig_time = audio.cue, audio.st.session_state, audio.time.monotonic
    clock = iter([100.0, 100.0 + elapsed])
    audio.cue = lambda name, *a, **k: cues.append(name)
    audio.st.session_state = state
    audio.time.monotonic = lambda: next(clock)
    try:
        with audio.result("text5", params):
            pass
    finally:
        audio.cue, audio.st.session_state, audio.time.monotonic = orig_cue, orig_state, orig_time
    return cues


def test_result_plays_signature_cached_or_nothing():
    state = FakeState()
    assert _run_result(None, 1.2, (5, 1), state) == ["text5"]          # slow, first time
    assert _run_result(None, 1.2, (5, 1), state) == []                 # plain rerun
    assert _run_result(None, 0.05, (6, 1), state) == ["cached"]        # changed but fast
    assert _run_result(None, 0.05, (6, 1), state) == []


def test_result_propagates_exceptions_and_plays_nothing():
    state = FakeState()
    cues: list[str] = []
    orig_cue, orig_state = audio.cue, audio.st.session_state
    audio.cue = lambda name, *a, **k: cues.append(name)
    audio.st.session_state = state
    try:
        try:
            with audio.result("text5", (1,)):
                raise ValueError("boom")
        except ValueError:
            pass
        else:
            raise AssertionError("exception was swallowed")
    finally:
        audio.cue, audio.st.session_state = orig_cue, orig_state
    assert cues == [] and "text5" not in state.get("_tala_last_result", {})


def test_style_options_have_english_keys():
    import json

    en = json.loads((ROOT / "locales" / "ui.en.json").read_text(encoding="utf-8"))
    opts = audio.style_options()
    assert [v for v, _ in opts] == ["melody", "ambience"]
    for _, key in opts:
        assert key in en


def test_removed_ios_note_is_gone_from_every_locale():
    for path in (ROOT / "locales").glob("ui.*.json"):
        assert "audio.ios_volume_note" not in path.read_text(encoding="utf-8"), path.name


def _run_standalone() -> int:
    tests = [(n, v) for n, v in sorted(globals().items())
             if n.startswith("test_") and callable(v)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except Exception as exc:  # noqa: BLE001 - report all guard failures
            failed += 1
            print(f"  FAIL  {name}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} audio guards pass")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run_standalone())
