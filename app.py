"""TALA — Text And Location Analytics.

An interactive NLP + geospatial analytics explorer for data-science training,
by Mico C. Magtira (DOST-NICER). National University Manila branding.

Run:  streamlit run app.py

Boot order matters here. The app targets Streamlit Community Cloud (~1 GB RAM,
shared CPU), so the module graph is kept deliberately shallow: only streamlit and
pandas load before the first page renders. sklearn, matplotlib, geopandas, folium
and NLTK are imported inside the functions that use them, which means a visitor
who only opens the Home page never pays for the geospatial or modelling stacks.

The session also starts behind a language gate (English, Filipino, Cebuano,
Ilocano, Hiligaynon). It runs before the boot splash on purpose: the splash is
then already localized, and a trainee never watches the interface change
language underneath them mid-load. See core/i18n.py for the translation model.
"""
from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="TALA — Text And Location Analytics",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)

from core import i18n  # noqa: E402  (after set_page_config, per Streamlit rules)

# Nothing else renders until a language is chosen. language_gate() never
# returns — it calls st.stop(), and the run that follows START finds is_set().
if not i18n.is_set():
    from core import gate  # noqa: E402

    gate.language_gate()

# The splash goes up before anything heavy so the browser has something to paint
# while the rest of this module and the first dataset read complete.
from core import splash  # noqa: E402

boot = splash.boot()
if boot:
    boot.update(6, i18n.t("boot.core"))

from core import data_loader as dl  # noqa: E402
from core import ui  # noqa: E402

if boot:
    boot.update(18, i18n.t("boot.theme"))

ui.inject_css()
ui.header()

# Pull the dataset in explicitly rather than letting the first page trigger it,
# so the read happens while the splash is still up and reports honest progress.
if boot:
    boot.update(32, i18n.t("boot.dataset"))
dl.ensure_loaded()

if boot:
    boot.update(44, i18n.t("boot.indexing"))
ui.sidebar_controls()

# --- Navigation ---------------------------------------------------------------
# Titles come from the catalog; the ones that should stay English (Topic
# Modeling, Clustering (DBSCAN), Generalization) simply have no translation and
# fall through to the English source. See core/i18n.py.
home = st.Page("views/home.py", title=i18n.t("home.nav"), icon="🏠", default=True)

text_pages = [
    st.Page("views/text_1_data.py", title=i18n.t("text_1_data.nav"), icon="🧹"),
    st.Page("views/text_2_wordcloud.py", title=i18n.t("text_2_wordcloud.nav"), icon="☁️"),
    st.Page("views/text_3_sentiment.py", title=i18n.t("text_3_sentiment.nav"), icon="😊"),
    st.Page("views/text_4_ngrams.py", title=i18n.t("text_4_ngrams.nav"), icon="🔗"),
    st.Page("views/text_5_topics.py", title=i18n.t("text_5_topics.nav"), icon="🧩"),
    st.Page("views/text_6_keywords.py", title=i18n.t("text_6_keywords.nav"), icon="🔑"),
    st.Page("views/text_7_metrics.py", title=i18n.t("text_7_metrics.nav"), icon="📐"),
    st.Page("views/text_8_themes.py", title=i18n.t("text_8_themes.nav"), icon="🎯"),
]

geo_pages = [
    st.Page("views/geo_1_ingest.py", title=i18n.t("geo_1_ingest.nav"), icon="🛰️"),
    st.Page("views/geo_2_cluster.py", title=i18n.t("geo_2_cluster.nav"), icon="🧭"),
    st.Page("views/geo_3_generalize.py", title=i18n.t("geo_3_generalize.nav"), icon="🔲"),
    st.Page("views/geo_4_map.py", title=i18n.t("geo_4_map.nav"), icon="🗺️"),
    st.Page("views/geo_5_nlp.py", title=i18n.t("geo_5_nlp.nav"), icon="📍"),
]

nav = st.navigation({
    i18n.t("nav.overview"): [home],
    i18n.t("nav.text"): text_pages,
    i18n.t("nav.geo"): geo_pages,
})

if boot:
    boot.update(55, i18n.t("boot.render"))

# The splash must come down even if a page raises, otherwise the overlay would
# sit on top of the traceback.
try:
    nav.run()
finally:
    if boot:
        boot.finish(i18n.t("boot.ready"))

ui.footer()
