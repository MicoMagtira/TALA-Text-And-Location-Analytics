"""About the project: AIKasalig, the DOST-NICER program, and where TALA fits.

An evaluator read TALA as a personal project; it is a learning module of
AIKasalig. This page names the project, its program and partners, shows their
logos on a white card (several marks are navy ink that vanishes on the night
theme) and credits the people behind it.

The prose lives in ``locales/pages/<lang>/about.md`` (block keys in English
source order), so translating never means touching this file. Blocks a language
has not translated yet fall back to English one by one (``i18n.tm``). The ``lg``
logos render here and on the splash only: both draw once, not on every rerun.
"""
import streamlit as st

from core import brand, i18n, tracks, ui

PAGE = "about"

# Story on the left (every other block, in source order), facts on the right as
# small cards. The columns stack on phones.
_FACTS = ("glance", "sisters", "credits")

ui.page_header(PAGE, "about")

with st.container(key="tala-logowall"):
    st.markdown(brand.strip_html("lg", "tala-logos tala-logos-wall"), unsafe_allow_html=True)

blocks = [k for k in i18n.page_blocks(PAGE) if k != "title"]
left, right = st.columns([3, 2], gap="large")
with left:
    # Any block not placed on the right reads as part of the story.
    for key in (k for k in blocks if k not in _FACTS):
        st.markdown(i18n.tm(PAGE, key))
with right:
    for key in (k for k in _FACTS if k in blocks):
        with st.container(border=True, key=f"tala-about-{key}"):
            st.markdown(i18n.tm(PAGE, key))

st.page_link(tracks.path_of("learn"),
             label=ui._t("nav.learn", "How TALA works"),
             icon=":material/arrow_forward:", icon_position="right")
