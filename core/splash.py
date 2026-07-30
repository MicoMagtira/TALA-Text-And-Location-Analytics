"""8-bit boot splash for TALA.

*Tala* is Filipino for **star**, so the loading screen is a pixel-art night sky:
a twinkling gold star flanked by a speech bubble (the Text half of the app) and a
map pin (the Location half), over a retro segmented progress bar.

Two deliberate implementation choices:

* **No GIF.** The sprites are inline SVG generated from the ASCII grids below and
  the motion is pure CSS. That means zero extra bytes over the wire, nothing to
  decode, crisp edges at any zoom, and no binary asset in the repo — which
  matters when the whole point of the exercise is a smaller, faster container.
  A strict CSP or an offline container cannot break it either.
* **No artificial delay.** Progress is driven by the server as real work
  completes, and the final frame fades itself out with a CSS animation rather
  than a ``time.sleep``. The splash never makes the app slower to reach.
"""
from __future__ import annotations

import random

import streamlit as st

# --- palette (National University Manila) ------------------------------------
SKY_DEEP = "#0b0f2b"
SKY_MID = "#1b2559"
NAVY = "#35408E"
GOLD = "#F5D89E"
GOLD_DEEP = "#C9962E"
INK_ON_SKY = "#c8d0f0"

# --- sprites ----------------------------------------------------------------
# '#' primary  '+' accent  'o' shadow/hole  '.' transparent
# The star is a rasterized 5-point polygon (r_out 7.2, r_in 3.7 on a 15x15 grid),
# so it is symmetric to the pixel; the legs were thickened by hand for weight.
STAR = """
.......#.......
.......#.......
......###......
......###......
..###########..
.#############.
..###########..
...#########...
....#######....
....#######....
....#######....
...###...###...
...##.....##...
"""

BUBBLE = """
############
#..........#
#.+..+..+..#
#..........#
############
..##........
..#.........
"""

PIN = """
...#####...
..#######..
.###ooo###.
.##ooooo##.
.###ooo###.
.#########.
..#######..
...#####...
....###....
.....#.....
...........
...ooooo...
"""


def _sprite_svg(art: str, colors: dict[str, str], pixel: int = 4,
                extra_class: str = "") -> str:
    """Turn an ASCII grid into inline SVG, run-length encoded per row.

    Adjacent cells of the same color collapse into one <rect>, which keeps the
    markup small enough to inline comfortably."""
    rows = [r for r in art.strip("\n").split("\n")]
    h = len(rows)
    w = max(len(r) for r in rows)
    rects: list[str] = []
    for y, row in enumerate(rows):
        x = 0
        row = row.ljust(w, ".")
        while x < w:
            ch = row[x]
            if ch not in colors:
                x += 1
                continue
            start = x
            while x < w and row[x] == ch:
                x += 1
            rects.append(
                f'<rect x="{start}" y="{y}" width="{x - start}" height="1" '
                f'fill="{colors[ch]}"/>'
            )
    return (
        f'<svg class="tala-sprite {extra_class}" viewBox="0 0 {w} {h}" '
        f'width="{w * pixel}" height="{h * pixel}" '
        f'shape-rendering="crispEdges" aria-hidden="true">{"".join(rects)}</svg>'
    )


def _starfield(n: int = 46, seed: int = 7) -> str:
    """Deterministic scatter of background stars, each blinking on its own clock."""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        left = rng.uniform(1, 99)
        top = rng.uniform(2, 96)
        size = rng.choice((2, 2, 2, 3, 3, 4))
        delay = rng.uniform(0, 3.2)
        dur = rng.uniform(1.8, 3.6)
        dim = rng.uniform(0.25, 0.7)
        out.append(
            f'<i style="left:{left:.2f}%;top:{top:.2f}%;width:{size}px;'
            f'height:{size}px;animation-delay:{delay:.2f}s;'
            f'animation-duration:{dur:.2f}s;--dim:{dim:.2f}"></i>'
        )
    return f'<div class="tala-starfield">{"".join(out)}</div>'


