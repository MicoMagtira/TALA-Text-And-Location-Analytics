"""Guards for the boot splash's client-side chrome handoff."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_boot_hides_chrome_until_the_splash_finishes():
    source = (ROOT / "core" / "splash.py").read_text(encoding="utf-8")
    assert "tala-boot-complete" in source
    assert 'section[data-testid="stSidebar"]' in source
    assert 'header[data-testid="stHeader"]' in source
    assert "_reveal_chrome_after" in source
    assert "host.setTimeout" in source


def test_gate_sliders_use_react_aria_contrast_selectors():
    source = (ROOT / "core" / "gate.py").read_text(encoding="utf-8")
    assert 'data-testid="stSlider"' in source
    assert 'pointer-events: none' in source
    assert 'translate(-50%, -50%)' in source
    assert "#fff9de" in source


if __name__ == "__main__":
    test_boot_hides_chrome_until_the_splash_finishes()
    test_gate_sliders_use_react_aria_contrast_selectors()
    print("2/2 splash and gate guards passed")
