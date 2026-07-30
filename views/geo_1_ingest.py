import streamlit as st

from core import data_loader as dl
from core import geo, ui

ui.page_title("Geospatial", "Ingest & CRS Validation",
              "Build spatial points from the coordinates, validate them, and "
              "reproject to a metric CRS — the foundation for every geo step.")

ui.learn(
    "CRS validation & reprojection (Lab 1)",
    "Two numbers in a spreadsheet are not yet a location. This lab turns `lon`/`lat` "
    "columns into geometry a computer can measure with, and every later page depends on "
    "getting it right here.\n\n"
    "**The validation gate.** 12,000 input rows lose 29 to missing coordinates and 256 "
    "to values outside the valid ranges (longitude ±180, latitude ±90), leaving 11,715 "
    "points. Note what that gate does *not* catch: a comment about Cebu carrying "
    "London's coordinates is perfectly valid as a number and survives untouched. Bounds "
    "checking proves a coordinate is well-formed, never that it is correct.\n\n"
    "**`set_crs` versus `to_crs` — the classic error.** `set_crs` *declares* what your "
    "numbers already mean; `to_crs` *converts* them to a different system. Calling "
    "`set_crs` when you meant `to_crs` silently relabels your data instead of moving it, "
    "and nothing errors — the points simply land in the wrong place on every subsequent "
    "map. If a layer looks shifted, suspect this first.\n\n"
    "**Why the reprojection is not optional.** EPSG:4326 measures in degrees, and a "
    "degree of longitude is ~111 km at the equator but shrinks toward the poles, so "
    "degree distances are not comparable across a map. DBSCAN's `eps` on the next page "
    "is a *distance*, so the data must first move to a metre-based CRS — here "
    "**EPSG:32651** (UTM zone 51N), chosen automatically from the median longitude.\n\n"
    "**Read the nearest-neighbour check as a diagnostic.** Median 2.3 km is sensible for "
    "health facilities. The two extremes are the interesting part: **minimum 0 m** means "
    "at least two points share identical coordinates — duplicates, or several comments "
    "rounded to the same facility — which will inflate density for DBSCAN. **Maximum 175 "
    "km** is the far-flung junk announcing itself before any map is drawn.\n\n"
    "**On privacy.** From this point you hold precise locations attached to personal "
    "accounts of medical visits. That combination is re-identifying. Everything you share "
    "from here should be aggregated — which is what Labs 3 and 5 build.",
    code=(
        "import geopandas as gpd\n"
        "gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lon, df.lat),\n"
        "                       crs='EPSG:4326')          # declare WGS84\n"
        "zone = int((gdf.geometry.x.median() + 180)//6) + 1\n"
        "gdf_m = gdf.to_crs(epsg=32600 + zone)            # transform to UTM metres"
    ),
)

if not dl.has_geo():
    st.warning("The active dataset has no longitude/latitude columns. Set them on "
               "**Text Analytics → Data & Preprocessing**.", icon="⚠️")
    st.stop()

key = dl.geo_key()

try:
    # Shared across sessions: the whole cohort on the bundled dataset resolves to
    # one cached layer instead of one 14 MB copy each.
    gdf, report = geo.points_for(*key)
except Exception as e:  # geopandas / shapely import or geometry error
    st.error(f"Could not build geometry: {e}")
    st.stop()

if gdf is None:
    st.error("The active dataset is no longer available. Re-upload it on "
             "**Text Analytics → Data & Preprocessing**.")
    st.stop()

# Session state records only that this trainee has completed Lab 1 — the layer
# itself lives in the shared cache.
st.session_state[dl.SS_POINTS_READY] = True

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
