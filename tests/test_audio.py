"""Guards for TALA's optional browser-side audio layer.

Run with ``python tests/test_audio.py`` or ``python -m pytest tests/ -q``.
These tests verify the production-asset contract without requiring a browser;
browser playback itself is intentionally delegated to the user's audio policy.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import audio  # noqa: E402


ROOT = Path(__file__).resolve().parent.parent


def test_runtime_audio_assets_exist_and_are_compact():
    """Runtime sound must be present without shipping the 170 MB WAV master."""
    expected = {
        "music": ("tala-background.mp3", 10 * 1024 * 1024),
        "start": ("tala-start.mp3", 512 * 1024),
        "click": ("tala-click.mp3", 512 * 1024),
    }
    for name, (filename, maximum) in expected.items():
        path = ROOT / "static" / "audio" / filename
        assert path.is_file(), f"missing runtime {name} asset: {path}"
        assert 0 < path.stat().st_size <= maximum, (
            f"{filename} is unexpectedly large; use an optimized runtime asset"
        )


def test_audio_manager_uses_static_urls_not_embedded_bytes():
    """Sound must stream separately from Streamlit rerun payloads."""
    assert all(url.startswith("/app/static/audio/") for url in audio.AUDIO_URLS.values())
    source = (ROOT / "core" / "audio.py").read_text(encoding="utf-8")
    assert "components.html" in source
    assert "clickHandler" in source
    assert "startLabels" in source
    assert "startMusicOnInteraction" in source
    assert "playStartThenMusic" in source
    assert "waitingForStartCue" in source
    assert "start.onended" in source
    assert "setAttribute('onended'" in source
    assert "manager.music.volume = 0" in source
    assert 'a[href]' in source
    assert 'summary' in source
    assert '[role="switch"]' in source
    assert '[role="radio"]' in source
    assert '[role="checkbox"]' in source
    assert '[data-baseweb="checkbox"]' in source
    assert "open(" not in source, "audio manager must not load sound bytes into Python"


def test_gate_can_start_music_before_start_button():
    source = (ROOT / "core" / "gate.py").read_text(encoding="utf-8")
    assert "play_music=True" in source
    assert "start_music_on_interaction=True" in source


def test_static_audio_serving_is_enabled():
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert "enableStaticServing = true" in config


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
