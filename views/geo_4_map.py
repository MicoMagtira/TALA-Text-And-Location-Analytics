import json

import streamlit as st

from core import data_loader as dl
from core import geo, i18n, ui, viz

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

if not st.session_state.get(dl.SS_POINTS_READY):
    st.warning(i18n.t("geo_4_map.need"), icon="⚠️")
    st.stop()

key = dl.geo_key()
eps_m, min_samples = dl.cluster_params()

st.markdown(i18n.t("geo_4_map.clip_head"))
clipped, clip_info = geo.clipped_for(*key, eps_m, min_samples)
if clip_info.get("clipped"):
    c1, c2, c3 = st.columns(3)
    c1.metric(i18n.t("geo_4_map.m_before"), f"{clip_info['before']:,}")
    c2.metric(i18n.t("geo_4_map.m_removed"), f"{clip_info['removed']:,}")
    c3.metric(i18n.t("geo_4_map.m_kept"), f"{clip_info['after']:,}")
else:
    st.info(i18n.t("geo_4_map.no_land"))

st.markdown(i18n.t("geo_4_map.map_head"))
from streamlit_folium import st_folium  # noqa: E402

palette = viz.categorical(ui.palette(), 12)
m = geo.cluster_marker_map(clipped, palette) if "cluster_id" in clipped.columns \
    else geo.base_map(clipped)
import folium  # noqa: E402

folium.LayerControl().add_to(m)
st_folium(m, use_container_width=True, height=520, returned_objects=[])

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
