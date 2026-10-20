"""Build the partner-logo assets TALA ships, from the raw files in ``logos/``.

Run:  .venv/Scripts/python tools/build_logos.py

The raw folder is git-ignored: it holds 1-2 MB source PNGs and the project's
private paperwork (proposal, notarized MOA), none of which belongs in a public
repository. What ships is ``assets/logos/NN_<slug>.webp``: trimmed to the ink,
cleaned for a white banner, scaled to one height, and saved as WebP (a few KB
each) because the app inlines them as data URIs: static serving is off, so every
byte rides in the page HTML.

Per-logo fixes, each because the raw file would look wrong on the white strip:

* **DOST** is a JPEG with a fake transparency checkerboard (white + #E7E7E7
  squares) baked into the pixels. Neutral light pixels become transparent, and
  grey anti-aliasing becomes black at partial alpha, so edges stay smooth.
* **NICER RDC-NLPHA** draws its map in pale, semi-transparent grey with tiny
  text; at strip sizes it all but vanishes next to the solid marks. Its alpha is
  lifted and its neutral greys deepened (coloured accents untouched).
* **National University** has a *white* wordmark under the shield, made for
  dark backgrounds; on a white banner it vanishes. The wordmark band (below the
  shield) is recoloured to NU navy; the shield itself is left untouched.

Order is fixed by the project: DOST, DOST-PCHRD, National University,
NICER-DOST, NICER (RDC-NLPHA), AIKasalig.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "logos"
OUT = ROOT / "assets" / "logos"
HEIGHT = 240          # px; 2x the largest on-screen height, so retina stays crisp
HEIGHT_SM = 72        # px; footer/strip variant, light enough to re-send every rerun
NU_NAVY = (53, 64, 142)

# (output slug, raw filename)
LOGOS = [
    ("01_dost", "DOST.jpg"),
    ("02_dost_pchrd", "DOST-PCHRD.png"),
    ("03_national_university", "National University.png"),
    ("04_nicer_dost", "NICER-DOST.png"),
    ("05_nicer_rdc_nlpha", "NICER LOGO 1.png"),
    ("06_aikasalig", "AIKasalig 1.png"),
]


def _dost(im: Image.Image) -> Image.Image:
    """Drop the baked-in checkerboard: neutral light pixels -> transparent."""
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    sat = a.max(axis=2) - a.min(axis=2)
    v = a.mean(axis=2)
    neutral = sat < 18
    alpha = np.full(v.shape, 255.0)
    # Black ink anti-aliased over a ~231 grey/255 white square: alpha = 1 - v/231.
    alpha[neutral] = np.clip(1.0 - v[neutral] / 228.0, 0, 1) * 255
    rgb = a.copy()
    rgb[neutral] = 0  # neutral ink is black; partial alpha carries the edge
    out = np.dstack([rgb, alpha]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def _nu(im: Image.Image) -> Image.Image:
    """Recolour the white wordmark below the shield to NU navy."""
    a = np.asarray(im.convert("RGBA")).copy()
    h = a.shape[0]
    opaque = a[..., 3] > 0
    coloured = opaque & (a[..., :3].min(axis=2) < 200)
    shield_bottom = int(np.where(coloured.any(axis=1))[0].max())
    band = np.zeros(h, dtype=bool)
    band[shield_bottom + 1:] = True
    white = opaque & (a[..., :3].min(axis=2) > 200) & band[:, None]
    a[white, 0], a[white, 1], a[white, 2] = NU_NAVY
    return Image.fromarray(a, "RGBA")


def _rdc(im: Image.Image) -> Image.Image:
    """Make the pale, semi-transparent map and its tiny text hold up when small."""
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    rgb, alpha = a[..., :3], a[..., 3]
    neutral = (rgb.max(axis=2) - rgb.min(axis=2)) < 20
    a[..., 3] = np.clip(alpha * 2.4, 0, 255)
    rgb[neutral] = rgb[neutral] * 0.62  # ~160 grey -> ~100: still grey, now legible
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def _trim(im: Image.Image) -> Image.Image:
    alpha = np.asarray(im.getchannel("A"))
    ys, xs = np.where(alpha > 8)
    pad = 4
    box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0),
           min(xs.max() + pad + 1, im.width), min(ys.max() + pad + 1, im.height))
    return im.crop(box)


def build() -> list[tuple[str, int, int, int]]:
    OUT.mkdir(parents=True, exist_ok=True)
    report = []
    for slug, raw in LOGOS:
        im = Image.open(RAW / raw)
        if slug == "01_dost":
            im = _dost(im)
        elif slug == "03_national_university":
            im = _nu(im)
        elif slug == "05_nicer_rdc_nlpha":
            im = _rdc(im)
        im = _trim(im.convert("RGBA"))
        for height, suffix in ((HEIGHT, ""), (HEIGHT_SM, "_sm")):
            w = round(im.width * height / im.height)
            path = OUT / f"{slug}{suffix}.webp"
            im.resize((w, height), Image.LANCZOS).save(path, "WEBP", quality=90, method=6)
            report.append((path.name, w, height, path.stat().st_size))
    return report


if __name__ == "__main__":
    for name, w, h, size in build():
        print(f"{name:32s} {w:4d}x{h}  {size / 1024:6.1f} KB")
