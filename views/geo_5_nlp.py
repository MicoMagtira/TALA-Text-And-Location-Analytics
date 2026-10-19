import streamlit as st

from core import data_loader as dl
from core import audio, geo, i18n, tracks, ui, viz

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
if dl.cluster_params_are_default():
    st.caption(i18n.t("geo_2_cluster.using_defaults",
                      eps=int(eps_m / 1000), n=min_samples))
    st.page_link("views/geo_2_cluster.py", label=i18n.t("geo_2_cluster.nav"), icon="🎚️")

clusters, _ = geo.clusters_for(*key, eps_m, min_samples)
text_col = key[3]
if text_col not in clusters.columns:
    ui.locked(i18n.t("geo_5_nlp.no_text"), "text_1_data",
              i18n.t("geo_5_nlp.pick_text"))

with audio.result(tracks.SIGNATURE[PAGE], key + (eps_m, min_samples)):
    summary = geo.cluster_text_for(*key, eps_m, min_samples, 8)

if summary.empty:
    ui.info(i18n.t("geo_5_nlp.no_clusters"))
    ui.track_footer(PAGE)
    st.stop()

st.markdown(i18n.t("geo_5_nlp.profiles_head"))
st.dataframe(summary, width="stretch")
st.download_button(i18n.t("geo_5_nlp.dl"), summary.to_csv(index=False),
                   "tala_cluster_summary.csv", "text/csv")

st.info(i18n.t("geo_5_nlp.privacy"), icon="🔒")

st.markdown(i18n.t("geo_5_nlp.map_head"))
centroids = geo.cluster_centroids(clusters, exclude_noise=True)
merged = centroids.merge(summary, on="cluster_id", how="left", suffixes=("", "_s"))

import html as _html  # noqa: E402

from core import maps  # noqa: E402

sent_color = {"positive": "#008300", "negative": "#e34948", "neutral": viz.INK_MUTED}


def _tip(r) -> str:
    sentiment = r.get("sentiment", "")
    shown = i18n.t(f"sent.{sentiment}") if sentiment in sent_color else sentiment
    # Tag and terms derive from user text, so escape them before they reach the
    # tooltip's HTML.
    return (f"<b>{i18n.t('geo_5_nlp.tip_cluster', id=int(r['cluster_id']))}</b> "
            f"({i18n.t('geo_5_nlp.tip_pts', n=int(r['n_points']))})<br>"
            f"{i18n.t('geo_5_nlp.tip_tag')}: {_html.escape(str(r.get('tag', '')))}<br>"
            f"{i18n.t('geo_5_nlp.tip_sentiment')}: {_html.escape(str(shown))} "
            f"(+{r.get('pos_%', 0)}% / -{r.get('neg_%', 0)}%)<br>"
            f"{i18n.t('geo_5_nlp.tip_top')}: {_html.escape(str(r.get('top_terms', '')))}")


# One row per cluster (a handful), so no sampling; row order matches ``merged``.
# The tip is HTML, so it is attached here rather than through to_frame's
# 90-character plain-text ``tip``.
frame = maps.to_frame(merged, extra_cols=[c for c in ("cluster_id", "n_points", "sentiment")
                                          if c in merged.columns])
frame["tip"] = [_tip(r) for _, r in merged.iterrows()]
st.pydeck_chart(
    maps.deck([maps.centroid_layer(frame, color_by=sent_color)],
              maps.view_for(frame), "{tip}"),
    height=540, width="stretch")

ui.page_done(PAGE)
ui.track_footer(PAGE)
