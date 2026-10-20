"""NLP primitives still shared by TALA's place-first pipeline.

The older word-cloud / NRC / LDA / RAKE / POS / readability helpers were dropped
with the place-first redesign. What remains: the VADER threshold and analyzer
(used by ``core/compare.py`` and ``core/salita.py``) and the TF-IDF K-Means
themes (``compare.theme_labels`` reuses it, so theme fits stay cached once).

Heavy dependencies (sklearn, vaderSentiment) import lazily inside the functions
that use them. Cached functions never take the UI language as a parameter, so a
whole cohort shares one copy (see ``tests/test_i18n.py``).
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from . import i18n

VADER_THRESHOLD = 0.05


@st.cache_resource(show_spinner=False)
def _vader():
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    return SentimentIntensityAnalyzer()


# ---------------------------------------------------------------------------
# TF-IDF K-Means themes
# ---------------------------------------------------------------------------
@i18n.localized_spinner("spin.kmeans")
@st.cache_data(show_spinner=False)
def tfidf_kmeans(corpus: tuple[str, ...], k: int = 4, seed: int = 42,
                 top_terms: int = 10):
    from sklearn.cluster import KMeans
    from sklearn.decomposition import TruncatedSVD
    from sklearn.feature_extraction.text import TfidfVectorizer

    docs = [d for d in corpus if d.strip()]
    if len(docs) < k:
        return None
    vec = TfidfVectorizer(ngram_range=(1, 2), max_df=0.9, min_df=3, max_features=1200)
    X = vec.fit_transform(docs)
    km = KMeans(n_clusters=k, n_init=10, random_state=seed)
    labels = km.fit_predict(X)
    terms = vec.get_feature_names_out()
    order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    top = {c: [terms[i] for i in order_centroids[c, :top_terms]] for c in range(k)}
    # TruncatedSVD, not PCA: it consumes the sparse TF-IDF matrix directly.
    # PCA required X.toarray(), which densified 12k x 1200 float64 into a ~115 MB
    # allocation — the single largest transient in the app, on a 1 GB box.
    coords = TruncatedSVD(n_components=2, random_state=seed).fit_transform(X)
    sizes = pd.Series(labels).value_counts().sort_index()
    return {"labels": labels, "top_terms": top, "coords": coords,
            "sizes": sizes, "docs": docs}
