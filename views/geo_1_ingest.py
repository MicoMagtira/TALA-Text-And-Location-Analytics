import streamlit as st

from core import data_loader as dl
from core import geo, ui

ui.page_title("Geospatial", "Ingest & CRS Validation",
              "Build spatial points from the coordinates, validate them, and "
              "reproject to a metric CRS — the foundation for every geo step.")

if not dl.has_geo():
    st.warning("The active dataset has no longitude/latitude columns. Set them on "
               "**Text Analytics → Data & Preprocessing**.", icon="⚠️")
    st.stop()

df = dl.active_df()
lon = st.session_state[dl.SS_LON_COL]
lat = st.session_state[dl.SS_LAT_COL]
text_col = st.session_state[dl.SS_TEXT_COL]

try:
    gdf, report = geo.build_points(df, lon, lat, text_col)
except Exception as e:  # geopandas / shapely import or geometry error
    st.error(f"Could not build geometry: {e}")
    st.stop()

st.session_state[dl.SS_POINTS] = gdf

st.markdown("#### Validation report")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Input rows", f"{report['input_rows']:,}")
c2.metric("Dropped: null coords", f"{report['dropped_null']:,}")
c3.metric("Dropped: out of range", f"{report['dropped_out_of_range']:,}")
c4.metric("Valid points", f"{report['valid_rows']:,}")

st.caption(f"Auto-selected projected CRS for metric distances: **EPSG:{geo.utm_epsg(gdf)}** "
           "(UTM zone from the data's median longitude; PH ≈ 32651).")

nn = geo.nn_distance_stats(geo.to_metric(gdf))
if nn:
    st.markdown("#### Nearest-neighbor distance (sanity check)")
    d1, d2, d3 = st.columns(3)
    d1.metric("Median NN", f"{nn['median_m'] / 1000:.1f} km")
    d2.metric("Min NN", f"{nn['min_m']:.0f} m")
    d3.metric("Max NN", f"{nn['max_m'] / 1000:.0f} km")

st.markdown("#### Map of valid points")
st.caption("Note: at this stage only global lon/lat bounds are enforced — obviously "
           "off-Philippines points (London, California, …) survive on purpose. They "
           "get removed later by land-clipping on the **Map & Exports** page.")
from streamlit_folium import st_folium  # noqa: E402

import folium  # noqa: E402
from folium.plugins import MarkerCluster  # noqa: E402

m = geo.base_map(gdf)
mc = MarkerCluster().add_to(m)
sample = gdf.sample(min(len(gdf), 3000), random_state=1)
for _, r in sample.iterrows():
    folium.CircleMarker([r.geometry.y, r.geometry.x], radius=3,
                        color="#35408E", fill=True, fill_opacity=0.7,
                        weight=1).add_to(mc)
st_folium(m, use_container_width=True, height=520, returned_objects=[])

st.success("Points ready. Continue to **Geospatial → Clustering (DBSCAN)**.", icon="➡️")

ui.learn(
    "CRS validation & reprojection (Lab 1)",
    "Raw coordinates are dirty: some are null, some out of the valid lon/lat range. "
    "We coerce to numeric, drop bad rows, and build a **WGS84 (EPSG:4326)** "
    "`GeoDataFrame`. Because distances in degrees are meaningless, we reproject to a "
    "**metric UTM** CRS (auto-picked from the median longitude) whenever we need "
    "meters — e.g. DBSCAN's `eps`. This is the classic `set_crs` (declare) vs "
    "`to_crs` (transform) distinction.",
    code=(
        "import geopandas as gpd\n"
        "gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat),\n"
        "                       crs='EPSG:4326')          # declare WGS84\n"
        "zone = int((gdf.geometry.x.median() + 180)//6) + 1\n"
        "gdf_m = gdf.to_crs(epsg=32600 + zone)            # transform to UTM metres"
    ),
)
