"""Visual theming for TALA.

Two color roles are kept deliberately separate:

* **Brand chrome** — National University Manila navy/gold/mineshaft. Used for the
  app header, sidebar, buttons and other UI furniture (see assets/styles.css and
  .streamlit/config.toml).
* **Data-viz palettes** — the categorical series colors used inside charts and
  maps. The default ("National University") is the data-viz skill's validated
  8-hue categorical set (worst adjacent CVD ΔE 9.1 light / 8.4 dark), which is
  blue-led so it harmonizes with the brand navy while staying colorblind-safe.
  Chart series color must be readable, so it is chosen by that computable gate
  rather than forced to the literal brand hexes.
"""
from __future__ import annotations

from functools import lru_cache

import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

# --- National University Manila brand ------------------------------------------
NU_NAVY = "#35408E"      # Navy Blue / Chambray  (primary)
NU_GOLD = "#F5D89E"      # Gold / Maize          (accent)
NU_DARK = "#333333"      # Mine Shaft            (dark text/elements)
NU_GOLD_DEEP = "#C9962E"  # readable gold for marks/text on white
NU_NAVY_LIGHT = "#5B67B7"

# --- Categorical data-viz palettes (validated) ---------------------------------
# Default: data-viz skill reference set, light-surface steps. Fixed slot order —
# assign in order, never cycle. Slots 4/3/5 (yellow/aqua/magenta) sit sub-3:1 on
# white, so charts using them always ship direct labels or a table view.
_CATEGORICAL = {
    "National University": [
        "#2a78d6", "#eb6834", "#1baf7a", "#eda100",
        "#e87ba4", "#008300", "#4a3aa7", "#e34948",
    ],
    # Okabe-Ito: widely used colorblind-safe eight.
    "Okabe-Ito (colorblind-safe)": [
        "#0072B2", "#E69F00", "#009E73", "#CC79A7",
        "#56B4E9", "#D55E00", "#F0E442", "#000000",
    ],
    # A warmer, brand-forward option (navy + deep gold led).
    "NU Warm": [
        "#35408E", "#C9962E", "#2E8B7A", "#C0413B",
        "#5B67B7", "#6B8E23", "#8A5FA8", "#B5651D",
    ],
}
DEFAULT_CATEGORICAL = "National University"

# --- Sequential colormaps (for magnitude: heatmaps, choropleths, word clouds) --
# Single-hue navy ramp light->dark, plus perceptually-uniform standards.
_NU_NAVY_RAMP = LinearSegmentedColormap.from_list(
    "nu_navy", ["#eef1fb", "#b7c0e6", "#7d8ac9", "#4a56a5", NU_NAVY, "#232a5e"]
)
_NU_GOLD_RAMP = LinearSegmentedColormap.from_list(
    "nu_gold", ["#fbf4e1", "#f5d89e", "#e2b85f", "#c9962e", "#966c17"]
)

_SEQUENTIAL = {
    "NU Navy": _NU_NAVY_RAMP,
    "NU Gold": _NU_GOLD_RAMP,
    "Viridis": mpl.colormaps["viridis"],
    "Cividis (colorblind-safe)": mpl.colormaps["cividis"],
    "Magma": mpl.colormaps["magma"],
}
DEFAULT_SEQUENTIAL = "NU Navy"

# Chart chrome / ink (light surface), from the data-viz reference.
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
SURFACE = "#ffffff"


def categorical_names() -> list[str]:
    return list(_CATEGORICAL)


def sequential_names() -> list[str]:
    return list(_SEQUENTIAL)


def categorical(name: str = DEFAULT_CATEGORICAL, n: int | None = None) -> list[str]:
    """Return the fixed-order categorical hexes. Assign in order; if more series
    than slots are needed, the caller must fold extras into 'Other'/facets."""
    colors = _CATEGORICAL.get(name, _CATEGORICAL[DEFAULT_CATEGORICAL])
    if n is None:
        return list(colors)
    if n <= len(colors):
        return colors[:n]
    # Never invent hues by cycling silently — repeat with a warning-friendly tail.
    reps = (n // len(colors)) + 1
    return (colors * reps)[:n]


def sequential_cmap(name: str = DEFAULT_SEQUENTIAL):
    """Return a matplotlib Colormap for magnitude encodings / word clouds."""
    return _SEQUENTIAL.get(name, _SEQUENTIAL[DEFAULT_SEQUENTIAL])


def sequential_hexes(name: str = DEFAULT_SEQUENTIAL, n: int = 6) -> list[str]:
    """Sample a sequential colormap into n hex steps (for branca/folium)."""
    cmap = sequential_cmap(name)
    return [mpl.colors.to_hex(cmap(i / max(1, n - 1))) for i in range(n)]


def apply_matplotlib_theme() -> None:
    """Apply a clean, brand-consistent look to matplotlib figures."""
    mpl.rcParams.update({
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": BASELINE,
        "axes.labelcolor": INK_SECONDARY,
        "axes.titlecolor": INK_PRIMARY,
        "axes.titleweight": "semibold",
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRIDLINE,
        "grid.linewidth": 0.8,
        "xtick.color": INK_MUTED,
        "ytick.color": INK_MUTED,
        "text.color": INK_PRIMARY,
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.autolayout": True,
    })


def plotly_template(palette: str = DEFAULT_CATEGORICAL) -> dict:
    """A minimal Plotly layout honoring the brand ink + categorical order."""
    return {
        "layout": {
            "colorway": categorical(palette),
            "font": {"color": INK_SECONDARY, "family": "Segoe UI, Arial, sans-serif"},
            "paper_bgcolor": SURFACE,
            "plot_bgcolor": SURFACE,
            "xaxis": {"gridcolor": GRIDLINE, "zerolinecolor": BASELINE, "linecolor": BASELINE},
            "yaxis": {"gridcolor": GRIDLINE, "zerolinecolor": BASELINE, "linecolor": BASELINE},
            "title": {"font": {"color": INK_PRIMARY, "size": 18}},
            "legend": {"font": {"color": INK_SECONDARY}},
        }
    }


@lru_cache(maxsize=1)
def load_css(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()
