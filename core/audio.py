"""Browser-side sound for TALA: a synth engine, not audio files.

Sound is synthesized in the visitor's browser with the Web Audio API (see
``core/sound_engine.js`` and ``docs/AUDIO.md``). There are no MP3s to download,
nothing is stored in session state, and no audio bytes ever travel through a
Streamlit delta. The engine lives on ``window.__talaSound`` and survives reruns,
so music does not restart when a trainee touches a control.

This module is the Python half:

* :func:`mount` sends the engine **once per session**, then on every run a tiny
  config script (preferences and the current area) so the music follows the page.
* :func:`cue` / :func:`special` play one sound from the server, for events the
  browser cannot see (a model finished fitting, a step was completed).
* :func:`result` decides *which* sound a page result deserves.

The engine installs a capture listener that treats the first pointer or key
event as the gesture that makes audio legal, so the language gate's first tap is
what unlocks everything that follows.
"""
from __future__ import annotations

import base64
import json
import time
from contextlib import contextmanager
from pathlib import Path

import streamlit as st

from . import i18n

SS_MUSIC_ON = "audio_music_on"
SS_MUSIC_VOLUME = "audio_music_volume"
SS_SFX_ON = "audio_sfx_on"
SS_SFX_VOLUME = "audio_sfx_volume"
SS_MUSIC_STYLE = "audio_music_style"
SS_STARTED = "audio_started"

_SS_ENGINE_SENT = "_tala_engine_sent"
_SS_CUE_N = "_tala_cue_n"
_SS_LAST_RESULT = "_tala_last_result"

ENGINE_PATH = Path(__file__).with_name("sound_engine.js")

# A result slower than this is "real compute" and earns its page signature; a
# faster one was almost certainly a cache hit and gets the short ``cached`` blip.
SLOW_RESULT_S = 0.3


def _defaults() -> None:
    """Initialize compact, per-session audio preferences."""
    st.session_state.setdefault(SS_MUSIC_ON, True)
    st.session_state.setdefault(SS_MUSIC_VOLUME, 25)
    st.session_state.setdefault(SS_SFX_ON, True)
    st.session_state.setdefault(SS_SFX_VOLUME, 65)
    st.session_state.setdefault(SS_MUSIC_STYLE, "melody")
    st.session_state.setdefault(SS_STARTED, False)


def started() -> bool:
    _defaults()
    return bool(st.session_state[SS_STARTED])


def mark_started() -> None:
    """Record that the language gate's Continue button was pressed."""
    _defaults()
    st.session_state[SS_STARTED] = True


def style_options() -> list[tuple[str, str]]:
    """``(value, i18n key)`` pairs for the music style select in Settings."""
    return [("melody", "audio.style_melody"), ("ambience", "audio.style_ambience")]


def _settings(target) -> None:
    """Render shared Music and SFX controls in a Streamlit container/sidebar."""
    _defaults()
    controls = target.container(key="audio-controls")
    music, sfx = controls.columns(2)
    with music:
        music.toggle(i18n.t("audio.music"), key=SS_MUSIC_ON)
        music.slider(
            i18n.t("audio.volume", name=i18n.t("audio.music")), 0, 100,
            key=SS_MUSIC_VOLUME, disabled=not st.session_state[SS_MUSIC_ON],
        )
    with sfx:
        sfx.toggle(i18n.t("audio.sfx"), key=SS_SFX_ON)
        sfx.slider(
            i18n.t("audio.volume", name=i18n.t("audio.sfx")), 0, 100,
            key=SS_SFX_VOLUME, disabled=not st.session_state[SS_SFX_ON],
        )


def gate_settings() -> None:
    """Settings shown on the language gate, so a trainee can choose sound up front."""
    with st.expander(i18n.t("audio.gate_heading"), expanded=False):
        _settings(st)


def sidebar_settings() -> None:
    """Persistent controls available throughout the app."""
    st.sidebar.markdown(f"### {i18n.t('audio.heading')}")
    _settings(st.sidebar)


