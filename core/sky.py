"""Landing-hero night sky: the survey's own points drawn as stars.

``build_sky_svg`` is pure (DataFrame in, SVG string out); ``sky_svg`` is the
cached wrapper keyed on the dataset key and size only (never the UI language).
The SVG background is transparent; the hero CSS supplies the gradient.
"""
from __future__ import annotations

import random

import numpy as np
import pandas as pd
import streamlit as st

from .splash import GOLD, GOLD_DEEP, SKY_DEEP, SKY_MID  # noqa: F401  (re-exported)

LON_RANGE = (116.0, 127.0)
LAT_RANGE = (4.5, 21.5)
MAX_POINTS = 1500
SEED = 20240607
TWINKLE_SHARE = 0.08
MAP_SHARE = 0.45          # right-hand fraction of the band holding the map
_TINTS = ("#ffffff", "#e8ecff", GOLD, GOLD_DEEP)

_CSS = (
    "<style>"
    ".s0{r:.7}.s1{r:1}.s2{r:1.4}"
    ".a{fill:#fff;opacity:.45}.b{fill:#e8ecff;opacity:.7}"
    f".c{{fill:{GOLD};opacity:.85}}.d{{fill:{GOLD_DEEP};opacity:.75}}"
    ".t{animation:tw 3s ease-in-out infinite}"
    "@keyframes tw{0%,100%{opacity:.2}50%{opacity:1}}"
    "@media (prefers-reduced-motion:reduce){.t{animation:none}}"
    "</style>"
)


def _find_cols(df: pd.DataFrame) -> tuple[str, str] | None:
    cols = {str(c).lower(): c for c in df.columns}
    lon = cols.get("lon") or cols.get("longitude") or cols.get("lng") or cols.get("x")
    lat = cols.get("lat") or cols.get("latitude") or cols.get("y")
    return (lon, lat) if lon is not None and lat is not None else None


def _in_box_points(df: pd.DataFrame) -> np.ndarray:
    cols = _find_cols(df)
    if cols is None:
        return np.empty((0, 2))
    lon = pd.to_numeric(df[cols[0]], errors="coerce").to_numpy(dtype=float)
    lat = pd.to_numeric(df[cols[1]], errors="coerce").to_numpy(dtype=float)
    ok = ((lon >= LON_RANGE[0]) & (lon <= LON_RANGE[1])
          & (lat >= LAT_RANGE[0]) & (lat <= LAT_RANGE[1]))
    return np.column_stack([lon[ok], lat[ok]])


def _star(x: float, y: float, rng: random.Random, i: int, twinkle: bool) -> str:
    size = rng.choices((0, 1, 2), weights=(6, 3, 1))[0]
    tint = rng.choices("abcd", weights=(4, 3, 2, 1))[0]
    cls = f"s{size} {tint}"
    style = ""
    if twinkle:
        cls += " t"
        style = f' style="animation-delay:{(i * 37 % 40) / 10:.1f}s"'
    return f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}"{style}/>'


def build_sky_svg(df: pd.DataFrame | None, width: int = 1100, height: int = 260,
                  max_points: int = MAX_POINTS) -> str:
    """Pure builder. Falls back to a generic starfield without in-box points."""
    pts = _in_box_points(df) if df is not None else np.empty((0, 2))
    rng = random.Random(SEED)
    parts: list[str] = []

    # Faint generic starfield (left side, and behind everything).
    n_bg = 90
    for i in range(n_bg):
        x = rng.uniform(0, width if len(pts) == 0 else width * (1 - MAP_SHARE))
        y = rng.uniform(0, height)
        parts.append(_star(x, y, rng, i, twinkle=rng.random() < TWINKLE_SHARE))
    if len(pts):
        # Dim the background field relative to map points.
        parts.insert(0, '<g opacity=".55">')
        parts.append("</g>")

    count = 0
    if len(pts):
        if len(pts) > max_points:
            idx = np.random.default_rng(SEED).choice(len(pts), max_points, replace=False)
            idx.sort()
            pts = pts[idx]
        count = len(pts)
        lon0, lon1 = LON_RANGE
        lat0, lat1 = LAT_RANGE
        mid_lat = np.radians((lat0 + lat1) / 2)
        wx = (lon1 - lon0) * np.cos(mid_lat)
        hy = lat1 - lat0
        pad = 12.0
        box_w = width * MAP_SHARE - 2 * pad
        box_h = height - 2 * pad
        scale = min(box_w / wx, box_h / hy)
        ox = width - pad - box_w / 2 - wx * scale / 2
        oy = pad + box_h / 2 - hy * scale / 2
        xs = ox + (pts[:, 0] - lon0) * np.cos(mid_lat) * scale
        ys = oy + (lat1 - pts[:, 1]) * scale
        parts.append("<g>")
        for i, (x, y) in enumerate(zip(xs, ys)):
            parts.append(_star(x, y, rng, i, twinkle=rng.random() < TWINKLE_SHARE))
        parts.append("</g>")

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="100%" preserveAspectRatio="xMaxYMid meet" role="img" '
        f'aria-label="Night sky of survey locations" data-points="{count}">'
        f'{_CSS}{"".join(parts)}</svg>'
    )


@st.cache_data(show_spinner=False, max_entries=16)
def sky_svg(df_key: str, width: int = 1100, height: int = 260) -> str:
    """Cached hero sky for the dataset identified by ``df_key``."""
    from . import data_loader

    return build_sky_svg(data_loader.dataset(df_key), width, height)


def active_sky_svg(width: int = 1100, height: int = 260) -> str:
    """Convenience for the landing page: sky for the session's active dataset."""
    from . import data_loader

    return sky_svg(data_loader.source_key(), width, height)
