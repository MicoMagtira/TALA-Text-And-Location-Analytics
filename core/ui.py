"""Shared UI helpers: header, footer, sidebar, track flow, and 'Learn' panels.

The 'Learn' expanders turn each page into live teaching material by pairing the
concept with the equivalent code from the source notebook / lab.

Every user-visible string here goes through :func:`core.i18n.t`, so the app
renders in the language chosen on the boot gate. Anything without a translation
falls back to English per key, which is what lets English copy be improved
without waiting on four translations.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from . import audio, data_loader as dl
from . import i18n, tracks
from .viz import categorical_names, sequential_names, load_css

ASSETS = Path(__file__).resolve().parent.parent / "assets"

SS_PALETTE = "cat_palette"
SS_SEQ = "seq_palette"
SS_TEACH = "teach_mode"
SS_CUSTOM_SW = "custom_stopwords"
SS_USE_TL = "use_tagalog"
SS_LANG_WIDGET = "lang_switcher"

# Which pill each page sits under. Kept here rather than passed per page so a
# page cannot drift out of its section when titles are edited.
_PILL = {"home": "pill.overview", "text": "pill.text", "geo": "pill.geo"}


def inject_css() -> None:
    css_path = ASSETS / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{load_css(str(css_path))}</style>", unsafe_allow_html=True)


def header() -> None:
    st.markdown(
        f"""
        <div class="tala-header">
          <h1>🌟 {i18n.t("app.title")}</h1>
          <div class="tala-sub">{i18n.t("app.subtitle")}</div>
          <div class="tala-dev">{i18n.t("app.developer")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        f"""
        <div class="tala-footer">
          <strong>{i18n.t("app.title")}</strong> · {i18n.t("app.developer")}<br>
          {i18n.t("app.footer")}
        </div>
        """,
        unsafe_allow_html=True,
    )


def source_label() -> str:
    """The active dataset's name, localized when it is the bundled example.

    Uploads keep the user's own filename — translating that would be wrong."""
    src = st.session_state.get(dl.SS_SOURCE, "n/a")
    return i18n.t("data.bundled_label") if src == dl.BUNDLED_LABEL else src


def _on_language_change() -> None:
    """Commit a sidebar language switch.

    Switching costs nothing heavy: only the render layer is localized, so the
    shared geo layers and fitted models stay in cache and are reused verbatim
    in the new language."""
    i18n.set_lang(st.session_state[SS_LANG_WIDGET])


def sidebar_controls() -> None:
    """Global sidebar: language, sound, a Settings expander, then the dataset caption."""
    dl.ensure_loaded()

    # Language first: a trainee who picked the wrong card on the gate, or a
    # trainer demoing the same page in two languages, should not have to reload.
    st.sidebar.markdown(f"### {i18n.t('side.language')}")
    st.session_state.setdefault(SS_LANG_WIDGET, i18n.current())
    st.sidebar.selectbox(
        i18n.t("side.language_pick"), list(i18n.LANGS), key=SS_LANG_WIDGET,
        format_func=i18n.label, on_change=_on_language_change,
        label_visibility="collapsed",
    )

    audio.sidebar_settings()

    # Everything a trainee rarely touches lives behind one expander, so the
    # sidebar is just language, sound and the page list.
    with st.sidebar.expander(i18n.t("side.settings"), expanded=False):
        st.session_state.setdefault(SS_PALETTE, categorical_names()[0])
        st.session_state.setdefault(SS_SEQ, sequential_names()[0])
        st.selectbox(i18n.t("side.palette_cat"), categorical_names(), key=SS_PALETTE)
        st.selectbox(i18n.t("side.palette_seq"), sequential_names(), key=SS_SEQ)

        st.session_state.setdefault(SS_USE_TL, True)
        st.checkbox(i18n.t("side.use_tagalog"), key=SS_USE_TL)
        st.session_state.setdefault(SS_CUSTOM_SW, "")
        st.text_area(
            i18n.t("side.custom_stopwords"), key=SS_CUSTOM_SW, height=90,
            placeholder=i18n.t("side.custom_placeholder"),
        )

        st.session_state.setdefault(SS_TEACH, True)
        st.toggle(i18n.t("side.show_learn"), key=SS_TEACH)

        styles = dict(audio.style_options())
        st.selectbox(i18n.t("audio.style"), list(styles), key=audio.SS_MUSIC_STYLE,
                     format_func=lambda v: i18n.t(styles[v]))

        # Workshop PCs are shared: let a trainee wipe what TALA saved here.
        if st.button(i18n.t("persist.forget"), key="tala_forget",
                     help=i18n.t("persist.forget_help")):
            from . import persist

            persist.forget()

    st.sidebar.markdown("---")
    st.sidebar.caption(i18n.t("side.data", source=source_label()))
    st.sidebar.caption(i18n.t("side.rows",
                              rows=f"{len(dl.active_df()):,}",
                              column=st.session_state.get(dl.SS_TEXT_COL)))


