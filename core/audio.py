"""Browser-side sound for TALA's game-like training experience.

Audio playback belongs in the browser, not in Streamlit's session state. This
module mounts a tiny component which owns three persistent ``<audio>`` elements
in the parent document: looping background music, the language-gate start cue,
and a general button-click cue. Keeping them outside a rerun's delta tree means
music does not restart whenever a trainee changes a control.

The click listener is deliberately installed in capture phase. The START cue and
the first music ``play()`` call therefore happen inside the actual browser click
event, which satisfies modern autoplay policies. Browsers may still mute or
block sound according to a user's own settings; the audio controls always remain
available to opt in, mute, or adjust volumes.
"""
from __future__ import annotations

import base64
import json

import streamlit as st

from . import i18n


# Community Cloud's static-file handler does not classify MP3 as normal media in
# every Streamlit release. GitHub Raw returns the correct ``audio/mpeg`` type;
# keep the app's static URLs as a same-origin fallback for local installs.
_GITHUB_AUDIO_ROOT = (
    "https://raw.githubusercontent.com/MicoMagtira/"
    "TALA-Text-And-Location-Analytics/main/static/audio"
)
AUDIO_URLS = {
    "music": f"{_GITHUB_AUDIO_ROOT}/tala-background.mp3",
    "start": f"{_GITHUB_AUDIO_ROOT}/tala-start.mp3",
    "click": f"{_GITHUB_AUDIO_ROOT}/tala-click.mp3",
}
STATIC_AUDIO_URLS = {
    "music": "/app/static/audio/tala-background.mp3",
    "start": "/app/static/audio/tala-start.mp3",
    "click": "/app/static/audio/tala-click.mp3",
}

SS_MUSIC_ON = "audio_music_on"
SS_MUSIC_VOLUME = "audio_music_volume"
SS_SFX_ON = "audio_sfx_on"
SS_SFX_VOLUME = "audio_sfx_volume"
SS_STARTED = "audio_started"

_IOS_VOLUME_CSS = """
<style>
.tala-ios-volume-note {
  display: none;
  margin: .45rem 0 0;
  color: inherit;
  font-size: .82rem;
}
html.tala-volume-locked .st-key-audio-controls [data-testid="stSlider"] {
  display: none !important;
}
html.tala-volume-locked .st-key-audio-controls .tala-ios-volume-note {
  display: block;
}
</style>
"""


def _defaults() -> None:
    """Initialize compact, per-session audio preferences."""
    st.session_state.setdefault(SS_MUSIC_ON, True)
    st.session_state.setdefault(SS_MUSIC_VOLUME, 25)
    st.session_state.setdefault(SS_SFX_ON, True)
    st.session_state.setdefault(SS_SFX_VOLUME, 65)
    st.session_state.setdefault(SS_STARTED, False)


def started() -> bool:
    _defaults()
    return bool(st.session_state[SS_STARTED])


def mark_started() -> None:
    """Record that the gate START button unlocked browser audio for this session."""
    _defaults()
    st.session_state[SS_STARTED] = True


def _settings(target, *, compact: bool = False) -> None:
    """Render shared Music and SFX controls in a Streamlit container/sidebar."""
    _defaults()
    controls = target.container(key="audio-controls")
    controls.markdown(_IOS_VOLUME_CSS, unsafe_allow_html=True)
    if compact:
        controls.caption(i18n.t("audio.gate_hint"))

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
    controls.markdown(
        f'<p class="tala-ios-volume-note">{i18n.t("audio.ios_volume_note")}</p>',
        unsafe_allow_html=True,
    )


def gate_settings() -> None:
    """Settings shown before START, so a trainee can choose sound up front."""
    with st.expander(i18n.t("audio.gate_heading"), expanded=False):
        _settings(st, compact=True)


def sidebar_settings() -> None:
    """Persistent controls available throughout the app."""
    st.sidebar.markdown(f"### {i18n.t('audio.heading')}")
    _settings(st.sidebar)


