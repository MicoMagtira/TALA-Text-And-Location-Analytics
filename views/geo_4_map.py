import json

import streamlit as st

from core import data_loader as dl
from core import audio, geo, i18n, tracks, ui, viz

PAGE = "geo_4_map"

ui.page_header(PAGE, "geo")
ui.learn_page(
    PAGE,
    code=(
        "import geopandas as gpd\n\n"
        "land = gpd.read_file('data/ph_land.geojson').geometry.iloc[0]\n"
        "kept = gdf[gdf.geometry.within(land)].copy()\n"
        "kept.to_file('outputs/clipped.geojson', driver='GeoJSON')"
    ),
)

key = dl.geo_key()
eps_m, min_samples = dl.cluster_params()

st.markdown(i18n.t("geo_4_map.clip_head"))
if dl.cluster_params_are_default():
    st.caption(i18n.t("geo_2_cluster.using_defaults",
                      eps=int(eps_m / 1000), n=min_samples))
    st.page_link("views/geo_2_cluster.py", label=i18n.t("geo_2_cluster.nav"), icon="🎚️")

with audio.result(tracks.SIGNATURE[PAGE], key + (eps_m, min_samples)):
    clipped, clip_info = geo.clipped_for(*key, eps_m, min_samples)
if clip_info.get("clipped"):
    c1, c2, c3 = st.columns(3)
    c1.metric(i18n.t("geo_4_map.m_before"), f"{clip_info['before']:,}")
    c2.metric(i18n.t("geo_4_map.m_removed"), f"{clip_info['removed']:,}")
    c3.metric(i18n.t("geo_4_map.m_kept"), f"{clip_info['after']:,}")
else:
    ui.info(i18n.t("geo_4_map.no_land"))

st.markdown(i18n.t("geo_4_map.map_head"))
from core import maps  # noqa: E402


@st.fragment
def _map_view():
    """The 'show removed' toggle only redraws the map; exports below do not use it."""
    palette = viz.categorical(ui.palette(), 12)
    show_removed = st.checkbox(i18n.t("geo_4_map.show_removed"), value=False,
                               disabled=not clip_info.get("clipped"))
    layers = [maps.land_layer()]
    if "cluster_id" in clipped.columns:
        kept_frame = maps.cluster_frame(clipped, palette)
        layers.append(maps.cluster_layer(clipped, palette, frame=kept_frame))
    else:
        kept_frame = maps.to_frame(clipped, tip=None)
        layers.append(maps.points_layer(kept_frame))
    if show_removed and clip_info.get("removed"):
        # Validated points the land clip dropped: the CRS/bounds lesson made visible.
        all_pts, _ = geo.points_for(*key)
        removed = all_pts.loc[~all_pts.index.isin(clipped.index)]
        layers.append(maps.points_layer(maps.to_frame(removed),
                                        color=(214, 39, 40, 220), radius_px=4))
        st.caption(i18n.t("geo_4_map.removed_caption", n=len(removed)))
    st.pydeck_chart(
        maps.deck(layers, maps.view_for(kept_frame),
                  "{tip}" if "tip" in kept_frame.columns else None),
        height=520, width="stretch")
    if kept_frame.attrs.get("sampled"):
        st.caption(i18n.t("maps.sampled", shown=len(kept_frame),
                          total=kept_frame.attrs["total"]))


_map_view()

st.markdown(i18n.t("geo_4_map.exports_head"))
# The export payload is deliberately NOT localized: downstream lab worksheets
# and any shared analysis depend on these field names being identical for every
# trainee, whichever language they are reading the app in.
metadata = {
    "app": "TALA — Text And Location Analytics",
    "crs": "EPSG:4326",
    "clip": clip_info,
    "n_features_exported": int(len(clipped)),
    "generalization": st.session_state.get(dl.SS_GEN_PARAMS),
    "dbscan": {"eps_m": eps_m, "min_samples": min_samples},
}
e1, e2 = st.columns(2)
e1.download_button(i18n.t("geo_4_map.dl_geojson"), clipped.to_json(),
                   "tala_clipped.geojson", "application/geo+json")
e2.download_button(i18n.t("geo_4_map.dl_meta"), json.dumps(metadata, indent=2),
                   "tala_metadata.json", "application/json")

ui.page_done(PAGE)
ui.track_footer(PAGE)
