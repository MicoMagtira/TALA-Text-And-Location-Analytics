import streamlit as st

from core import data_loader as dl
from core import audio, geo, i18n, tracks, ui, viz

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

key = dl.geo_key()
eps_m, min_samples = dl.cluster_params()

from core import maps  # noqa: E402


@st.fragment
def _generalize():
    """Method, cell size and map affect only this block, so rerun only it."""
    grid_label = i18n.t("geo_3_generalize.grid")
    centroid_label = i18n.t("geo_3_generalize.centroids")
    method = st.radio(i18n.t("geo_3_generalize.method"),
                      [grid_label, centroid_label], horizontal=True)

    gen = None
    if method == grid_label:
        cell_km = st.slider(i18n.t("geo_3_generalize.cell"), 5, 100, 20, 5)
        with audio.result(tracks.SIGNATURE[PAGE], key + ("grid", cell_km * 1000)):
            gen = geo.grid_for(*key, cell_km * 1000)
        st.session_state[dl.SS_GEN_PARAMS] = ("grid", cell_km * 1000)
        if len(gen):
            vmax = int(gen["n_points"].max())
            hexes = viz.sequential_hexes(ui.seq_palette(), 6)
            tip = f"{i18n.t('geo_3_generalize.tooltip_points')} {{properties.n_points}}"
            st.pydeck_chart(
                maps.deck([maps.grid_layer(gen, hexes)],
                          maps.view_for(maps.bounds_frame(gen)), tip),
                height=520, width="stretch")
            # Legend: min to max along the same ramp the cells use.
            st.caption(f"{i18n.t('geo_3_generalize.legend')}: 1 to {vmax:,}")
            st.markdown(
                "<div style='height:10px;border-radius:5px;max-width:320px;"
                f"background:linear-gradient(to right,{','.join(hexes)})'></div>",
                unsafe_allow_html=True)
    else:
        exclude = st.checkbox(i18n.t("geo_3_generalize.exclude"), value=True)
        if dl.cluster_params_are_default():
            st.caption(i18n.t("geo_2_cluster.using_defaults",
                              eps=int(eps_m / 1000), n=min_samples))
            st.page_link("views/geo_2_cluster.py", label=i18n.t("geo_2_cluster.nav"),
                         icon=":material/tune:")
        with audio.result(tracks.SIGNATURE[PAGE],
                          key + ("centroids", eps_m, min_samples, exclude)):
            gen = geo.centroids_for(*key, eps_m, min_samples, exclude)
        st.session_state[dl.SS_GEN_PARAMS] = ("centroids", exclude)
        st.metric(i18n.t("geo_3_generalize.m_centroids"), len(gen))
        if len(gen):
            frame = maps.to_frame(
                gen, extra_cols=("cluster_id", "n_points"),
                tip=lambda g: [i18n.t("geo_3_generalize.cluster_tip",
                                      id=int(c), n=int(n))
                               for c, n in zip(g["cluster_id"], g["n_points"])])
            st.pydeck_chart(
                maps.deck([maps.centroid_layer(frame)], maps.view_for(frame), "{tip}"),
                height=520, width="stretch")

    if gen is not None and len(gen):
        st.download_button(i18n.t("geo_3_generalize.dl"),
                           gen.to_json(), "tala_generalized.geojson",
                           "application/geo+json")


_generalize()
ui.page_done(PAGE)
ui.track_footer(PAGE)