def mount(
    *,
    start_labels: tuple[str, ...] = (),
    play_music: bool | None = None,
    start_music_on_interaction: bool = False,
) -> None:
    """Install/update the browser audio manager without rendering a player.

    ``start_labels`` is only supplied on the language gate. It lets the capture
    listener distinguish the START button from every other Streamlit button.
    ``start_music_on_interaction`` lets the language gate begin its loop on the
    first visitor interaction when the browser blocks unmuted autoplay.
    """
    _defaults()
    if play_music is None:
        play_music = started()
    state = {
        "urls": AUDIO_URLS,
        "fallbackUrls": STATIC_AUDIO_URLS,
        "musicOn": bool(st.session_state[SS_MUSIC_ON]),
        "musicVolume": int(st.session_state[SS_MUSIC_VOLUME]) / 100,
        "sfxOn": bool(st.session_state[SS_SFX_ON]),
        "sfxVolume": int(st.session_state[SS_SFX_VOLUME]) / 100,
        "startLabels": list(start_labels),
        "playMusic": bool(play_music),
        "startMusicOnInteraction": start_music_on_interaction,
    }
    payload = json.dumps(state).replace("</", "<\\/")
    # Streamlit's sanitizer accepts a small executable ``st.html`` script but
    # can discard a long controller containing browser event-handler syntax.
    # Keep the controller data-only in the HTML payload, then inject it from
    # the supported JavaScript-enabled ``st.html`` bootstrap. This avoids
    # ``eval()``, which hosted Content Security Policies commonly disallow.
    controller = f"""
        (() => {{
          try {{
            const host = window.parent === window ? window : window.parent;
            const doc = host.document;
            const config = {payload};
            const manager = host.__talaAudio || (host.__talaAudio = {{}});
            // Terminal/local development must play the MP3 files in this
            // checkout, not the versions already published on GitHub. Deployed
            // apps keep GitHub Raw as the primary MIME-safe delivery route.
            const localHosts = new Set(['localhost', '127.0.0.1', '::1']);
            const useLocalAssets = localHosts.has(host.location.hostname)
              || host.location.hostname.endsWith('.local');
            const primaryUrls = useLocalAssets ? config.fallbackUrls : config.urls;
            const secondaryUrls = useLocalAssets ? config.urls : config.fallbackUrls;
            // iPhone Safari keeps media volume under the device's physical
            // controls. Feature-detect the locked property instead of relying
            // on user-agent text, so iPads/newer Safari remain supported.
            const volumeProbe = doc.createElement('audio');
            let volumeLocked = false;
            try {{
              volumeProbe.volume = 0.37;
              volumeLocked = volumeProbe.volume !== 0.37;
            }} catch (_) {{
              volumeLocked = true;
            }}
            doc.documentElement.classList.toggle('tala-volume-locked', volumeLocked);

            const makeAudio = (name, src, fallbackSrc, loop, preload) => {{
              let audio = doc.getElementById(`tala-audio-${{name}}`);
              if (!audio) {{
                audio = doc.createElement('audio');
                audio.id = `tala-audio-${{name}}`;
                audio.loop = loop;
                audio.preload = preload;
                audio.setAttribute('aria-hidden', 'true');
                audio.style.display = 'none';
                doc.body.appendChild(audio);
              }}
              if (audio.dataset.talaPrimaryUrl !== src) {{
                audio.dataset.talaPrimaryUrl = src;
                audio.dataset.talaFallbackUrl = fallbackSrc;
                audio.dataset.talaUsingFallback = 'false';
                audio.src = src;
                audio.onerror = () => {{
                  if (audio.dataset.talaUsingFallback === 'true' || !fallbackSrc) return;
                  audio.dataset.talaUsingFallback = 'true';
                  audio.src = fallbackSrc;
                  audio.load();
                }};
              }}
              return audio;
            }};

            manager.music = makeAudio(
              'music', primaryUrls.music, secondaryUrls.music, true, 'metadata'
            );
            manager.start = makeAudio(
              'start', primaryUrls.start, secondaryUrls.start, false, 'auto'
            );
            manager.click = makeAudio(
              'click', primaryUrls.click, secondaryUrls.click, false, 'auto'
            );
            manager.config = config;
            // Keep the loop inaudible during the START cue, even if Streamlit
            // has already rerun and supplied a fresh configuration.
            manager.music.volume = manager.waitingForStartCue ? 0 : config.musicVolume;
            manager.start.volume = config.sfxVolume;
            manager.click.volume = config.sfxVolume;

            manager.play = (name) => {{
              if (!manager.config.sfxOn) return;
              const sound = manager[name];
              if (!sound) return;
              sound.currentTime = 0;
              sound.play().catch(() => {{}});
            }};
            manager.playMusic = () => {{
              if (manager.waitingForStartCue) return;
              if (!manager.config.musicOn) {{
                manager.music.pause();
                return;
              }}
              manager.music.play().catch(() => {{}});
            }};
            manager.playStartThenMusic = () => {{
              // Do not overlap the gate's distinct START cue with the loop.
              // If SFX is muted, there is no cue to wait for.
              if (!manager.config.sfxOn) {{
                manager.waitingForStartCue = false;
                manager.playMusic();
                return;
              }}
              manager.waitingForStartCue = true;
              // Starting the loop muted inside this real click event preserves
              // browser media permission. Restoring its volume after the cue is
              // reliable where an asynchronous second play() would be blocked.
              if (manager.config.musicOn) {{
                manager.music.volume = 0;
                manager.music.play().catch(() => {{}});
              }} else {{
                manager.music.pause();
              }}
              // Store this handler on the parent-document <audio> element.
              // A Streamlit rerun may replace this component iframe before the
              // cue ends, but the parent audio element and its inline handler
              // remain alive long enough to resume the loop.
              const resumeScript =
                "var audio=window.__talaAudio;if(audio){{audio.waitingForStartCue=false;"
                + "if(audio.config&&audio.config.musicOn){{audio.music.volume=audio.config.musicVolume;}}"
                + "else{{audio.music.pause();}}}}";
              manager.start.onended = null;
              manager.start.setAttribute('onended', resumeScript);
              manager.start.currentTime = 0;
              manager.start.play().catch(() => {{
                // A browser may reject a play request; do not leave music paused.
                manager.waitingForStartCue = false;
                manager.start.removeAttribute('onended');
                manager.music.volume = manager.config.musicVolume;
                manager.playMusic();
              }});
            }};

            if (manager.clickHandler) {{
              doc.removeEventListener('click', manager.clickHandler, true);
            }}
            manager.clickHandler = (event) => {{
              const target = event.target;
              if (!(target instanceof host.Element)) return;
              // Streamlit navigation uses links, Learn panels use <summary>,
              // and its radios, checkboxes, and toggles are label/BaseWeb
              // controls. Treat each as an app interaction, not only literal
              // <button> elements.
              const control = target.closest(
                'button, a[href], summary, label, input, select, [role="button"], '
                + '[role="tab"], [role="switch"], [role="radio"], [role="checkbox"], '
                + '[role="menuitem"], [data-baseweb="radio"], [data-baseweb="checkbox"]'
              );
              if (!control || control.disabled || control.getAttribute('aria-disabled') === 'true') return;
              const label = (control.innerText || control.textContent || '').trim();
              const isStart = manager.config.startLabels.some(
                (startLabel) => startLabel && label.includes(startLabel)
              );
              if (isStart) {{
                manager.playStartThenMusic();
              }} else {{
                manager.play('click');
                if (manager.config.startMusicOnInteraction) manager.playMusic();
              }}
            }};
            doc.addEventListener('click', manager.clickHandler, true);

            if (config.playMusic) manager.playMusic();
          }} catch (_) {{
            // Sound is an enhancement. A restrictive browser/CSP must not stop TALA.
          }}
        }})();
        """
    encoded_controller = base64.b64encode(controller.encode("utf-8")).decode("ascii")
    st.html(
        f"""
        <script>
        (() => {{
          const script = document.createElement("script");
          script.textContent = atob("{encoded_controller}");
          document.head.appendChild(script);
          script.remove();
        }})();
        </script>
        """,
        unsafe_allow_javascript=True,
    )
