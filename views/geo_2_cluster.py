import pandas as pd
import streamlit as st

from core import data_loader as dl
from core import geo, ui, viz

ui.page_title("Geospatial", "Clustering (DBSCAN)",
              "Group nearby points into density-based clusters. Use the k-distance "
              "elbow to choose a sensible neighborhood radius (eps).")

ui.learn(
    "DBSCAN & the k-distance elbow (Lab 2)",
    "The important difference from k-means: **DBSCAN is never told how many clusters to "
    "find.** You describe what \"dense\" means and it reports however many dense regions "
    "exist — possibly zero. It is also the only method here allowed to say *this point "
    "belongs to nothing*, labelling it noise (`cluster_id = -1`). For scattered real-world "
    "events that honesty is the whole appeal.\n\n"
    "**Two parameters, one definition.** `eps` is a radius in metres and `min_samples` a "
    "count. Together they define density: a point is a core point if at least "
    "`min_samples` neighbours fall within `eps`. Clusters grow by chaining core points "
    "together. Because `eps` is a real distance, this only works on the projected "
    "metre-based layer from Lab 1 — run it on raw degrees and `eps=15000` means 15,000 "
    "degrees, which is nonsense the code will happily compute.\n\n"
    "**Reading the k-distance curve above.** Each point's distance to its k-th nearest "
    "neighbour, sorted ascending. The flat stretch is points sitting in dense company; "
    "the upward sweep at the right is increasingly isolated points. The knee between them "
    "is where \"nearby\" stops meaning much — a defensible starting `eps`. On this data "
    "the 10th-neighbour distance is 7.8 km at the median but 60.1 km at the 90th "
    "percentile, and that steep tail is exactly the knee you are looking for.\n\n"
    "**How sensitive this is.** Holding `min_samples=10` and moving only `eps`:\n\n"
    "- `eps = 5 km` → **109 clusters, 7,241 noise** (fragmented; most data discarded)\n"
    "- `eps = 15 km` → **29 clusters, 2,199 noise** (the lab default)\n"
    "- `eps = 40 km` → **17 clusters, 1,290 noise** (merging distinct cities)\n\n"
    "Same data, same algorithm, three different stories. Nothing in the output says which "
    "is right — that judgement is yours, and it is what you must defend.\n\n"
    "**What a cluster is not.** It is a region that met *your* density threshold. It is "
    "not a community, a catchment, or an outbreak. And noise is not error: an isolated "
    "point may be the most important case in the dataset.",
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
    st.warning("Run **Geospatial → Ingest & CRS Validation** first to build points.",
               icon="⚠️")
    st.stop()

key = dl.geo_key()
gdf, _ = geo.points_for(*key)
gm = geo.to_metric(gdf)

with st.expander("📈 k-distance plot (find the elbow for eps)", expanded=True):
    k = st.slider("k (neighbor rank)", 3, 20, 10)
    kd = geo.k_distance(gm, k)
    fig, ax = viz.figure(figsize=(8, 3.2))
    ax.plot(kd / 1000, color=viz.NU_NAVY, lw=1.6)
    ax.set_xlabel("points (sorted)")
    ax.set_ylabel(f"distance to {k}-th neighbor (km)")
    ax.set_title("Look for the 'knee' — that distance is a good eps")
    st.pyplot(fig, width="stretch")

st.markdown("#### DBSCAN parameters")
c1, c2, c3 = st.columns([2, 2, 1])
eps_km = c1.slider("eps (km)", 1.0, 100.0, 15.0, 1.0)
min_samples = c2.slider("min_samples", 2, 50, 10)
if c3.button("↺ Lab defaults"):
    eps_km, min_samples = 15.0, 10

result, info = geo.clusters_for(*key, eps_km * 1000, min_samples)
# Only the parameters are per-session; trainees who pick the same eps and
# min_samples share one clustered layer.
st.session_state[dl.SS_CLUSTER_PARAMS] = (eps_km * 1000, min_samples)

m1, m2, m3 = st.columns(3)
m1.metric("Clusters found", info["n_clusters"])
m2.metric("Noise points", f"{info['n_noise']:,}")
m3.metric("Clustered points", f"{len(result) - info['n_noise']:,}")

st.markdown("#### Cluster map")
palette = viz.categorical(ui.palette(), max(1, info["n_clusters"]))
from streamlit_folium import st_folium  # noqa: E402

m = geo.cluster_marker_map(result, palette)
st_folium(m, use_container_width=True, height=520, returned_objects=[])

st.markdown("#### Cluster sizes")
sizes = (result[result["cluster_id"] != -1]["cluster_id"]
         .value_counts().sort_index())
if len(sizes):
    st.bar_chart(pd.DataFrame({"points": sizes.values},
                              index=[f"C{c}" for c in sizes.index]))
else:
    st.info("No clusters at this setting — lower min_samples or raise eps.")

st.success("Clusters ready. Continue to **Generalization**, **NLP per Cluster**, "
           "or **Map & Exports**.", icon="➡️")
