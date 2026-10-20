"""Save and resume: one small browser cookie, ``tala_prefs``.

Why a cookie and not a server store: the app runs on a ~1 GB shared container
with no database, and a trainee on a workshop PC expects "close the tab, come
back tomorrow, carry on". A cookie costs the server nothing and is sent back to
us on the first request of the next session, so ``restore()`` can run before the
language gate is even considered.

The payload is base64url(JSON) with ``{"v": 1, ...}`` and holds **only keys and
parameters** (the house rule from ``core/data_loader.py``): never a DataFrame,
never an upload's bytes. An upload is remembered by its content key; if the
shared cache has since evicted it, ``restore()`` falls back to the bundled
dataset rather than failing.

Everything read back is validated field by field and bad or old data is
ignored silently: a cookie is user-editable input, and a stale one from an older
release must never be able to break the app.

Writing is a tiny ``st.html`` script (the server cannot set cookies from a
Streamlit run) and happens only when the payload hash changed.
"""
from __future__ import annotations

import base64
import hashlib
import json

import streamlit as st

COOKIE = "tala_prefs"
VERSION = 1
MAX_AGE = 180 * 24 * 3600          # 180 days
MAX_COOKIE_BYTES = 3_800           # browsers cap a cookie near 4 KB
MAX_STOPWORDS_CHARS = 1_000
_MAX_LABEL = 120
_MAX_KEY = 200

