import streamlit as st

from core import data_loader as dl
from core import geo, ui, viz

ui.page_title("Geospatial", "NLP per Cluster",
              "The integration point: profile each spatial cluster with TF-IDF "
              "keywords + VADER sentiment — showing aggregates only, never raw text.")

if dl.SS_CLUSTERS not in st.session_state:
    st.warning("Run **Geospatial → Clustering (DBSCAN)** first.", icon="⚠️")
    st.stop()

clusters = st.session_state[dl.SS_CLUSTERS]
text_col = st.session_state[dl.SS_TEXT_COL]
if text_col not in clusters.columns:
    st.warning("The clustered layer has no text column to analyze.", icon="⚠️")
    st.stop()

with st.spinner("Profiling clusters (keywords + sentiment)…"):
    summary = geo.per_cluster_nlp(clusters, text_col)
st.session_state[dl.SS_CLUSTER_TEXT] = summary

if summary.empty:
    st.info("No non-noise clusters to profile.")
    st.stop()

st.markdown("#### Cluster profiles")
st.dataframe(summary, use_container_width=True)
st.download_button("⬇️ Download cluster summary (CSV)", summary.to_csv(index=False),
                   "tala_cluster_summary.csv", "text/csv")

st.info("🔒 **Privacy-safe by design:** the table and map expose only cluster-level "
        "keywords and sentiment percentages — never individual comments.", icon="🔒")

st.markdown("#### Map — cluster centroids with topics & sentiment")
centroids = geo.cluster_centroids(clusters, exclude_noise=True)
merged = centroids.merge(summary, on="cluster_id", how="left", suffixes=("", "_s"))

from streamlit_folium import st_folium  # noqa: E402

import folium  # noqa: E402

sent_color = {"positive": "#008300", "negative": "#e34948", "neutral": viz.INK_MUTED}
m = geo.base_map(merged)
vmax = int(merged["n_points"].max()) if len(merged) else 1
for _, r in merged.iterrows():
    tip = (f"<b>Cluster {int(r['cluster_id'])}</b> ({int(r['n_points'])} pts)<br>"
           f"Tag: {r.get('tag', '')}<br>"
           f"Sentiment: {r.get('sentiment', '')} "
           f"(+{r.get('pos_%', 0)}% / -{r.get('neg_%', 0)}%)<br>"
           f"Top: {r.get('top_terms', '')}")
    folium.CircleMarker(
        [r.geometry.y, r.geometry.x],
        radius=6 + 18 * (r["n_points"] / vmax),
        color=sent_color.get(r.get("sentiment"), viz.NU_NAVY),
        fill=True, fill_opacity=0.65, weight=1.5,
        tooltip=folium.Tooltip(tip),
    ).add_to(m)
st_folium(m, use_container_width=True, height=540, returned_objects=[])

ui.learn(
    "NLP per cluster — where text meets place (Lab 5)",
    "For each DBSCAN cluster we join its comments into one document, extract the top "
    "**TF-IDF** terms (what that place talks about), and take the **majority VADER "
    "sentiment**. An auto-tag maps keywords to a human label (e.g. *Staff "
    "Experience*). Crucially, maps and tooltips carry only these **aggregates** — the "
    "raw comments never leave the table — which keeps location-linked text private.",
    code=(
        "from sklearn.feature_extraction.text import TfidfVectorizer\n"
        "for cid, grp in gdf.groupby('cluster_id'):\n"
        "    docs = clean(grp[text_col])\n"
        "    X = TfidfVectorizer(ngram_range=(1,2)).fit_transform([' '.join(docs)])\n"
        "    top_terms = ...            # highest TF-IDF terms for the cluster\n"
        "    sentiment = majority(vader(t) for t in grp[text_col])\n"
        "    # export ONLY: cluster_id, n_points, top_terms, sentiment %"
    ),
)
