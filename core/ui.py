"""Shared UI helpers: header, footer, sidebar controls, and 'Learn' panels.

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

from . import data_loader as dl
from . import i18n
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
    """Global controls rendered on every page (language, palette, teach mode)."""
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

    st.sidebar.markdown(f"### {i18n.t('side.appearance')}")
    st.session_state.setdefault(SS_PALETTE, categorical_names()[0])
    st.session_state.setdefault(SS_SEQ, sequential_names()[0])
    st.sidebar.selectbox(i18n.t("side.palette_cat"), categorical_names(), key=SS_PALETTE)
    st.sidebar.selectbox(i18n.t("side.palette_seq"), sequential_names(), key=SS_SEQ)

    st.sidebar.markdown(f"### {i18n.t('side.stopwords')}")
    st.session_state.setdefault(SS_USE_TL, True)
    st.sidebar.checkbox(i18n.t("side.use_tagalog"), key=SS_USE_TL)
    st.session_state.setdefault(SS_CUSTOM_SW, "")
    st.sidebar.text_area(
        i18n.t("side.custom_stopwords"), key=SS_CUSTOM_SW, height=90,
        placeholder=i18n.t("side.custom_placeholder"),
    )

    st.sidebar.markdown(f"### {i18n.t('side.training')}")
    st.session_state.setdefault(SS_TEACH, True)
    st.sidebar.toggle(i18n.t("side.show_learn"), key=SS_TEACH)

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
    """Pill + title + blurb, all resolved from the catalog by page name.

    ``page`` is the view's module stem (``text_3_sentiment``), which is also the
    key prefix and the name of its Learn essay file. One identifier, so a page
    cannot drift out of sync with its own translations."""
    st.markdown(f'<span class="tala-pill">{i18n.t(_PILL[section])}</span>',
                unsafe_allow_html=True)
    st.markdown(f"## {i18n.t(f'{page}.title')}")
    blurb = i18n.t(f"{page}.blurb")
    if blurb and blurb != f"{page}.blurb":
        st.markdown(blurb)


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
    with st.expander(i18n.t("learn.header", title=i18n.tm(page, "title")),
                     expanded=True):
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
