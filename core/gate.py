"""Language-select gate — the first screen of a TALA session.

The app opens like a console game: the pixel-art night sky from the boot splash,
five language cards, and a START button. Nothing else renders until a language
is chosen, so the boot splash that follows is already localized and a trainee
never sees the UI change language underneath them.

Why this is not a GIF
---------------------
The brief asked for "a basic animation similar to the theme". The splash already
solves that without a binary asset: sprites are ASCII grids rendered to inline
SVG and every bit of motion is CSS. Reusing that here keeps the promise the rest
of the app makes — zero extra bytes over the wire, crisp at any zoom, works
offline and behind a strict CSP, and nothing new in the repo to keep in sync.
A GIF would have been the only binary in the tree and the only part of the boot
sequence that could not scale with the container budget.

Why a real page rather than the fixed overlay
---------------------------------------------
The boot splash is a fixed-position overlay because nothing on it is clickable.
This screen needs real Streamlit buttons, and widgets cannot be nested inside
injected HTML — so the sky is painted onto the app background and the art sits
in normal flow above it, with the widgets styled to match.
"""
from __future__ import annotations

import streamlit as st

from . import i18n
from .splash import (
    BUBBLE, GOLD, GOLD_DEEP, INK_ON_SKY, NAVY, PIN, SKY_DEEP, SKY_MID, STAR,
    _sprite_svg, _starfield,
)

_GATE_CSS = f"""
<style>
/* Paint the night sky onto the app itself; the art then sits in normal flow so
   the language buttons underneath stay real, focusable Streamlit widgets. */
.stApp {{
  background:
    radial-gradient(120% 90% at 50% 0%, {SKY_MID} 0%, {SKY_DEEP} 62%, #05071a 100%);
}}
section[data-testid="stSidebar"], header[data-testid="stHeader"] {{ display: none; }}
.block-container {{ position: relative; z-index: 2; padding-top: 2.2rem; max-width: 900px; }}

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
@keyframes tala-blink {{
  0%, 49%   {{ opacity: 1; }}
  50%, 100% {{ opacity: .15; }}
}}
@keyframes tala-scan {{
  0%   {{ transform: translateY(-100%); }}
  100% {{ transform: translateY(100%); }}
}}

/* Starfield + CRT dressing live in a fixed layer behind the widgets. */
.tala-sky {{ position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }}
.tala-sky::before {{
  content: ""; position: absolute; inset: 0;
  background: repeating-linear-gradient(
    to bottom, rgba(0,0,0,.22) 0 1px, transparent 1px 3px);
  mix-blend-mode: multiply;
}}
.tala-sky::after {{
  content: ""; position: absolute; inset: 0;
  background:
    linear-gradient(to bottom, transparent 0%, rgba(255,255,255,.05) 50%, transparent 100%),
    radial-gradient(120% 80% at 50% 50%, transparent 55%, rgba(0,0,0,.55) 100%);
  background-size: 100% 42%, 100% 100%;
  background-repeat: no-repeat, no-repeat;
  animation: tala-scan 3.4s linear infinite;
}}
.tala-starfield {{ position: absolute; inset: 0; }}
.tala-starfield i {{
  position: absolute; display: block; background: #ffffff;
  animation-name: tala-twinkle; animation-iteration-count: infinite;
  animation-timing-function: ease-in-out; opacity: var(--dim);
}}

.tala-sprite {{ image-rendering: pixelated; display: block; }}
.tala-cast {{
  display: flex; align-items: center; justify-content: center;
  gap: clamp(14px, 5vw, 46px);
}}
.tala-cast .side {{ animation: tala-bob 2.6s ease-in-out infinite; opacity: .95; }}
.tala-cast .side.right {{ animation-delay: 1.3s; }}
.tala-starwrap {{ position: relative; display: grid; place-items: center; }}
.tala-starwrap .core {{ animation: tala-star-pulse 2.1s ease-in-out infinite; }}
.tala-starwrap .ray {{
  position: absolute; background: {GOLD}; animation: tala-ray 1.7s ease-in-out infinite;
}}
.tala-starwrap .ray.h {{ width: 108px; height: 3px; }}
.tala-starwrap .ray.v {{ width: 3px; height: 108px; animation-delay: .42s; }}
.tala-starwrap .ray.d1, .tala-starwrap .ray.d2 {{ width: 84px; height: 3px; opacity: .5; }}
.tala-starwrap .ray.d1 {{ transform: rotate(45deg); animation-delay: .85s; }}
.tala-starwrap .ray.d2 {{ transform: rotate(-45deg); animation-delay: 1.27s; }}

.tala-wordmark {{ text-align: center; margin: .5rem 0 .2rem; }}
.tala-wordmark b {{
  display: block; color: {GOLD}; font-size: clamp(2.1rem, 8vw, 3.4rem);
  font-weight: 700; letter-spacing: .42em; text-indent: .42em; line-height: 1;
  font-family: "Courier New", ui-monospace, monospace;
  text-shadow: 3px 3px 0 {GOLD_DEEP}, 6px 6px 0 rgba(0,0,0,.45);
}}
.tala-wordmark span {{
  display: block; margin-top: .7rem; color: {INK_ON_SKY};
  font-family: "Courier New", ui-monospace, monospace;
  font-size: clamp(.56rem, 2vw, .72rem); letter-spacing: .3em; opacity: .82;
}}
.tala-prompt {{
  text-align: center; color: {GOLD}; margin: 1.6rem 0 .4rem;
  font-family: "Courier New", ui-monospace, monospace;
  font-size: clamp(.72rem, 2.4vw, .9rem); letter-spacing: .22em;
  text-transform: uppercase; animation: tala-blink 1.4s step-end infinite;
}}
.tala-hint {{
  text-align: center; color: {INK_ON_SKY}; opacity: .6; margin-bottom: .6rem;
  font-family: "Courier New", ui-monospace, monospace; font-size: .7rem;
}}

/* --- 8-bit widget skin -------------------------------------------------- */
.stButton > button {{
  font-family: "Courier New", ui-monospace, monospace;
  font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
  border-radius: 0; border: 3px solid {NAVY};
  background: rgba(0,0,0,.35); color: {INK_ON_SKY};
  box-shadow: 0 0 0 3px rgba(0,0,0,.4); transition: none;
  padding: .7rem .4rem;
}}
.stButton > button:hover {{
  border-color: {GOLD}; color: {GOLD}; background: rgba(53,64,142,.35);
  transform: translateY(-2px);
}}
/* The picked language: Streamlit's "primary" button type carries the state. */
.stButton > button[kind="primary"] {{
  background: linear-gradient(to bottom, {GOLD} 0 45%, {GOLD_DEEP} 45% 100%);
  color: #1b2559; border-color: {GOLD}; box-shadow: 0 0 18px rgba(245,216,158,.45);
}}
.stButton > button[kind="primary"]:hover {{
  color: #1b2559; background: linear-gradient(to bottom, {GOLD} 0 45%, {GOLD_DEEP} 45% 100%);
}}
.stButton > button:disabled {{ opacity: .35; }}
.tala-greet {{
  text-align: center; color: {INK_ON_SKY}; opacity: .7; margin-top: .25rem;
  font-family: "Courier New", ui-monospace, monospace; font-size: .68rem;
  letter-spacing: .08em;
}}

@media (prefers-reduced-motion: reduce) {{
  .tala-sky *, .tala-sky::after, .tala-starwrap .core, .tala-cast .side,
  .tala-prompt {{ animation: none !important; }}
  .tala-starfield i {{ opacity: .8; }}
}}
</style>
"""


