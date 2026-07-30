import json

import streamlit as st

from core import data_loader as dl
from core import geo, ui, viz

ui.page_title("Geospatial", "Map & Exports",
              "Clip to Philippine land (removing the bogus off-PH coordinates), "
              "explore the interactive map, and export the stable output contract.")

ui.learn(
    "Land clipping & the output contract (Lab 4)",
    "This page applies a Philippines land polygon, not a simple rectangular bounding box. "
    "That distinction removes overseas or implausible locations more defensibly while "
    "retaining the geographic shape of the country. Compare the before/removed/kept counts "
    "and investigate surprising removals—coastal locations can need particular care.\n\n"
    "The GeoJSON and `metadata.json` form an output contract: another person can see the "
    "CRS, clipping decision, record count, and analysis context without guessing. Export "
    "aggregated or clipped data when sharing. A map is a communication aid, so document "
    "its filtering choices and never treat an unverified point pattern as a causal claim.",
    code=(
        "# App step (every run, no network):\n"
        "ph_land = gpd.read_file('data/ph_land.geojson').geometry.iloc[0]\n"
        "kept = gdf[gdf.geometry.within(ph_land)]          # spatial clip\n"
        "metadata = {'crs': 'EPSG:4326', 'n_features_exported': len(kept)}\n"
        "kept.to_file('map.geojson', driver='GeoJSON')"
    ),
)

if dl.SS_CLUSTERS not in st.session_state and dl.SS_POINTS not in st.session_state:
    st.warning("Build points and clusters first (Ingest → Clustering).", icon="⚠️")
    st.stop()

src = st.session_state.get(dl.SS_CLUSTERS, st.session_state.get(dl.SS_POINTS))

st.markdown("#### 1 · Clip to Philippine land")
with st.spinner("Loading land boundary and clipping…"):
    clipped, clip_info = geo.clip_to_ph(src)
if clip_info.get("clipped"):
    c1, c2, c3 = st.columns(3)
    c1.metric("Before", f"{clip_info['before']:,}")
    c2.metric("Removed (off-PH)", f"{clip_info['removed']:,}")
    c3.metric("Kept", f"{clip_info['after']:,}")
else:
    st.info("Land boundary unavailable; showing unclipped points.")

gen = st.session_state.get(dl.SS_GENERALIZED)
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
    "generalized_features": int(len(gen)) if gen is not None else 0,
    "dbscan": {"eps_m": None, "min_samples": None},
}
e1, e2 = st.columns(2)
e1.download_button("⬇️ Clipped layer (GeoJSON)", clipped.to_json(),
                   "tala_clipped.geojson", "application/geo+json")
e2.download_button("⬇️ metadata.json", json.dumps(metadata, indent=2),
                   "tala_metadata.json", "application/json")
