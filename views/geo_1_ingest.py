import streamlit as st

from core import data_loader as dl
from core import geo, i18n, ui

PAGE = "geo_1_ingest"

ui.page_header(PAGE, "geo")
ui.learn_page(
    PAGE,
    code=(
        "import geopandas as gpd\n"
        "gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat),\n"
        "                       crs='EPSG:4326')          # declare WGS84\n"
        "zone = int((gdf.geometry.x.median() + 180)//6) + 1\n"
        "gdf_m = gdf.to_crs(epsg=32600 + zone)            # transform to UTM metres"
    ),
)

if not dl.has_geo():
    st.warning(i18n.t("geo_1_ingest.no_geo"), icon="⚠️")
    st.stop()

key = dl.geo_key()

try:
    # Shared across sessions: the whole cohort on the bundled dataset resolves to
    # one cached layer instead of one 14 MB copy each.
    gdf, report = geo.points_for(*key)
except Exception as e:  # geopandas / shapely import or geometry error
    st.error(i18n.t("geo_1_ingest.geom_error", error=e))
    st.stop()

if gdf is None:
    st.error(i18n.t("geo_1_ingest.gone"))
    st.stop()

# Session state records only that this trainee has completed Lab 1 — the layer
# itself lives in the shared cache.
st.session_state[dl.SS_POINTS_READY] = True

st.markdown(i18n.t("geo_1_ingest.report_head"))
c1, c2, c3, c4 = st.columns(4)
c1.metric(i18n.t("geo_1_ingest.m_input"), f"{report['input_rows']:,}")
c2.metric(i18n.t("geo_1_ingest.m_null"), f"{report['dropped_null']:,}")
c3.metric(i18n.t("geo_1_ingest.m_oob"), f"{report['dropped_out_of_range']:,}")
c4.metric(i18n.t("geo_1_ingest.m_valid"), f"{report['valid_rows']:,}")

st.caption(i18n.t("geo_1_ingest.crs_caption", epsg=geo.utm_epsg(gdf)))

nn = geo.nn_distance_stats(geo.to_metric(gdf))
if nn:
    st.markdown(i18n.t("geo_1_ingest.nn_head"))
    d1, d2, d3 = st.columns(3)
    d1.metric(i18n.t("geo_1_ingest.m_median"), f"{nn['median_m'] / 1000:.1f} km")
    d2.metric(i18n.t("geo_1_ingest.m_min"), f"{nn['min_m']:.0f} m")
    d3.metric(i18n.t("geo_1_ingest.m_max"), f"{nn['max_m'] / 1000:.0f} km")

st.markdown(i18n.t("geo_1_ingest.map_head"))
st.caption(i18n.t("geo_1_ingest.map_caption"))
import html as _html  # noqa: E402

from core import maps  # noqa: E402

# ALL valid points go to the browser (pydeck draws them on the GPU); only the
# 50k safety cap in to_frame can thin them, and then we say so.
text_col = key[3]
frame = maps.to_frame(
    gdf, tip=(lambda g: [_html.escape(str(v)) for v in g[text_col].fillna("")])
    if text_col in gdf.columns else None)
st.pydeck_chart(
    maps.deck([maps.points_layer(frame)], maps.view_for(frame),
              "{tip}" if "tip" in frame.columns else None),
    height=520, width="stretch")
if frame.attrs.get("sampled"):
    st.caption(i18n.t("maps.sampled", shown=len(frame), total=frame.attrs["total"]))

st.success(i18n.t("geo_1_ingest.success"), icon="➡️")