def _art() -> str:
    """The sprite cast + wordmark, identical in spirit to the boot splash."""
    star = (
        '<div class="tala-starwrap">'
        '<span class="ray h"></span><span class="ray v"></span>'
        '<span class="ray d1"></span><span class="ray d2"></span>'
        + _sprite_svg(STAR, {"#": GOLD}, pixel=7, extra_class="core")
        + "</div>"
    )
    return (
        f'<div class="tala-sky">{_starfield()}</div>'
        '<div class="tala-cast">'
        f'<div class="side left">{_sprite_svg(BUBBLE, {"#": NAVY, "+": GOLD}, 5)}</div>'
        f"{star}"
        f'<div class="side right">{_sprite_svg(PIN, {"#": NAVY, "o": GOLD}, 5)}</div>'
        "</div>"
        '<div class="tala-wordmark"><b>TALA</b>'
        f'<span>{i18n.t("app.wordmark_sub")}</span>'
        f'<span>{i18n.t("app.wordmark_org")}</span></div>'
    )


def language_gate() -> None:
    """Render the language chooser and stop the script.

    Never returns: the caller reaches the rest of the app only on a later run,
    once ``i18n.is_set()`` is true."""
    st.markdown(_GATE_CSS, unsafe_allow_html=True)
    st.markdown(_art(), unsafe_allow_html=True)

    pick = st.session_state.get(i18n.SS_PICK)

    # The prompt is shown in the highlighted language once one is picked, so the
    # screen answers in your language before you have committed to it.
    preview = pick or i18n.DEFAULT_LANG
    st.session_state[i18n.SS_LANG] = preview      # temporary, for this render only
    prompt = i18n.t("gate.prompt")
    hint = i18n.t("gate.hint")
    start_label = i18n.t("gate.start")
    footer = (i18n.t("gate.selected", language=i18n.LANGS[pick]["endonym"])
              if pick else i18n.t("gate.press_start"))
    del st.session_state[i18n.SS_LANG]            # not chosen until START

    st.markdown(f'<div class="tala-prompt">▸ {prompt} ◂</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="tala-hint">{hint}</div>', unsafe_allow_html=True)

    for col, (code, meta) in zip(st.columns(len(i18n.LANGS)), i18n.LANGS.items()):
        with col:
            if st.button(meta["endonym"], key=f"tala_lang_{code}",
                         type="primary" if pick == code else "secondary",
                         use_container_width=True):
                st.session_state[i18n.SS_PICK] = code
                st.rerun()
            st.markdown(f'<div class="tala-greet">{meta["hello"]}</div>',
                        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        if st.button(f"▶  {start_label}", key="tala_start", type="primary",
                     use_container_width=True, disabled=pick is None):
            i18n.set_lang(pick)
            st.rerun()
        st.markdown(f'<div class="tala-greet">{footer}</div>', unsafe_allow_html=True)

    st.stop()
