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

Import cost note: this module is pulled in by ``core.ui``, which ``app.py``
imports on every page load. It therefore stays matplotlib-free at import time —
palettes are plain hex data, and matplotlib is only imported inside the two
functions that genuinely need a ``Colormap`` object (word clouds and the
matplotlib theme).
"""
from __future__ import annotations

from functools import lru_cache

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
# Stored as ordered hex stops rather than matplotlib Colormap objects so that
# importing this module costs nothing. The perceptually-uniform standards are
# 16-step samples of the matplotlib originals (viridis/cividis/magma), which is
# well past the resolution any of our encodings resolve.
_SEQUENTIAL: dict[str, list[str]] = {
    # Single-hue navy ramp light->dark.
    "NU Navy": ["#eef1fb", "#b7c0e6", "#7d8ac9", "#4a56a5", NU_NAVY, "#232a5e"],
    "NU Gold": ["#fbf4e1", "#f5d89e", "#e2b85f", "#c9962e", "#966c17"],
    "Viridis": ["#440154", "#481a6c", "#472f7d", "#414487", "#39568c", "#31688e",
                "#2a788e", "#23888e", "#1f988b", "#22a884", "#35b779", "#54c568",
                "#7ad151", "#a5db36", "#d2e21b", "#fde725"],
    "Cividis (colorblind-safe)": [
                "#00224e", "#002e6c", "#1e3a6f", "#35456c", "#47516c", "#575d6d",
                "#666970", "#757575", "#848279", "#948e77", "#a59c74", "#b7a96e",
                "#c8b866", "#dbc75a", "#eed649", "#fee838"],
    "Magma": ["#000004", "#0b0924", "#20114b", "#3b0f70", "#57157e", "#721f81",
              "#8c2981", "#a8327d", "#c43c75", "#de4968", "#f1605d", "#fa7f5e",
              "#fe9f6d", "#febf84", "#fddea0", "#fcfdbf"],
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


def sequential_stops(name: str = DEFAULT_SEQUENTIAL) -> list[str]:
    """Return the raw ordered hex stops of a sequential palette (no matplotlib)."""
    return list(_SEQUENTIAL.get(name, _SEQUENTIAL[DEFAULT_SEQUENTIAL]))


@lru_cache(maxsize=8)
def sequential_cmap(name: str = DEFAULT_SEQUENTIAL):
    """Return a matplotlib Colormap for magnitude encodings / word clouds.

    Imports matplotlib lazily — only word-cloud rendering needs a real Colormap,
    so pages that never draw one never pay for the import."""
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list(name, sequential_stops(name))


def _lerp_hex(a: str, b: str, t: float) -> str:
    """Linearly interpolate two #rrggbb colors in sRGB."""
    ar, ag, ab = (int(a[i:i + 2], 16) for i in (1, 3, 5))
    br, bg, bb = (int(b[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (
        round(ar + (br - ar) * t),
        round(ag + (bg - ag) * t),
        round(ab + (bb - ab) * t),
    )


def sequential_hexes(name: str = DEFAULT_SEQUENTIAL, n: int = 6) -> list[str]:
    """Sample a sequential palette into n hex steps (for branca/folium/Plotly).

    Pure-Python interpolation over the stored stops, so the geo and Plotly pages
    do not drag matplotlib in just to pick colors."""
    stops = sequential_stops(name)
    if n <= 1:
        return stops[:1]
    out = []
    for i in range(n):
        pos = i / (n - 1) * (len(stops) - 1)
        lo = min(int(pos), len(stops) - 2)
        out.append(_lerp_hex(stops[lo], stops[lo + 1], pos - lo))
    return out


def figure(figsize=(8, 3.2)):
    """Create a themed, thread-safe matplotlib Figure.

    Deliberately avoids ``plt.subplots``. pyplot keeps a *process-global* registry
    of figures, but Streamlit runs every user session on its own thread — so
    concurrent trainees rendering charts can interleave on that shared state and
    land a figure in the wrong session. Worse, pyplot holds a reference to every
    figure it creates, so without an explicit ``plt.close`` each rerun leaked one.

    Constructing ``Figure`` directly keeps the object local to the caller: nothing
    is registered globally, and it is garbage-collected normally. ``st.pyplot``
    accepts such a figure exactly like a pyplot one."""
    from matplotlib.figure import Figure

    apply_matplotlib_theme()
    fig = Figure(figsize=figsize)
    fig.set_facecolor(SURFACE)
    ax = fig.subplots()
    return fig, ax


def apply_matplotlib_theme() -> None:
    """Apply a clean, brand-consistent look to matplotlib figures.

    Sets the non-interactive Agg backend, which is the only safe choice on a
    headless server and avoids any GUI toolkit being probed at import time."""
    import matplotlib as mpl

    if mpl.get_backend().lower() != "agg":
        mpl.use("Agg", force=True)

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
