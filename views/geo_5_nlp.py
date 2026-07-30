import streamlit as st

from core import data_loader as dl
from core import geo, ui, viz

ui.page_title("Geospatial", "NLP per Cluster",
              "The integration point: profile each spatial cluster with TF-IDF "
              "keywords + VADER sentiment — showing aggregates only, never raw text.")

ui.learn(
    "NLP per cluster — where text meets place (Lab 5)",
    "This is the page the whole app exists for. Everything before it ran one track or the "
    "other; here the text becomes an *attribute of place*. For each of the 29 non-noise "
    "clusters you get TF-IDF keywords, a sentiment breakdown, and a rule-based tag — a "
    "profile of what people are saying **in that specific area**.\n\n"
    "**Why this is more than either half.** The text pages found that 1,448 comments "
    "mention waiting hours; the geo pages found a cluster of 1,750 points. Neither could "
    "connect them. Grouping by `cluster_id` before running TF-IDF answers the question "
    "that matters operationally: not *what is discussed* or *where is dense*, but "
    "**which concern belongs to which place** — the difference between \"waiting times "
    "are a problem\" and \"waiting times are the problem in these four areas.\"\n\n"
    "**TF-IDF is doing something specific here.** It is not ranking each cluster's "
    "commonest words — that would return `health` and `hospital` for all 29. It weights "
    "each cluster's terms against the *other clusters*, surfacing what makes this area's "
    "comments distinctive. A term appearing everywhere scores near zero even if it "
    "appears constantly.\n\n"
    "**Read size first, always.** A cluster of 1,750 comments supports a claim; a cluster "
    "of 12 does not, yet both produce a confident-looking row of keywords and a sentiment "
    "percentage. Small clusters yield unstable terms that change completely if you nudge "
    "`eps`. Sort by `n_points` and treat the tail with suspicion. The auto-assigned `tag` "
    "is a keyword-matching convenience for navigation, not a classification — read the "
    "terms and decide yourself.\n\n"
    "**The privacy boundary is structural.** This table exports counts, aggregated "
    "percentages and term lists — never a comment, never a coordinate. That is "
    "deliberate: location-linked personal accounts of medical visits are among the most "
    "re-identifying combinations you can hold. Aggregate here is not a formatting choice; "
    "it is the control that makes the output shareable.",
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

key = dl.geo_key()
eps_m, min_samples = dl.cluster_params()
if eps_m is None:
    st.warning("Run **Geospatial → Clustering (DBSCAN)** first.", icon="⚠️")
    st.stop()

clusters, _ = geo.clusters_for(*key, eps_m, min_samples)
text_col = key[3]
if text_col not in clusters.columns:
    st.warning("The clustered layer has no text column to analyze.", icon="⚠️")
    st.stop()

summary = geo.cluster_text_for(*key, eps_m, min_samples, 8)

if summary.empty:
    st.info("No non-noise clusters to profile.")
    st.stop()

st.markdown("#### Cluster profiles")
st.dataframe(summary, width="stretch")
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
