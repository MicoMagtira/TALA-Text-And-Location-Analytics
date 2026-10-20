"""Visual theming for TALA.

Two color roles are kept deliberately separate:

* **Brand chrome** — National University Manila navy/gold/mineshaft. Used for the
  app header, sidebar, buttons and other UI furniture (see assets/styles.css and
  .streamlit/config.toml).
* **Data-viz palettes** — one fixed, colour-blind-safe palette per role
  (categorical, sequential, diverging), used inside charts and maps. There is no
  picker: see the comment above ``_CATEGORICAL``.

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

# --- Fixed data-viz palettes (colour-blind safe, no user choice) ----------------
# TALA ships exactly one palette per role. The Settings panel used to offer
# pickers; they were removed so every chart reads the same and the default is
# already safe for colour-blind readers (docs/PLAN_PANEL.md). The *names* below
# stay so older callers (``viz.categorical(ui.palette(), n)``) keep working.
#
# Categorical: the Okabe-Ito set (designed for all common colour-vision types),
# with its black swapped for the brand navy so the eighth series sits with the
# night/gold identity. Fixed slot order: assign in order, never cycle. Yellow and
# sky blue are light on white, so charts using them ship direct labels.
_CATEGORICAL = {
    "TALA": [
        "#0072B2", "#E69F00", "#009E73", "#CC79A7",
        "#56B4E9", "#D55E00", "#F0E442", "#232a5e",
    ],
}
DEFAULT_CATEGORICAL = "TALA"

# Sequential (magnitude: heatmaps, bubble maps): a 16-step sample of matplotlib's
# cividis, which is perceptually uniform and readable under every common colour
# deficiency. Stored as hex stops so importing this module stays free.
_SEQUENTIAL: dict[str, list[str]] = {
    "TALA": ["#00224e", "#002e6c", "#1e3a6f", "#35456c", "#47516c", "#575d6d",
             "#666970", "#757575", "#848279", "#948e77", "#a59c74", "#b7a96e",
             "#c8b866", "#dbc75a", "#eed649", "#fee838"],
}
DEFAULT_SEQUENTIAL = "TALA"

# Diverging (above/below a midpoint, such as a log-odds z): brand blue to brand
# gold through a warm neutral. Blue-orange is the diverging pair that survives
# red-green colour blindness; the neutral centre keeps "no difference" quiet.
_DIVERGING: dict[str, list[str]] = {
    "TALA": ["#233a8f", "#3f58a8", "#6b82c2", "#9db0dc", "#d2dcf0", "#f3f1ea",
             "#f6e3b4", "#efca7b", "#dba73f", "#b98215", "#8a5c00"],
}
DEFAULT_DIVERGING = "TALA"

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


def diverging_names() -> list[str]:
    return list(_DIVERGING)


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


def _sample(stops: list[str], n: int) -> list[str]:
    """Sample ordered hex stops into ``n`` evenly spaced hexes (sRGB interpolation)."""
    if n <= 1:
        return stops[:1]
    out = []
    for i in range(n):
        pos = i / (n - 1) * (len(stops) - 1)
        lo = min(int(pos), len(stops) - 2)
        out.append(_lerp_hex(stops[lo], stops[lo + 1], pos - lo))
    return out


def sequential_hexes(name: str = DEFAULT_SEQUENTIAL, n: int = 6) -> list[str]:
    """Sample the sequential palette into n hex steps (for pydeck/Plotly).

    Pure-Python interpolation over the stored stops, so the geo and Plotly pages
    do not drag matplotlib in just to pick colors."""
    return _sample(sequential_stops(name), n)


def diverging_stops(name: str = DEFAULT_DIVERGING) -> list[str]:
    """The raw ordered hex stops of the diverging palette (low end first)."""
    return list(_DIVERGING.get(name, _DIVERGING[DEFAULT_DIVERGING]))


def diverging_hexes(n: int = 9, name: str = DEFAULT_DIVERGING) -> list[str]:
    """Sample the blue-to-gold diverging palette into ``n`` steps. An odd ``n``
    puts the neutral midpoint exactly in the middle."""
    return _sample(diverging_stops(name), n)


def hex_to_rgba(hex_color: str, alpha: int = 200) -> list[int]:
    """``#rrggbb`` -> ``[r, g, b, alpha]`` (0-255), the colour form pydeck wants."""
    h = hex_color.lstrip("#")
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)] + [int(alpha)]


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