SS_RESTORED = "_tala_restored"
SS_HASH = "_tala_cookie_hash"
SS_FORGET = "_tala_forget_pending"


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------
def encode(payload: dict) -> str:
    """Payload -> cookie value, <= MAX_COOKIE_BYTES.

    If it is too big, custom stopwords are dropped first (the only free-text,
    user-sized field), then the done list and label, so the cookie always fits."""
    data = dict(payload)

    def _enc(d: dict) -> str:
        raw = json.dumps(d, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    out = _enc(data)
    for field in ("custom_sw", "done", "label"):
        if len(out) <= MAX_COOKIE_BYTES:
            break
        data.pop(field, None)
        out = _enc(data)
    return out


def decode(value: str | None) -> dict | None:
    """Cookie value -> payload dict, or None for anything corrupt or foreign."""
    if not value or not isinstance(value, str) or len(value) > 8_000:
        return None
    try:
        padded = value + "=" * (-len(value) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
    except Exception:
        return None
    if not isinstance(data, dict) or data.get("v") != VERSION:
        return None
    return data


# ---------------------------------------------------------------------------
# Collect (session -> payload)
# ---------------------------------------------------------------------------
def collect() -> dict:
    """Snapshot the session's saveable state as plain JSON values."""
    from . import audio, data_loader as dl, i18n, tracks, ui

    ss = st.session_state
    out: dict = {"v": VERSION}
    if i18n.is_set():
        out["lang"] = i18n.current()
    for short, key in (("music_on", audio.SS_MUSIC_ON), ("music_vol", audio.SS_MUSIC_VOLUME),
                       ("sfx_on", audio.SS_SFX_ON), ("sfx_vol", audio.SS_SFX_VOLUME),
                       ("style", audio.SS_MUSIC_STYLE), ("pal", ui.SS_PALETTE),
                       ("seq", ui.SS_SEQ), ("learn", ui.SS_TEACH), ("tl", ui.SS_USE_TL)):
        if key in ss:
            out[short] = ss[key]
    sw = str(ss.get(ui.SS_CUSTOM_SW, "") or "").strip()[:MAX_STOPWORDS_CHARS]
    if sw:
        out["custom_sw"] = sw
    if dl.SS_SOURCE_KEY in ss:
        out["src"] = ss[dl.SS_SOURCE_KEY]
        out["text"] = ss.get(dl.SS_TEXT_COL)
        out["lon"] = ss.get(dl.SS_LON_COL)
        out["lat"] = ss.get(dl.SS_LAT_COL)
        out["label"] = str(ss.get(dl.SS_SOURCE, ""))[:_MAX_LABEL]
    if dl.SS_CLUSTER_PARAMS in ss:
        out["cluster"] = list(ss[dl.SS_CLUSTER_PARAMS])
    if dl.SS_GEN_PARAMS in ss:
        out["gen"] = list(ss[dl.SS_GEN_PARAMS])
    done = sorted(ss.get(tracks.SS_DONE, ()))
    if done:
        out["done"] = done
    if ss.get(tracks.SS_LAST_PAGE):
        out["last"] = ss[tracks.SS_LAST_PAGE]
    return out


# ---------------------------------------------------------------------------
# Apply (payload -> session), validated
# ---------------------------------------------------------------------------
def _num(v, lo: float, hi: float) -> float | None:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    return float(v) if lo <= v <= hi else None


def apply(data: dict) -> None:
    """Validate ``data`` and write the good fields into session state.

    Order matters: the dataset goes first because ``dl.set_active`` resets the
    geo chain, and the saved cluster parameters are restored after it."""
    from . import audio, data_loader as dl, i18n, tracks, ui
    from .viz import categorical_names, sequential_names

    ss = st.session_state
    lang = data.get("lang")
    if isinstance(lang, str) and lang in i18n.LANGS:
        i18n.set_lang(lang)

    for short, key in (("music_on", audio.SS_MUSIC_ON), ("sfx_on", audio.SS_SFX_ON),
                       ("learn", ui.SS_TEACH), ("tl", ui.SS_USE_TL)):
        if isinstance(data.get(short), bool):
            ss[key] = data[short]
    for short, key in (("music_vol", audio.SS_MUSIC_VOLUME), ("sfx_vol", audio.SS_SFX_VOLUME)):
        n = _num(data.get(short), 0, 100)
        if n is not None:
            ss[key] = int(n)
    if data.get("style") in {k for k, _ in audio.style_options()}:
        ss[audio.SS_MUSIC_STYLE] = data["style"]
    if data.get("pal") in categorical_names():
        ss[ui.SS_PALETTE] = data["pal"]
    if data.get("seq") in sequential_names():
        ss[ui.SS_SEQ] = data["seq"]
    sw = data.get("custom_sw")
    if isinstance(sw, str):
        ss[ui.SS_CUSTOM_SW] = sw[:MAX_STOPWORDS_CHARS]

    _apply_dataset(data, dl)

    cl = data.get("cluster")
    if isinstance(cl, list) and len(cl) == 2:
        eps, ms = _num(cl[0], 1, 1_000_000), _num(cl[1], 1, 10_000)
        if eps is not None and ms is not None:
            ss[dl.SS_CLUSTER_PARAMS] = (eps, int(ms))
    gen = data.get("gen")
    if isinstance(gen, list) and len(gen) == 2:
        if gen[0] == "grid" and _num(gen[1], 1, 10_000_000) is not None:
            ss[dl.SS_GEN_PARAMS] = ("grid", float(gen[1]))
        elif gen[0] == "centroids" and isinstance(gen[1], bool):
            ss[dl.SS_GEN_PARAMS] = ("centroids", gen[1])

    known = set(tracks.ALL_PAGES)   # pages from older releases (text_*, geo_*) are dropped
    done = data.get("done")
    if isinstance(done, list):
        ss[tracks.SS_DONE] = sorted({p for p in done if isinstance(p, str) and p in known})
    last = data.get("last")
    if isinstance(last, str) and last in known:
        ss[tracks.SS_LAST_PAGE] = last
    # A returning visitor has already had the celebration for finished chapters.
    finished = [c for c in tracks.CHAPTERS if tracks.track_complete(c)]
    if finished:
        celebrated = set(ss.get(tracks.SS_CELEBRATED, ())) | set(finished)
        if len(finished) == len(tracks.CHAPTERS):
            celebrated.add("sky")
        ss[tracks.SS_CELEBRATED] = sorted(celebrated)


def _apply_dataset(data: dict, dl) -> None:
    """Re-point the session at the saved dataset, or leave the bundled one."""
    key = data.get("src")
    if not isinstance(key, str) or not key or len(key) > _MAX_KEY:
        return
    df = dl.dataset(key)
    if df is None:                       # evicted upload: ensure_loaded() picks the bundled set
        return
    cols = set(map(str, df.columns))

    def _col(name):
        return name if isinstance(name, str) and name in cols else None

    text, lon, lat = _col(data.get("text")), _col(data.get("lon")), _col(data.get("lat"))
    g_text, _, _ = dl.guess_columns(df)
    label = data.get("label")
    if not (isinstance(label, str) and label):
        label = dl.BUNDLED_LABEL if key == dl.BUNDLED_KEY else key
    dl.set_active(key, text or g_text, lon, lat, label[:_MAX_LABEL])


# ---------------------------------------------------------------------------
# Browser I/O
# ---------------------------------------------------------------------------
def _read_cookie() -> str | None:
    try:
        return st.context.cookies.get(COOKIE)
    except Exception:
        return None


def _write_js(js: str) -> None:
    from . import audio

    audio._html_script(js, marker='<i class="tala-cue"></i>')


def restore() -> None:
    """Load saved prefs once per session. Call right after ``set_page_config``,
    before the language gate: a restored language makes ``i18n.is_set()`` true,
    so returning visitors skip the gate."""
    ss = st.session_state
    if ss.get(SS_RESTORED):
        return
    ss[SS_RESTORED] = True
    if ss.pop(SS_FORGET, False):
        _write_js(f'document.cookie="{COOKIE}=; Max-Age=0; Path=/; SameSite=Lax";')
        return
    raw = _read_cookie()
    data = decode(raw)
    if data is None:
        return
    try:
        apply(data)
    except Exception:
        return                           # never let a bad cookie block the app
    ss[SS_HASH] = hashlib.sha256((raw or "").encode()).hexdigest()


def save() -> None:
    """Write the cookie if the payload changed. Call after ``nav.run()``."""
    ss = st.session_state
    value = encode(collect())
    digest = hashlib.sha256(value.encode()).hexdigest()
    if ss.get(SS_HASH) == digest:
        return
    ss[SS_HASH] = digest
    _write_js(f'document.cookie="{COOKIE}={value}; Max-Age={MAX_AGE}; Path=/; SameSite=Lax";')


def forget() -> None:
    """"Forget me on this computer": expire the cookie, wipe the session, go to the gate.

    The expiry script is emitted on the *next* run (by ``restore``), because a
    script sent right before ``st.rerun()`` may never reach the browser. The
    pending flag survives the wipe, and the cleared ``_tala_restored`` flag
    lets ``restore`` run once more, where it expires the cookie instead of
    reading it back."""
    st.session_state.clear()
    st.session_state[SS_FORGET] = True
    st.rerun()
