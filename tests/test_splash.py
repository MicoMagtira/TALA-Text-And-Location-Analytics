"""Guards for the boot splash's client-side chrome handoff."""
from __future__ import annotations

import base64
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import splash


def test_boot_hides_chrome_until_the_splash_finishes():
    source = (ROOT / "core" / "splash.py").read_text(encoding="utf-8")
    assert "tala-boot-complete" in source
    assert 'section[data-testid="stSidebar"]' in source
    assert 'header[data-testid="stHeader"]' in source
    assert "_reveal_chrome_after" in source
    assert "host.setTimeout" in source
    assert "st.html(" in source
    assert "unsafe_allow_javascript=True" in source
    assert "components.html" not in source
    assert "encoded_reveal" in source
    assert 'document.createElement("script")' in source
    assert "tala-show-chrome" in source
    assert "const host = window;" in source
    assert "opacity: 0" in source
    assert "pointer-events: none" in source


def test_splash_reveal_bootstrap_contains_the_controller():
    rendered = []
    original_html = splash.st.html
    splash.st.html = lambda body, **kwargs: rendered.append((body, kwargs))
    try:
        splash.Splash._reveal_chrome_after(1.25)
    finally:
        splash.st.html = original_html

    body, options = rendered[0]
    assert options == {"unsafe_allow_javascript": True}
    encoded = re.search(r'atob\("([A-Za-z0-9+/=]+)"\)', body)
    assert encoded, "missing splash controller payload"
    controller = base64.b64decode(encoded.group(1)).decode("utf-8")
    assert "host.setTimeout" in controller
    assert "tala-boot-complete" in controller
    assert "1250" in controller


def test_gate_sliders_use_react_aria_contrast_selectors():
    source = (ROOT / "core" / "gate.py").read_text(encoding="utf-8")
    assert 'data-testid="stSlider"' in source
    assert 'pointer-events: none' in source
    assert 'translate(-50%, -50%)' in source
    assert "#fff9de" in source


if __name__ == "__main__":
    test_boot_hides_chrome_until_the_splash_finishes()
    test_splash_reveal_bootstrap_contains_the_controller()
    test_gate_sliders_use_react_aria_contrast_selectors()
    print("3/3 splash and gate guards passed")