def palette() -> str:
    return st.session_state.get(SS_PALETTE, categorical_names()[0])


def seq_palette() -> str:
    return st.session_state.get(SS_SEQ, sequential_names()[0])


def stopwords() -> set:
    from . import preprocess

    return preprocess.build_stopwords(
        st.session_state.get(SS_CUSTOM_SW, ""),
        st.session_state.get(SS_USE_TL, True),
    )


# ---------------------------------------------------------------------------
# Page scaffolding — every page renders through these two calls
# ---------------------------------------------------------------------------
def page_header(page: str, section: str) -> None:
    """Pill + title + blurb, resolved from the catalog by page name.

    ``page`` is the view's module stem (``text_3_sentiment``), which is also the
    key prefix and the name of its Learn essay file. One identifier, so a page
    cannot drift out of sync with its own translations.

    Track pages get a compact header and the progress strip, and record
    themselves as the last page visited (Home's "Continue" card reads it). Only
    Home keeps the big banner (``header()``, drawn by app.py)."""
    st.markdown(f'<span class="tala-pill">{i18n.t(_PILL[section])}</span>',
                unsafe_allow_html=True)
    st.markdown(f"## {i18n.t(f'{page}.title')}")
    pos = tracks.position(page)
    if pos:
        st.session_state[tracks.SS_LAST_PAGE] = page
        _progress_strip(page, *pos)
    blurb = i18n.t(f"{page}.blurb")
    if blurb and blurb != f"{page}.blurb":
        st.markdown(blurb)


def strip_html(track: str, current: str | None = None) -> str:
    """Pixel progress segments for a track as static HTML (done / current / todo)."""
    done = tracks.done_pages()
    segs = []
    for p in tracks.TRACKS[track]:
        state = "current" if p == current else ("done" if p in done else "todo")
        segs.append(f'<i class="tala-seg tala-seg-{state}"></i>')
    return f'<div class="tala-segs">{"".join(segs)}</div>'


def _progress_strip(page: str, track: str, index: int, total: int) -> None:
    """``TEXT TRACK . 3 / 8`` plus one clickable pixel segment per page.

    Segments are ``st.page_link`` rather than plain anchors: an anchor would
    reload the browser tab and start a fresh session, losing the trainee's
    progress. Each sits in a keyed container so CSS can colour it by state."""
    st.caption(f"{i18n.t(f'track.label_{track}')} · {index} / {total}")
    done = tracks.done_pages()
    with st.container(key="tala-strip"):
        for col, p in zip(st.columns(total, gap="small"), tracks.TRACKS[track]):
            state = "current" if p == page else ("done" if p in done else "todo")
            with col, st.container(key=f"tala-seg-{state}-{p}"):
                n = tracks.TRACKS[track].index(p) + 1
                st.page_link(tracks.path_of(p), label=str(n),
                             help=i18n.t(f"{p}.nav"), disabled=(p == page))


def page_done(page: str) -> None:
    """Mark this page's step finished; if that completed a track, show the card.

    The card is tied to the page that completed the track, so it stays put across
    reruns of that page instead of vanishing on the first slider touch."""
    was_done = page in tracks.done_pages()
    tracks.mark_done(page)
    if not was_done and tracks.track_of(page):
        st.toast(i18n.t("track.step_done"), icon="✅")
    just = st.session_state.get(tracks.SS_JUST_COMPLETED)
    if just and just[0] == page:
        _track_complete_card(just[1])


