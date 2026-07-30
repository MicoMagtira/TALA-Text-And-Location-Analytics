import streamlit as st

from core import data_loader as dl
from core import geo, ui, viz

ui.page_title("Geospatial", "Generalization",
              "Summarize points into coarser features so patterns read at a glance "
              "and individual locations are not exposed.")

ui.learn(
    "Generalization: grid vs centroids (Lab 3)",
    "Generalization is the step where you *deliberately destroy precision*. That sounds "
    "like damage, and it is — chosen on purpose, because a map of exact coordinates "
    "attached to medical complaints is both harder to read and unsafe to publish. The "
    "question is not whether to lose detail but which detail you can afford to lose.\n\n"
    "**Grid aggregation** lays equal metre-based squares over the projected points and "
    "counts what falls in each. Every location becomes \"somewhere in this cell\". At 20 "
    "km this corpus yields **387 populated cells**, the busiest holding 506 points and "
    "the median holding just 4 — a long-tailed distribution worth noticing, because a "
    "choropleth of it will be dominated by a handful of cells.\n\n"
    "**Cluster centroids** replace each DBSCAN cluster with one representative point "
    "carrying the member count, giving **29 markers** instead of 11,715. Far cleaner, but "
    "it inherits every parameter choice from the previous page — change `eps` and your "
    "centroids move.\n\n"
    "**Choosing between them.** Grids answer \"where is activity concentrated?\" and "
    "cover everywhere, including sparse areas. Centroids answer \"where are the dense "
    "groups we identified?\" and are silent about everything DBSCAN called noise. Grids "
    "impose an arbitrary lattice that can split one real hotspot across four cells; "
    "centroids place a marker at a mean position where possibly nobody was — a centroid "
    "can land in the sea.\n\n"
    "**Cell size is a privacy control, not just a visual one.** Shrink the cells and "
    "counts drop until a cell contains one person at a known address. A common rule is "
    "to suppress or merge any cell below a minimum count (often 5). Use the slider and "
    "watch the median count fall — that is your privacy budget being spent.\n\n"
    "**The question to carry forward:** what does this representation hide, and is that "
    "the detail I intended to remove?",
    code=(
        "from shapely.geometry import box, Point\n"
        "# grid: count points inside each cell\n"
        "cell = box(x0, y0, x0 + size, y0 + size)\n\n"
        "# centroid: one point per cluster\n"
        "Point(grp.geometry.x.mean(), grp.geometry.y.mean())"
    ),
)

if not st.session_state.get(dl.SS_POINTS_READY):
    st.warning("Build points (Ingest) — and ideally clusters (DBSCAN) — first.",
               icon="⚠️")
    st.stop()

key = dl.geo_key()
eps_m, min_samples = dl.cluster_params()

method = st.radio("Method", ["Grid aggregation", "Cluster centroids"], horizontal=True)

from streamlit_folium import st_folium  # noqa: E402

import branca  # noqa: E402
import folium  # noqa: E402

gen = None
if method == "Grid aggregation":
    cell_km = st.slider("Grid cell size (km)", 5, 100, 20, 5)
    gen = geo.grid_for(*key, cell_km * 1000)
    st.session_state[dl.SS_GEN_PARAMS] = ("grid", cell_km * 1000)
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
    if eps_m is None:
        st.info("Cluster centroids need DBSCAN clusters. Run **Clustering** first.")
        st.stop()
    gen = geo.centroids_for(*key, eps_m, min_samples, exclude)
    st.session_state[dl.SS_GEN_PARAMS] = ("centroids", exclude)
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

if gen is not None and len(gen):
    st.download_button("⬇️ Download generalized layer (GeoJSON)",
                       gen.to_json(), "tala_generalized.geojson",
                       "application/geo+json")
