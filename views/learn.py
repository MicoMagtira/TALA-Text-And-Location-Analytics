"""How TALA works: the essay, About and attributions.

The prose lives in ``locales/pages/<lang>/learn.md`` (block keys in English
source order), so translating never means touching this file. Blocks a language
has not translated yet fall back to English one by one (``i18n.tm``).
"""
import streamlit as st

from core import i18n, ui

PAGE = "learn"

ui.page_header(PAGE, "learn")

for key in i18n.page_blocks(PAGE):
    if key != "title":
        st.markdown(i18n.tm(PAGE, key))

st.divider()
st.markdown(f"### {i18n.t('home.about')}")
st.markdown(i18n.t("home.intro"))
# The project, its partners and the credits live on their own page.
st.page_link("views/about.py",
             label=ui._t("learn.about_link", "About the project: AIKasalig, its partners and credits"),
             icon=":material/arrow_forward:", icon_position="right")
st.caption(ui._t("learn.attribution",
                 "Place names and coordinates: GeoNames (geonames.org), CC BY 4.0."))