def _track_complete_card(track: str) -> None:
    other = "geo" if track == "text" else "text"
    with st.container(border=True, key="tala-complete"):
        st.markdown(f"### {i18n.t(f'track.complete_{track}')}")
        st.write(i18n.t(f"track.covered_{track}"))
        c1, c2 = st.columns(2)
        with c1:
            if not tracks.track_complete(other):
                st.page_link(tracks.path_of(tracks.first_todo(other)),
                             label=i18n.t(f"track.start_{other}"), icon="▶")
        with c2:
            st.page_link(tracks.path_of("home"), label=i18n.t("track.go_home"), icon="🏠")


def track_footer(page: str) -> None:
    """Back and Next at the foot of a track page: the page's only way onward.

    On a track's last page Next becomes "start the other track" (while it is
    unfinished) or "Finish, Home"."""
    track = tracks.track_of(page)
    if track is None:
        return
    prev, nxt = tracks.neighbours(page)
    other = "geo" if track == "text" else "text"
    if nxt:
        target, label = nxt, i18n.t("track.next")
    elif not tracks.track_complete(other):
        target, label = tracks.first_todo(other), i18n.t(f"track.start_{other}")
    else:
        target, label = "home", i18n.t("track.finish")
    with st.container(key="tala-footnav"):
        left, right = st.columns(2)
        with left:
            if prev:
                st.page_link(tracks.path_of(prev), label=i18n.t("track.back"),
                             help=i18n.t(f"{prev}.nav"))
        with right, st.container(key="tala-footnav-next"):
            st.page_link(tracks.path_of(target), label=label)


def warn(msg: str) -> None:
    """``st.warning`` that also plays the warning sound."""
    st.warning(msg)
    audio.cue("warn")


def error(msg: str) -> None:
    """``st.error`` that also plays the error sound."""
    st.error(msg)
    audio.cue("error")


def info(msg: str) -> None:
    """``st.info``; silent by design."""
    st.info(msg)


def locked(msg: str, link_page: str, link_label: str) -> None:
    """A friendly card for a page that genuinely cannot run (no coordinates, say).

    Shows the reason and a link to where it is fixed, plays ``locked``, draws the
    track footer so the page is never a dead end, then ends the run. Callers do
    not need their own ``st.stop()``."""
    audio.cue("locked")
    with st.container(border=True, key="tala-locked"):
        st.markdown(f"#### 🔒 {msg}")
        st.page_link(tracks.path_of(link_page), label=link_label, icon="➡️")
    last = st.session_state.get(tracks.SS_LAST_PAGE)
    if last:
        track_footer(last)
    st.stop()


def learn_page(page: str, code: str | None = None, lang: str = "python") -> None:
    """Render a page's Learn essay from ``locales/pages/<lang>/<page>.md``.

    The prose lives in the catalogs, not in the view, so translating a page
    never means touching Python and improving the English never means editing
    fourteen files. ``code`` stays in the view because code snippets are not
    translated in any language — a trainee retypes them into Colab as-is."""
    if not st.session_state.get(SS_TEACH, True):
        return
    keys = [k for k in i18n.page_blocks(page) if k != "title"]
    body = "\n\n".join(filter(None, (i18n.tm(page, k) for k in keys)))
    with st.expander(i18n.t("learn.title", title=i18n.tm(page, "title")),
                     expanded=False):
        st.markdown(f"> {i18n.t('learn.routine')}")
        st.markdown(i18n.t("learn.understand"))
        st.markdown(body)
        st.markdown(i18n.t("learn.try_heading"))
        st.markdown(i18n.t("learn.try_body"))
        st.markdown(i18n.t("learn.discuss_heading"))
        st.markdown(i18n.t("learn.discuss_body"))
        if code:
            with st.expander(i18n.t("learn.see_code"), expanded=False):
                st.code(code, language=lang)
