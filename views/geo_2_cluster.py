import pandas as pd
import streamlit as st

from core import data_loader as dl
from core import geo, i18n, ui, viz

PAGE = "geo_2_cluster"

ui.page_header(PAGE, "geo")
ui.learn_page(
    PAGE,
    code=(
        "from sklearn.cluster import DBSCAN\n"
        "from sklearn.neighbors import NearestNeighbors\n\n"
        "xy = list(zip(gdf_m.geometry.x, gdf_m.geometry.y))\n"
        "# k-distance for the elbow\n"
        "d, _ = NearestNeighbors(n_neighbors=11).fit(xy).kneighbors(xy)\n"
        "kdist = sorted(d[:, 10])\n\n"
        "labels = DBSCAN(eps=15000, min_samples=10).fit_predict(xy)  # metres"
    ),
)

if not st.session_state.get(dl.SS_POINTS_READY):
    st.warning(i18n.t("geo_2_cluster.need_points"), icon="⚠️")
    st.stop()

key = dl.geo_key()
gdf, _ = geo.points_for(*key)
gm = geo.to_metric(gdf)

with st.expander(i18n.t("geo_2_cluster.kdist_head"), expanded=True):
    k = st.slider(i18n.t("geo_2_cluster.k"), 3, 20, 10)
    kd = geo.k_distance(gm, k)
    fig, ax = viz.figure(figsize=(8, 3.2))
    ax.plot(kd / 1000, color=viz.NU_NAVY, lw=1.6)
    ax.set_xlabel(i18n.t("geo_2_cluster.kd_x"))
    ax.set_ylabel(i18n.t("geo_2_cluster.kd_y", k=k))
    ax.set_title(i18n.t("geo_2_cluster.kd_title"))
    st.pyplot(fig, width="stretch")

st.markdown(i18n.t("geo_2_cluster.params_head"))
c1, c2, c3 = st.columns([2, 2, 1])
eps_km = c1.slider(i18n.t("geo_2_cluster.eps"), 1.0, 100.0, 15.0, 1.0)
min_samples = c2.slider(i18n.t("geo_2_cluster.min_samples"), 2, 50, 10)
if c3.button(i18n.t("geo_2_cluster.defaults")):
    eps_km, min_samples = 15.0, 10

result, info = geo.clusters_for(*key, eps_km * 1000, min_samples)
# Only the parameters are per-session; trainees who pick the same eps and
# min_samples share one clustered layer.
st.session_state[dl.SS_CLUSTER_PARAMS] = (eps_km * 1000, min_samples)

m1, m2, m3 = st.columns(3)
m1.metric(i18n.t("geo_2_cluster.m_clusters"), info["n_clusters"])
m2.metric(i18n.t("geo_2_cluster.m_noise"), f"{info['n_noise']:,}")
m3.metric(i18n.t("geo_2_cluster.m_clustered"),
          f"{len(result) - info['n_noise']:,}")

st.markdown(i18n.t("geo_2_cluster.map_head"))
palette = viz.categorical(ui.palette(), max(1, info["n_clusters"]))
from streamlit_folium import st_folium  # noqa: E402

m = geo.cluster_marker_map(result, palette)
st_folium(m, use_container_width=True, height=520, returned_objects=[])

st.markdown(i18n.t("geo_2_cluster.sizes_head"))
sizes = (result[result["cluster_id"] != -1]["cluster_id"]
         .value_counts().sort_index())
if len(sizes):
    st.bar_chart(pd.DataFrame({i18n.t("geo_2_cluster.points"): sizes.values},
                              index=[f"C{c}" for c in sizes.index]))
else:
    st.info(i18n.t("geo_2_cluster.no_clusters"))

st.success(i18n.t("geo_2_cluster.success"), icon="➡️")
