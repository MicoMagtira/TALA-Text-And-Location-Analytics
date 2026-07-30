"""TALA — Text And Location Analytics.

An interactive NLP + geospatial analytics explorer for data-science training,
by Mico C. Magtira (DOST-NICER). National University Manila branding.

Run:  streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="TALA — Text And Location Analytics",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded",
)

from core import ui  # noqa: E402  (after set_page_config, per Streamlit rules)

ui.inject_css()
ui.header()
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
nav.run()

ui.footer()