_CSS = f"""
<style>
@keyframes tala-twinkle {{
  0%, 100% {{ opacity: var(--dim); transform: scale(1); }}
  50%      {{ opacity: 1; transform: scale(1.35); }}
}}
@keyframes tala-star-pulse {{
  0%, 100% {{ transform: scale(1) rotate(-4deg); filter: drop-shadow(0 0 6px {GOLD_DEEP}); }}
  50%      {{ transform: scale(1.09) rotate(4deg); filter: drop-shadow(0 0 22px {GOLD}); }}
}}
@keyframes tala-ray {{
  0%, 100% {{ opacity: .15; transform: scale(.7); }}
  50%      {{ opacity: .85; transform: scale(1.25); }}
}}
@keyframes tala-bob {{
  0%, 100% {{ transform: translateY(0); }}
  50%      {{ transform: translateY(-7px); }}
}}
@keyframes tala-scan {{
  0%   {{ transform: translateY(-100%); }}
  100% {{ transform: translateY(100%); }}
}}
@keyframes tala-caret {{
  0%, 49%   {{ opacity: 1; }}
  50%, 100% {{ opacity: 0; }}
}}
@keyframes tala-block-in {{
  from {{ transform: scaleY(.3); opacity: 0; }}
  to   {{ transform: scaleY(1); opacity: 1; }}
}}
@keyframes tala-fade-out {{
  from {{ opacity: 1; }}
  to   {{ opacity: 0; visibility: hidden; }}
}}

.tala-splash {{
  position: fixed; inset: 0; z-index: 99999;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 1.1rem;
  background:
    radial-gradient(120% 90% at 50% 8%, {SKY_MID} 0%, {SKY_DEEP} 62%, #05071a 100%);
  overflow: hidden;
  font-family: "Courier New", ui-monospace, monospace;
  /* honour the reduced-motion preference: keep the art, drop the animation */
}}
.tala-splash.is-done {{
  animation: tala-fade-out .45s ease .05s forwards;
  pointer-events: none;
}}

.tala-starfield {{ position: absolute; inset: 0; }}
.tala-starfield i {{
  position: absolute; display: block; background: #ffffff;
  animation-name: tala-twinkle; animation-iteration-count: infinite;
  animation-timing-function: ease-in-out; opacity: var(--dim);
}}

/* --- CRT dressing ------------------------------------------------------- */
.tala-splash::before {{           /* static scanlines */
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background: repeating-linear-gradient(
    to bottom, rgba(0,0,0,.22) 0 1px, transparent 1px 3px);
  mix-blend-mode: multiply;
}}
.tala-splash::after {{            /* travelling bright band + vignette */
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background:
    linear-gradient(to bottom, transparent 0%, rgba(255,255,255,.055) 50%, transparent 100%),
    radial-gradient(120% 80% at 50% 50%, transparent 55%, rgba(0,0,0,.55) 100%);
  background-size: 100% 42%, 100% 100%;
  background-repeat: no-repeat, no-repeat;
  animation: tala-scan 3.4s linear infinite;
}}

/* --- sprite row --------------------------------------------------------- */
.tala-sprite {{ image-rendering: pixelated; display: block; }}
.tala-cast {{
  position: relative; z-index: 2;
  display: flex; align-items: center; justify-content: center; gap: clamp(14px, 5vw, 46px);
}}
.tala-cast .side {{ animation: tala-bob 2.6s ease-in-out infinite; opacity: .95; }}
.tala-cast .side.right {{ animation-delay: 1.3s; }}

.tala-starwrap {{ position: relative; display: grid; place-items: center; }}
.tala-starwrap .core {{ animation: tala-star-pulse 2.1s ease-in-out infinite; }}
.tala-starwrap .ray {{
  position: absolute; background: {GOLD};
  animation: tala-ray 1.7s ease-in-out infinite;
}}
.tala-starwrap .ray.h {{ width: 108px; height: 3px; }}
.tala-starwrap .ray.v {{ width: 3px; height: 108px; animation-delay: .42s; }}
.tala-starwrap .ray.d1,
.tala-starwrap .ray.d2 {{ width: 84px; height: 3px; opacity: .5; }}
.tala-starwrap .ray.d1 {{ transform: rotate(45deg); animation-delay: .85s; }}
.tala-starwrap .ray.d2 {{ transform: rotate(-45deg); animation-delay: 1.27s; }}

/* --- wordmark ----------------------------------------------------------- */
.tala-wordmark {{
  position: relative; z-index: 2; text-align: center; margin-top: .35rem;
}}
.tala-wordmark b {{
  display: block; color: {GOLD}; font-size: clamp(2.1rem, 8vw, 3.4rem);
  font-weight: 700; letter-spacing: .42em; text-indent: .42em; line-height: 1;
  text-shadow: 3px 3px 0 {GOLD_DEEP}, 6px 6px 0 rgba(0,0,0,.45);
}}
.tala-wordmark span {{
  display: block; margin-top: .7rem; color: {INK_ON_SKY};
  font-size: clamp(.56rem, 2vw, .72rem); letter-spacing: .3em; opacity: .82;
}}

/* --- progress ----------------------------------------------------------- */
.tala-progress {{
  position: relative; z-index: 2; display: flex; gap: 3px;
  padding: 5px; border: 3px solid {NAVY}; background: rgba(0,0,0,.35);
  box-shadow: 0 0 0 3px rgba(0,0,0,.4);
}}
.tala-progress i {{
  display: block; width: clamp(7px, 1.7vw, 11px); height: 17px;
  background: rgba(255,255,255,.07);
}}
.tala-progress i.on {{
  background: linear-gradient(to bottom, {GOLD} 0 45%, {GOLD_DEEP} 45% 100%);
  transform-origin: bottom;
  animation: tala-block-in .22s ease backwards;
}}
.tala-status {{
  position: relative; z-index: 2; color: {GOLD};
  font-size: clamp(.66rem, 2.2vw, .8rem); letter-spacing: .16em;
  min-height: 1.2em; text-transform: uppercase;
}}
.tala-status .pct {{ color: {INK_ON_SKY}; opacity: .75; margin-right: .8em; }}
.tala-status .caret {{ animation: tala-caret 1s step-end infinite; }}

@media (prefers-reduced-motion: reduce) {{
  .tala-splash *, .tala-splash::after {{ animation: none !important; }}
  .tala-starfield i {{ opacity: .8; }}
}}
</style>
"""