def _html_script(js: str, *, marker: str = "") -> None:
    """Run ``js`` in the app document through the supported ``st.html`` hook.

    Streamlit's sanitizer accepts a small executable ``st.html`` script but can
    discard a long controller containing browser event-handler syntax. So the
    HTML carries only a base64 bootstrap, and the code is decoded and injected
    from it. That avoids ``eval()``, which hosted Content Security Policies
    commonly disallow. ``marker`` is an inert element the engine's CSS hides, so
    the element container this renders into leaves no visible gap.
    """
    encoded = base64.b64encode(js.encode("utf-8")).decode("ascii")
    st.html(
        f"""
        {marker}
        <script>
        (() => {{
          const script = document.createElement("script");
          script.textContent = atob("{encoded}");
          document.head.appendChild(script);
          script.remove();
        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def _config_js(area: str) -> str:
    _defaults()
    prefs = {
        "musicOn": bool(st.session_state[SS_MUSIC_ON]),
        "musicVol": int(st.session_state[SS_MUSIC_VOLUME]),
        "sfxOn": bool(st.session_state[SS_SFX_ON]),
        "sfxVol": int(st.session_state[SS_SFX_VOLUME]),
        "style": str(st.session_state[SS_MUSIC_STYLE]),
    }
    return (
        f"window.__talaSound?.setPrefs({json.dumps(prefs)});"
        f"window.__talaSound?.area({json.dumps(area)});"
    )


def mount(area: str) -> None:
    """Install/update the browser sound engine and tell it which area we are in.

    ``area`` is ``'gate'``, ``'home'``, ``'text'`` or ``'geo'`` and picks the
    music. The engine source is sent **once per session**: the DOM survives
    reruns, so later runs send only the small config. Engine and config travel
    in the same script on that first run, so the config can never run before
    the engine exists.
    """
    js = _config_js(area)
    if not st.session_state.get(_SS_ENGINE_SENT):
        js = ENGINE_PATH.read_text(encoding="utf-8") + "\n" + js
        st.session_state[_SS_ENGINE_SENT] = True
    _html_script(js)


def _next_nonce() -> int:
    n = int(st.session_state.get(_SS_CUE_N, 0)) + 1
    st.session_state[_SS_CUE_N] = n
    return n


def _call(expr: str) -> None:
    """Emit a one-line call on the engine. The nonce makes the markup differ on
    every call, so Streamlit re-executes it even for a repeated sound."""
    n = _next_nonce()
    _html_script(f"/* {n} */ window.__talaSound?.{expr};", marker=f'<i class="tala-cue" data-n="{n}"></i>')


def cue(name: str, arg=None, delay_ms: int = 0) -> None:
    """Play one sound from the server (a key of the engine's ``S`` table)."""
    _call(f"play({json.dumps(name)}, {json.dumps(arg)}, {int(delay_ms)})")


def special(name: str) -> None:
    """Play a fanfare (``'trackDone'`` or ``'fullSky'``), then music turns to the
    harana until the area changes."""
    _call(f"special({json.dumps(name)})")


def boot_timeline(from_pct: int, seconds: float, segments: list[float]) -> None:
    """Schedule the boot bar's progress ticks and the ready chime. ``segments``
    are the CSS fill delays (seconds) of the bar segments filled in the tail."""
    _call(f"bootTimeline({int(from_pct)}, {float(seconds):.2f}, {json.dumps([round(s, 3) for s in segments])})")


@contextmanager
def result(sig: str, params: tuple):
    """Wrap a page's main compute and play the sound its outcome deserves.

    >>> with audio.result("text5", (n_topics, seed, min_df)):
    ...     topics = nlp.lda_topics(...)

    Unchanged ``(sig, params)`` since the last run is a plain rerun: silence.
    Changed and slow plays the page signature ``sig``; changed but fast (a cache
    hit) plays ``cached``. Exceptions propagate and play nothing.
    """
    started_at = time.monotonic()
    yield
    elapsed = time.monotonic() - started_at
    last = st.session_state.setdefault(_SS_LAST_RESULT, {})
    params = tuple(params)
    if sig in last and last[sig] == params:
        return
    last[sig] = params
    cue(sig if elapsed >= SLOW_RESULT_S else "cached")
