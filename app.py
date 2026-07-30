"""TALA — Text And Location Analytics.

An interactive NLP + geospatial analytics explorer for data-science training,
by Mico C. Magtira (DOST-NICER). National University Manila branding.

Run:  streamlit run app.py

Boot order matters here. The app targets Streamlit Community Cloud (~1 GB RAM,
shared CPU), so the module graph is kept deliberately shallow: only streamlit and
pandas load before the first page renders. sklearn, matplotlib, geopandas, folium
and NLTK are imported inside the functions that use them, which means a visitor
who only opens the Home page never pays for the geospatial or modelling stacks.
"""
from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="TALA — Text And Location Analytics",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)

# The splash goes up before anything heavy so the browser has something to paint
# while the rest of this module and the first dataset read complete.
from core import splash  # noqa: E402  (after set_page_config, per Streamlit rules)

boot = splash.boot()
if boot:
    boot.update(6, "Booting TALA core")

from core import data_loader as dl  # noqa: E402
from core import ui  # noqa: E402

if boot:
    boot.update(18, "Loading theme and palettes")

ui.inject_css()
ui.header()

# Pull the dataset in explicitly rather than letting the first page trigger it,
# so the read happens while the splash is still up and reports honest progress.
if boot:
    boot.update(32, "Reading dataset (Parquet)")
dl.ensure_loaded()

if boot:
    boot.update(44, "Indexing text and coordinates")
ui.sidebar_controls()

# --- Navigation ---------------------------------------------------------------
home = st.Page("views/home.py", title="Home & About", icon="🏠", default=True)

text_pages = [
    st.Page("views/text_1_data.py", title="Data & Preprocessing", icon="🧹"),
    st.Page("views/text_2_wordcloud.py", title="Word Frequency & Clouds", icon="☁️"),
    st.Page("views/text_3_sentiment.py", title="Sentiment & Emotion", icon="😊"),
    st.Page("views/text_4_ngrams.py", title="N-grams & Networks", icon="🔗"),
    st.Page("views/text_5_topics.py", title="Topic Modeling", icon="🧩"),
    st.Page("views/text_6_keywords.py", title="Keywords & Nouns", icon="🔑"),
    st.Page("views/text_7_metrics.py", title="Linguistic Metrics", icon="📐"),
    st.Page("views/text_8_themes.py", title="Themes (TF-IDF K-Means)", icon="🎯"),
]

geo_pages = [
    st.Page("views/geo_1_ingest.py", title="Ingest & CRS Validation", icon="🛰️"),
    st.Page("views/geo_2_cluster.py", title="Clustering (DBSCAN)", icon="🧭"),
    st.Page("views/geo_3_generalize.py", title="Generalization", icon="🔲"),
    st.Page("views/geo_4_map.py", title="Map & Exports", icon="🗺️"),
    st.Page("views/geo_5_nlp.py", title="NLP per Cluster", icon="📍"),
]

nav = st.navigation({
    "Overview": [home],
    "Text Analytics": text_pages,
    "Geospatial Analytics": geo_pages,
})

if boot:
    boot.update(55, "Rendering view")

# The splash must come down even if a page raises, otherwise the overlay would
# sit on top of the traceback.
try:
    nav.run()
finally:
    if boot:
        boot.finish("Ready")

ui.footer()
