import streamlit as st

from core import data_loader as dl
from core import geo, ui, viz

ui.page_title("Geospatial", "Generalization",
              "Summarize points into coarser features so patterns read at a glance "
              "and individual locations are not exposed.")

ui.learn(
    "Generalization: grid vs centroids (Lab 3)",
    "Generalization deliberately trades exact location for a safer, more readable view. "
    "**Grid aggregation** counts points in equal-sized meter-based cells, making density "
    "patterns easier to compare. **Cluster centroids** replace each DBSCAN cluster with a "
    "single representative point and its count. Both outputs are returned to WGS84 for "
    "web mapping.\n\n"
    "Choose the method based on the decision you need to support: grids preserve broad "
    "density while centroids summarize known clusters. Try several grid sizes; smaller "
    "cells can reveal detail but may expose people or create unstable-looking patterns. "
    "Ask what the method hides, whether noise should be included, and whether the final "
    "representation is safe enough for your audience.",
    code=(
        "from shapely.geometry import box, Point\n"
        "# grid: count points inside each cell\n"
        "cell = box(x0, y0, x0 + size, y0 + size)\n\n"
        "# centroid: one point per cluster\n"
        "Point(grp.geometry.x.mean(), grp.geometry.y.mean())"
    ),
)

if dl.SS_CLUSTERS not in st.session_state and dl.SS_POINTS not in st.session_state:
    st.warning("Build points (Ingest) — and ideally clusters (DBSCAN) — first.",
               icon="⚠️")
    st.stop()

method = st.radio("Method", ["Grid aggregation", "Cluster centroids"], horizontal=True)
source = st.session_state.get(dl.SS_CLUSTERS, st.session_state.get(dl.SS_POINTS))

from streamlit_folium import st_folium  # noqa: E402

import branca  # noqa: E402
import folium  # noqa: E402

if method == "Grid aggregation":
    cell_km = st.slider("Grid cell size (km)", 5, 100, 20, 5)
    gen = geo.grid_aggregate(source, cell_m=cell_km * 1000)
    st.session_state[dl.SS_GENERALIZED] = gen
    st.metric("Grid cells with points", len(gen))
    if len(gen):
        vmax = int(gen["n_points"].max())
        cmap = branca.colormap.LinearColormap(
            viz.sequential_hexes(ui.seq_palette(), 6), vmin=0, vmax=vmax,
            caption="points per cell")
        m = geo.base_map(gen)
        folium.GeoJson(
            gen.to_json(),
            style_function=lambda f: {
                "fillColor": cmap(f["properties"]["n_points"]),
                "color": "#555", "weight": 0.4, "fillOpacity": 0.7},
            tooltip=folium.GeoJsonTooltip(fields=["n_points"], aliases=["Points:"]),
        ).add_to(m)
        cmap.add_to(m)
        st_folium(m, use_container_width=True, height=520, returned_objects=[])
else:
    exclude = st.checkbox("Exclude noise points", value=True)
    if dl.SS_CLUSTERS not in st.session_state:
        st.info("Cluster centroids need DBSCAN clusters. Run **Clustering** first.")
        st.stop()
    gen = geo.cluster_centroids(st.session_state[dl.SS_CLUSTERS], exclude_noise=exclude)
    st.session_state[dl.SS_GENERALIZED] = gen
    st.metric("Cluster centroids", len(gen))
    if len(gen):
        m = geo.base_map(gen)
        vmax = int(gen["n_points"].max())
        for _, r in gen.iterrows():
            folium.CircleMarker(
                [r.geometry.y, r.geometry.x],
                radius=6 + 18 * (r["n_points"] / vmax),
                color=viz.NU_NAVY, fill=True, fill_opacity=0.6, weight=1,
                tooltip=f"Cluster {int(r['cluster_id'])} · {int(r['n_points'])} points",
            ).add_to(m)
        st_folium(m, use_container_width=True, height=520, returned_objects=[])

if dl.SS_GENERALIZED in st.session_state and len(st.session_state[dl.SS_GENERALIZED]):
    gen = st.session_state[dl.SS_GENERALIZED]
    st.download_button("⬇️ Download generalized layer (GeoJSON)",
                       gen.to_json(), "tala_generalized.geojson",
                       "application/geo+json")
