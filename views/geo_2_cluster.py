import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from core import data_loader as dl
from core import geo, ui, viz

ui.page_title("Geospatial", "Clustering (DBSCAN)",
              "Group nearby points into density-based clusters. Use the k-distance "
              "elbow to choose a sensible neighborhood radius (eps).")
viz.apply_matplotlib_theme()

ui.learn(
    "DBSCAN & the k-distance elbow (Lab 2)",
    "**DBSCAN** finds areas where points are densely packed and labels points outside "
    "those areas as **noise** (`cluster_id = -1`). It needs `eps`, the neighborhood "
    "radius in meters, and `min_samples`, the number of nearby points needed to count as "
    "a dense area. This is why Lab 1's metric CRS is essential.\n\n"
    "Start by setting the k-distance neighbor rank close to `min_samples`, then look for "
    "the bend where distances begin rising quickly; that is a defensible starting `eps`, "
    "not a universal answer. Compare cluster count, noise count, and cluster sizes after "
    "changing one parameter. A cluster indicates local density under your settings—it does "
    "not by itself identify a community, cause, or service catchment.",
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

if dl.SS_POINTS not in st.session_state:
    st.warning("Run **Geospatial → Ingest & CRS Validation** first to build points.",
               icon="⚠️")
    st.stop()

gdf = st.session_state[dl.SS_POINTS]
gm = geo.to_metric(gdf)

with st.expander("📈 k-distance plot (find the elbow for eps)", expanded=True):
    k = st.slider("k (neighbor rank)", 3, 20, 10)
    kd = geo.k_distance(gm, k)
    fig, ax = plt.subplots(figsize=(8, 3.2))
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

result, info = geo.run_dbscan(gdf, eps_m=eps_km * 1000, min_samples=min_samples)
st.session_state[dl.SS_CLUSTERS] = result

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
