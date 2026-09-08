import streamlit as st

from core import data_loader as dl
from core import geo, i18n, ui, viz

PAGE = "geo_3_generalize"

ui.page_header(PAGE, "geo")
ui.learn_page(
    PAGE,
    code=(
        "from shapely.geometry import box\n\n"
        "# occupied cells only — never materialize an empty grid\n"
        "cell = 20000  # metres\n"
        "ix = np.floor((xy - [xmin, ymin]) / cell).astype(int)\n"
        "occupied, counts = np.unique(ix, axis=0, return_counts=True)\n"
        "cells = [box(xmin + i*cell, ymin + j*cell,\n"
        "             xmin + (i+1)*cell, ymin + (j+1)*cell) for i, j in occupied]"
    ),
)

if not st.session_state.get(dl.SS_POINTS_READY):
    st.warning(i18n.t("geo_3_generalize.need_points"), icon="⚠️")
    st.stop()

key = dl.geo_key()
eps_m, min_samples = dl.cluster_params()

grid_label = i18n.t("geo_3_generalize.grid")
centroid_label = i18n.t("geo_3_generalize.centroids")
method = st.radio(i18n.t("geo_3_generalize.method"),
                  [grid_label, centroid_label], horizontal=True)

from streamlit_folium import st_folium  # noqa: E402

import branca  # noqa: E402
import folium  # noqa: E402

gen = None
if method == grid_label:
    cell_km = st.slider(i18n.t("geo_3_generalize.cell"), 5, 100, 20, 5)
    gen = geo.grid_for(*key, cell_km * 1000)
    st.session_state[dl.SS_GEN_PARAMS] = ("grid", cell_km * 1000)
    if len(gen):
        vmax = int(gen["n_points"].max())
        cmap = branca.colormap.LinearColormap(
            viz.sequential_hexes(ui.seq_palette(), 6), vmin=0, vmax=vmax,
            caption=i18n.t("geo_3_generalize.legend"))
        m = geo.base_map(gen)
        folium.GeoJson(
            gen.to_json(),
            style_function=lambda f: {
                "fillColor": cmap(f["properties"]["n_points"]),
                "color": "#555", "weight": 0.4, "fillOpacity": 0.7},
            tooltip=folium.GeoJsonTooltip(
                fields=["n_points"],
                aliases=[i18n.t("geo_3_generalize.tooltip_points")]),
        ).add_to(m)
        cmap.add_to(m)
        st_folium(m, use_container_width=True, height=520, returned_objects=[])
else:
    exclude = st.checkbox(i18n.t("geo_3_generalize.exclude"), value=True)
    if eps_m is None:
        st.info(i18n.t("geo_3_generalize.need_clusters"))
        st.stop()
    gen = geo.centroids_for(*key, eps_m, min_samples, exclude)
    st.session_state[dl.SS_GEN_PARAMS] = ("centroids", exclude)
    st.metric(i18n.t("geo_3_generalize.m_centroids"), len(gen))
    if len(gen):
        m = geo.base_map(gen)
        vmax = int(gen["n_points"].max())
        for _, r in gen.iterrows():
            folium.CircleMarker(
                [r.geometry.y, r.geometry.x],
                radius=6 + 18 * (r["n_points"] / vmax),
                color=viz.NU_NAVY, fill=True, fill_opacity=0.6, weight=1,
                tooltip=i18n.t("geo_3_generalize.cluster_tip",
                               id=int(r["cluster_id"]), n=int(r["n_points"])),
            ).add_to(m)
        st_folium(m, use_container_width=True, height=520, returned_objects=[])

if gen is not None and len(gen):
    st.download_button(i18n.t("geo_3_generalize.dl"),
                       gen.to_json(), "tala_generalized.geojson",
                       "application/geo+json")
