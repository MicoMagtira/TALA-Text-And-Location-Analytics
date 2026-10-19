import pandas as pd
import streamlit as st

from core import data_loader as dl
from core import audio, geo, i18n, tracks, ui, viz

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

key = dl.geo_key()
gdf, _ = geo.points_for(*key)
gm = geo.to_metric(gdf)



@st.fragment
def _kdistance():
    """The k slider only redraws this plot, so it must not rerun the clustering."""
    with st.expander(i18n.t("geo_2_cluster.kdist_head"), expanded=True):
        k = st.slider(i18n.t("geo_2_cluster.k"), 3, 20, 10)
        kd = geo.k_distance(gm, k)
        fig, ax = viz.figure(figsize=(8, 3.2))
        ax.plot(kd / 1000, color=viz.NU_NAVY, lw=1.6)
        ax.set_xlabel(i18n.t("geo_2_cluster.kd_x"))
        ax.set_ylabel(i18n.t("geo_2_cluster.kd_y", k=k))
        ax.set_title(i18n.t("geo_2_cluster.kd_title"))
        st.pyplot(fig, width="stretch")


_kdistance()

st.markdown(i18n.t("geo_2_cluster.params_head"))


def _reset_defaults() -> None:
    st.session_state["geo2_eps"] = dl.DEFAULT_EPS_M / 1000
    st.session_state["geo2_min"] = dl.DEFAULT_MIN_SAMPLES


# Sliders start from the session's current params (the defaults on first visit),
# so coming back to this page shows what the later pages are using.
cur_eps, cur_min = dl.cluster_params()
c1, c2, c3 = st.columns([2, 2, 1])
eps_km = c1.slider(i18n.t("geo_2_cluster.eps"), 1.0, 100.0,
                   float(min(100.0, max(1.0, cur_eps / 1000))), 1.0, key="geo2_eps")
min_samples = c2.slider(i18n.t("geo_2_cluster.min_samples"), 2, 50,
                        int(min(50, max(2, cur_min))), key="geo2_min")
c3.button(i18n.t("geo_2_cluster.defaults"), on_click=_reset_defaults)

with audio.result(tracks.SIGNATURE[PAGE], key + (eps_km * 1000, min_samples)):
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


@st.fragment
def _cluster_map(result, palette):
    """Map + selection readout. A click reruns only this block, not the page."""
    from core import maps

    frame = maps.cluster_frame(result, palette)
    layer = maps.cluster_layer(result, palette, frame=frame)
    event = st.pydeck_chart(
        maps.deck([layer], maps.view_for(frame), "{tip}"),
        height=520, width="stretch", on_select="rerun",
        selection_mode="single-object", key="geo2_map")
    if frame.attrs.get("sampled"):
        st.caption(i18n.t("maps.sampled", shown=len(frame),
                          total=frame.attrs["total"]))
    picked = (event.selection.objects.get(maps.CLUSTER_LAYER_ID) or [None])[0]
    if picked is None:
        st.caption(i18n.t("geo_2_cluster.pick_hint"))
        return
    cid = int(picked["cluster_id"])
    if cid == -1:
        ui.info(i18n.t("geo_2_cluster.picked_noise"))
        return
    n = int((result["cluster_id"] == cid).sum())
    st.info(i18n.t("geo_2_cluster.picked", id=cid, n=n))
    st.page_link("views/geo_5_nlp.py", label=i18n.t("geo_5_nlp.nav"), icon="➡️")


_cluster_map(result, palette)

st.markdown(i18n.t("geo_2_cluster.sizes_head"))
sizes = (result[result["cluster_id"] != -1]["cluster_id"]
         .value_counts().sort_index())
if len(sizes):
    st.bar_chart(pd.DataFrame({i18n.t("geo_2_cluster.points"): sizes.values},
                              index=[f"C{c}" for c in sizes.index]))
else:
    ui.info(i18n.t("geo_2_cluster.no_clusters"))

ui.page_done(PAGE)
ui.track_footer(PAGE)
