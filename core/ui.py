"""Shared UI helpers: header, footer, sidebar controls, and 'Learn' panels.

The 'Learn' expanders turn each page into live teaching material by pairing the
concept with the equivalent code from the source notebook / lab.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from . import data_loader as dl
from .viz import categorical_names, sequential_names, load_css

ASSETS = Path(__file__).resolve().parent.parent / "assets"

APP_TITLE = "TALA — Text And Location Analytics"
APP_SUB = "NLP + Geospatial Analytics Explorer"
DEVELOPER = "Mico C. Magtira — Senior Data and NLP-Geospatial Scientist, DOST-NICER"

SS_PALETTE = "cat_palette"
SS_SEQ = "seq_palette"
SS_TEACH = "teach_mode"
SS_CUSTOM_SW = "custom_stopwords"
SS_USE_TL = "use_tagalog"


def inject_css() -> None:
    css_path = ASSETS / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{load_css(str(css_path))}</style>", unsafe_allow_html=True)


def header() -> None:
    st.markdown(
        f"""
        <div class="tala-header">
          <h1>🌟 {APP_TITLE}</h1>
          <div class="tala-sub">{APP_SUB}</div>
          <div class="tala-dev">Developed by {DEVELOPER}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def footer() -> None:
    st.markdown(
        f"""
        <div class="tala-footer">
          <strong>{APP_TITLE}</strong> · {DEVELOPER}<br>
          National University Manila · For data science / NLP / geospatial training use.
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_controls() -> None:
    """Global controls rendered on every page (palette, language, teach mode)."""
    dl.ensure_loaded()
    st.sidebar.markdown("### 🎨 Appearance")
    st.session_state.setdefault(SS_PALETTE, categorical_names()[0])
    st.session_state.setdefault(SS_SEQ, sequential_names()[0])
    st.sidebar.selectbox("Categorical palette (series)", categorical_names(), key=SS_PALETTE)
    st.sidebar.selectbox("Sequential palette (maps/heatmaps)", sequential_names(), key=SS_SEQ)

    st.sidebar.markdown("### 🈳 Language / stopwords")
    st.session_state.setdefault(SS_USE_TL, True)
    st.sidebar.checkbox("Include Filipino/Tagalog stopwords", key=SS_USE_TL)
    st.session_state.setdefault(SS_CUSTOM_SW, "")
    st.sidebar.text_area(
        "Custom stopwords (comma or newline separated)", key=SS_CUSTOM_SW, height=90,
        placeholder="e.g. clinic, hospital, ospital",
    )

    st.sidebar.markdown("### 🎓 Training")
    st.session_state.setdefault(SS_TEACH, True)
    st.sidebar.toggle("Show 'Learn' explanations", key=SS_TEACH)

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Data: {st.session_state.get(dl.SS_SOURCE, 'n/a')}")
    st.sidebar.caption(f"{len(dl.active_df()):,} rows · text column: "
                       f"`{st.session_state.get(dl.SS_TEXT_COL)}`")


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


def learn(title: str, body_md: str, code: str | None = None,
          lang: str = "python") -> None:
    """Render a collapsible teaching panel (only when teach mode is on)."""
    if not st.session_state.get(SS_TEACH, True):
        return
    with st.expander(f"📘 Learn — {title}"):
        st.markdown(body_md)
        if code:
            st.code(code, language=lang)


def page_title(pill: str, title: str, blurb: str | None = None) -> None:
    st.markdown(f'<span class="tala-pill">{pill}</span>', unsafe_allow_html=True)
    st.markdown(f"## {title}")
    if blurb:
        st.markdown(blurb)
