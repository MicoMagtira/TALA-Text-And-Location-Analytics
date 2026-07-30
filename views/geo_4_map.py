import json

import streamlit as st

from core import data_loader as dl
from core import geo, ui, viz

ui.page_title("Geospatial", "Map & Exports",
              "Clip to Philippine land (removing the bogus off-PH coordinates), "
              "explore the interactive map, and export the stable output contract.")

ui.learn(
    "Land clipping & the output contract (Lab 4)",
    "Here is the number that should stop you: clipping removes **3,467 of 11,715 "
    "points**. Nearly a third of this dataset was never in the Philippines, and it "
    "survived every previous page. Lab 1's bounds check passed them because London and "
    "California are valid coordinates. DBSCAN clustered them. The maps you have already "
    "looked at all included them.\n\n"
    "**Nothing warned you.** That is the lesson of this page, and the reason the dirty "
    "coordinates were left in this long on purpose. Bad spatial data does not announce "
    "itself; it produces confident, attractive, wrong output at every intermediate step.\n\n"
    "**Polygon, not bounding box.** A rectangle around the Philippines would also catch "
    "chunks of Malaysia, Taiwan and open sea. Clipping to the actual land geometry is a "
    "*principled* filter — a point is kept because it falls on the country, not because "
    "it falls in a convenient rectangle. The polygon is buffered ~15 km so a coarse "
    "coastline does not discard legitimate seaside facilities; without that buffer you "
    "silently lose real coastal data, which is its own quiet failure.\n\n"
    "**The output contract.** Exports pair the GeoJSON with a `metadata.json` recording "
    "CRS, the clipping decision and counts, DBSCAN parameters and the generalization "
    "method. This is what makes the work reproducible: someone receiving your layer "
    "should never have to guess whether coordinates are lon/lat or projected, or whether "
    "3,467 records were dropped. A layer without that metadata is not a finished "
    "deliverable.\n\n"
    "**Before you publish.** Prefer the aggregated layers from Lab 3 over raw points. A "
    "map is a rhetorical object — readers grant it more authority than a table, so state "
    "your filtering choices *on the map itself*, and never let a point pattern imply a "
    "cause it cannot support.",
    code=(
        "# App step (every run, no network):\n"
        "ph_land = gpd.read_file('data/ph_land.geojson').geometry.iloc[0]\n"
        "kept = gdf[gdf.geometry.within(ph_land)]          # spatial clip\n"
        "metadata = {'crs': 'EPSG:4326', 'n_features_exported': len(kept)}\n"
        "kept.to_file('map.geojson', driver='GeoJSON')"
    ),
)

if not st.session_state.get(dl.SS_POINTS_READY):
    st.warning("Build points and clusters first (Ingest → Clustering).", icon="⚠️")
    st.stop()

key = dl.geo_key()
eps_m, min_samples = dl.cluster_params()

st.markdown("#### 1 · Clip to Philippine land")
clipped, clip_info = geo.clipped_for(*key, eps_m, min_samples)
if clip_info.get("clipped"):
    c1, c2, c3 = st.columns(3)
    c1.metric("Before", f"{clip_info['before']:,}")
    c2.metric("Removed (off-PH)", f"{clip_info['removed']:,}")
    c3.metric("Kept", f"{clip_info['after']:,}")
else:
    st.info("Land boundary unavailable; showing unclipped points.")

st.markdown("#### 2 · Interactive map")
from streamlit_folium import st_folium  # noqa: E402

palette = viz.categorical(ui.palette(), 12)
m = geo.cluster_marker_map(clipped, palette) if "cluster_id" in clipped.columns \
    else geo.base_map(clipped)
import folium  # noqa: E402

folium.LayerControl().add_to(m)
st_folium(m, use_container_width=True, height=520, returned_objects=[])

st.markdown("#### 3 · Exports (stable output contract)")
metadata = {
    "app": "TALA — Text And Location Analytics",
    "crs": "EPSG:4326",
    "clip": clip_info,
    "n_features_exported": int(len(clipped)),
    "generalization": st.session_state.get(dl.SS_GEN_PARAMS),
    "dbscan": {"eps_m": eps_m, "min_samples": min_samples},
}
e1, e2 = st.columns(2)
e1.download_button("⬇️ Clipped layer (GeoJSON)", clipped.to_json(),
                   "tala_clipped.geojson", "application/geo+json")
e2.download_button("⬇️ metadata.json", json.dumps(metadata, indent=2),
                   "tala_metadata.json", "application/json")
