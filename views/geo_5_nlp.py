import streamlit as st

from core import data_loader as dl
from core import geo, i18n, ui, viz

PAGE = "geo_5_nlp"

ui.page_header(PAGE, "geo")
ui.learn_page(
    PAGE,
    code=(
        "from sklearn.feature_extraction.text import TfidfVectorizer\n\n"
        "for cid, grp in gdf.groupby('cluster_id'):\n"
        "    if cid == -1:\n"
        "        continue\n"
        "    X = TfidfVectorizer(ngram_range=(1, 2)).fit_transform(clean(grp.text))\n"
        "    scores = X.mean(axis=0).A1\n"
        "    top = terms[scores.argsort()[::-1][:8]]   # aggregates only"
    ),
)

key = dl.geo_key()
eps_m, min_samples = dl.cluster_params()
if eps_m is None:
    st.warning(i18n.t("geo_5_nlp.need_clusters"), icon="⚠️")
    st.stop()

clusters, _ = geo.clusters_for(*key, eps_m, min_samples)
text_col = key[3]
if text_col not in clusters.columns:
    st.warning(i18n.t("geo_5_nlp.no_text"), icon="⚠️")
    st.stop()

summary = geo.cluster_text_for(*key, eps_m, min_samples, 8)

if summary.empty:
    st.info(i18n.t("geo_5_nlp.no_clusters"))
    st.stop()

st.markdown(i18n.t("geo_5_nlp.profiles_head"))
st.dataframe(summary, width="stretch")
st.download_button(i18n.t("geo_5_nlp.dl"), summary.to_csv(index=False),
                   "tala_cluster_summary.csv", "text/csv")

st.info(i18n.t("geo_5_nlp.privacy"), icon="🔒")

st.markdown(i18n.t("geo_5_nlp.map_head"))
centroids = geo.cluster_centroids(clusters, exclude_noise=True)
merged = centroids.merge(summary, on="cluster_id", how="left", suffixes=("", "_s"))

from streamlit_folium import st_folium  # noqa: E402

import folium  # noqa: E402

sent_color = {"positive": "#008300", "negative": "#e34948", "neutral": viz.INK_MUTED}
m = geo.base_map(merged)
vmax = int(merged["n_points"].max()) if len(merged) else 1
for _, r in merged.iterrows():
    sentiment = r.get("sentiment", "")
    shown = i18n.t(f"sent.{sentiment}") if sentiment in sent_color else sentiment
    tip = (f"<b>{i18n.t('geo_5_nlp.tip_cluster', id=int(r['cluster_id']))}</b> "
           f"({i18n.t('geo_5_nlp.tip_pts', n=int(r['n_points']))})<br>"
           f"{i18n.t('geo_5_nlp.tip_tag')}: {r.get('tag', '')}<br>"
           f"{i18n.t('geo_5_nlp.tip_sentiment')}: {shown} "
           f"(+{r.get('pos_%', 0)}% / -{r.get('neg_%', 0)}%)<br>"
           f"{i18n.t('geo_5_nlp.tip_top')}: {r.get('top_terms', '')}")
    folium.CircleMarker(
        [r.geometry.y, r.geometry.x],
        radius=6 + 18 * (r["n_points"] / vmax),
        color=sent_color.get(sentiment, viz.NU_NAVY),
        fill=True, fill_opacity=0.65, weight=1.5,
        tooltip=folium.Tooltip(tip),
    ).add_to(m)
st_folium(m, use_container_width=True, height=540, returned_objects=[])
