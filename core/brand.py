"""Project identity: the AIKasalig partner logos, in one place.

TALA is a learning module of **AIKasalig** (Project 4 of the DOST-NICER R&D
Center on Natural Language Processing for Health Applications at National
University). Every surface that shows the partners (the boot splash, Home, the
About page, the footer) draws them from here, so the order, alt text and sizing
cannot drift between screens.

Why a white strip: three of the six marks (the National University wordmark,
the RDC-NLPHA map, the AIKasalig wordmark) are navy or grey ink made for light
paper and disappear on the night-sky theme. They always sit on white.

Why per-logo heights: the marks range from square shields to 3:1 wordmarks. At
one shared height the wide ones look twice as heavy, so each gets an optical
factor (``aspect ** -0.38``, clamped) and square marks a small boost, which
evens out their visual weight.

Static serving is off (``.streamlit/config.toml``), so the images ride in the
HTML as data URIs. Two sizes exist (see ``tools/build_logos.py``): ``lg`` for
the splash and About page, which render once, and ``sm`` (a few KB each) for
anything that re-renders on every interaction, such as the footer.
"""
from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

LOGO_DIR = Path(__file__).resolve().parent.parent / "assets" / "logos"

# Proper names, never translated (like the chapter names Lugar and Salita).
PROJECT = "AIKasalig"
EYEBROW = "AIKasalig · DOST-NICER"                                   # Home hero pill
PARTNER_LINE = "AIKasalig · DOST-NICER RDC-NLPHA · National University"   # boot splash
DEVELOPER = "Mico C. Magtira"

# (file slug, alt text). Order is fixed by the project and must not be sorted.
LOGOS: list[tuple[str, str]] = [
    ("01_dost", "Department of Science and Technology (DOST)"),
    ("02_dost_pchrd", "DOST Philippine Council for Health Research and Development (DOST-PCHRD)"),
    ("03_national_university", "National University"),
    ("04_nicer_dost", "DOST Niche Centers in the Regions for R&D (NICER)"),
    ("05_nicer_rdc_nlpha", "NICER R&D Center on Natural Language Processing for Health Applications"),
    ("06_aikasalig", "AIKasalig"),
]


@lru_cache(maxsize=None)
def _logo(slug: str, size: str) -> tuple[str, float]:
    """``(data URI, aspect ratio)`` for one logo; read and encoded once per process."""
    suffix = "_sm" if size == "sm" else ""
    path = LOGO_DIR / f"{slug}{suffix}.webp"
    data = path.read_bytes()
    from PIL import Image  # lazy: only the first call per logo pays for it

    with Image.open(path) as im:
        aspect = im.width / im.height
    return "data:image/webp;base64," + base64.b64encode(data).decode("ascii"), aspect


# Marks whose ink is thin or small for their box (the RDC-NLPHA map with its tiny
# caption) read lighter than their shape suggests; they get a little extra height.
_BOOST = {"05_nicer_rdc_nlpha": 1.3}


def optical_factor(aspect: float, slug: str = "") -> float:
    """Relative height that gives marks of different shapes similar visual weight."""
    factor = max(0.62, min(1.15, aspect ** -0.38))
    if aspect < 1.3:
        factor *= 1.2
    return factor * _BOOST.get(slug, 1.0)


@lru_cache(maxsize=None)
def strip_html(size: str = "sm", css_class: str = "tala-logos") -> str:
    """The six logos as one white, wrapping strip of ``<img>`` tags.

    Heights are ``calc(var(--logo-h) * factor)``, so the stylesheet sets one
    ``--logo-h`` per breakpoint and every mark scales together. No blank lines:
    Streamlit's markdown parser would break the HTML at one."""
    items = []
    for slug, alt in LOGOS:
        uri, aspect = _logo(slug, size)
        items.append(
            f'<img src="{uri}" alt="{alt}" title="{alt}" loading="lazy" '
            f'style="height:calc(var(--logo-h) * {optical_factor(aspect, slug):.3f})">'
        )
    return f'<div class="{css_class}" role="group" aria-label="Project partners">{"".join(items)}</div>'