_BLOCKS = 18


def _frame(pct: int, message: str, done: bool = False) -> str:
    pct = max(0, min(100, int(pct)))
    lit = round(_BLOCKS * pct / 100)
    blocks = "".join(
        f'<i class="on" style="animation-delay:{i * 0.03:.2f}s"></i>' if i < lit
        else "<i></i>"
        for i in range(_BLOCKS)
    )
    star = (
        '<div class="tala-starwrap">'
        '<span class="ray h"></span><span class="ray v"></span>'
        '<span class="ray d1"></span><span class="ray d2"></span>'
        + _sprite_svg(STAR, {"#": GOLD}, pixel=7, extra_class="core")
        + "</div>"
    )
    cast = (
        '<div class="tala-cast">'
        f'<div class="side left">{_sprite_svg(BUBBLE, {"#": NAVY, "+": GOLD}, 5)}</div>'
        f"{star}"
        f'<div class="side right">{_sprite_svg(PIN, {"#": NAVY, "o": GOLD}, 5)}</div>'
        "</div>"
    )
    return (
        f'<div class="tala-splash{" is-done" if done else ""}">'
        + _starfield()
        + cast
        + '<div class="tala-wordmark"><b>TALA</b>'
          "<span>TEXT AND LOCATION ANALYTICS</span></div>"
        + f'<div class="tala-progress">{blocks}</div>'
        + f'<div class="tala-status"><span class="pct">{pct:3d}%</span>'
          f'{message}<span class="caret">_</span></div>'
        + "</div>"
    )


class Splash:
    """Handle for a live splash. Use via :func:`boot`."""

    def __init__(self) -> None:
        # The stylesheet gets its own element because ``st.empty()`` *replaces*
        # its content on every write — keeping the CSS inside the frame slot
        # would tear it out again on the first progress update.
        st.markdown(_CSS, unsafe_allow_html=True)
        self._slot = st.empty()

    def update(self, pct: int, message: str) -> None:
        self._slot.markdown(_frame(pct, message), unsafe_allow_html=True)

    def finish(self, message: str = "Ready") -> None:
        """Render the fade-out frame.

        The overlay animates itself away client-side, so the page underneath is
        already painted and interactive — no server-side sleep, and the splash
        costs nothing on the critical path."""
        self._slot.markdown(_frame(100, message, done=True), unsafe_allow_html=True)


def boot(force: bool = False) -> Splash | None:
    """Return a :class:`Splash` on a session's first script run, else ``None``.

    Reruns triggered by widgets must not flash the splash again, so this is
    gated on session state."""
    if not force and st.session_state.get("_tala_booted"):
        return None
    st.session_state["_tala_booted"] = True
    return Splash()
