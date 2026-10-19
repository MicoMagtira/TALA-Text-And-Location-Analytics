"""Guards for the boot splash: START button, client-only reveal, cookie skip."""
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import splash


def test_boot_hides_chrome_until_start_is_pressed():
    source = (ROOT / "core" / "splash.py").read_text(encoding="utf-8")
    assert "tala-boot-complete" in source
    assert 'section[data-testid="stSidebar"]' in source
    assert 'header[data-testid="stHeader"]' in source
    assert "tala-show-chrome" in source
    assert "opacity: 0" in source
    assert "pointer-events: none" in source
    # The old server-driven reveal path is gone: START is client-only.
    assert "_reveal_chrome_after" not in source
    assert "components.html" not in source


def test_frames_carry_a_start_button_and_a_css_fallback():
    for html in (splash._frame(100, "Ready", done=True), splash._finale(40, 3.0)):
        assert '<button id="tala-start"' in html
        assert "START" in html
    css = splash._CSS
    assert "tala-start-in" in css
    assert "calc(var(--tail) + 12s)" in css     # no-JS fallback fade
    assert "body.tala-boot-complete .tala-splash" in css
    assert "prefers-reduced-motion" in css


def test_segment_delays_match_the_finale_blocks():
    delays = splash._segment_delays(44, 4.0)
    lit = round(splash._BLOCKS * 44 / 100)
    assert len(delays) == splash._BLOCKS - lit
    assert delays[0] == 0 and delays == sorted(delays) and delays[-1] < 4.0
    html = splash._finale(44, 4.0)
    assert f"animation-delay:{delays[-1]:.2f}s" in html


class _Ctx:
    def __init__(self, cookies):
        self.cookies = cookies


def _boot_with(cookies, state=None):
    orig_state, orig_ctx = splash.st.session_state, splash.st.context
    orig_splash = splash.Splash
    splash.st.session_state = {} if state is None else state
    splash.st.context = _Ctx(cookies)
    splash.Splash = lambda: "SPLASH"
    try:
        return splash.boot()
    finally:
        splash.st.session_state, splash.st.context = orig_state, orig_ctx
        splash.Splash = orig_splash


def test_cookie_or_session_flag_skips_the_splash():
    assert _boot_with({"tala_booted": "1"}) is None
    assert _boot_with({}, {"_tala_booted": True}) is None
    state: dict = {}
    assert _boot_with({}, state) == "SPLASH"
    assert state["_tala_booted"] is True


def test_gate_is_language_first_with_continue_and_sky_marker():
    source = (ROOT / "core" / "gate.py").read_text(encoding="utf-8")
    assert 'st.container(key="tala-gate-langs")' in source
    assert "tala-gate-sky" in source
    assert "gate.continue" in source and "audio.mount(\"gate\")" in source
    assert "audio.mark_started()" in source and "i18n.set_lang(pick)" in source


def test_gate_sliders_use_react_aria_contrast_selectors():
    source = (ROOT / "core" / "gate.py").read_text(encoding="utf-8")
    assert 'data-testid="stSlider"' in source
    assert 'pointer-events: none' in source
    assert 'translate(-50%, -50%)' in source
    assert "#fff9de" in source


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
    print("splash and gate guards passed")
