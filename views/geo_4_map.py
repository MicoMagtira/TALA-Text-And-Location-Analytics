import io
import json

import matplotlib.pyplot as plt
import streamlit as st

from core import data_loader as dl
from core import geo, ui, viz

ui.page_title("Geospatial", "Map & Exports",
              "Clip to Philippine land (removing the bogus off-PH coordinates), "
              "render a publication map, and export the stable output contract.")
viz.apply_matplotlib_theme()

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

st.markdown("#### 2 · Publication map")
gen = st.session_state.get(dl.SS_GENERALIZED)
fig, ax = plt.subplots(figsize=(7, 8))
land = geo.ph_land()
if land is not None:
    import geopandas as gpd

    gpd.GeoSeries([land], crs="EPSG:4326").plot(ax=ax, color="#eef0f7",
                                                edgecolor="#c9cee8", linewidth=0.6)
if gen is not None and "n_points" in gen.columns and len(gen):
    gen.plot(ax=ax, column="n_points", cmap=viz.sequential_cmap(ui.seq_palette()),
             legend=True, markersize=25, alpha=0.8,
             legend_kwds={"label": "points", "shrink": 0.5})
else:
    clipped.plot(ax=ax, color=viz.NU_NAVY, markersize=3, alpha=0.5)
ax.set_title("TALA — Generalized health-service feedback (PH)")
ax.set_axis_off()
st.pyplot(fig, width="stretch")

png_buf = io.BytesIO()
fig.savefig(png_buf, format="png", dpi=240, bbox_inches="tight")

st.markdown("#### 3 · Interactive map")
from streamlit_folium import st_folium  # noqa: E402

palette = viz.categorical(ui.palette(), 12)
m = geo.cluster_marker_map(clipped, palette) if "cluster_id" in clipped.columns \
    else geo.base_map(clipped)
import folium  # noqa: E402

folium.LayerControl().add_to(m)
st_folium(m, use_container_width=True, height=520, returned_objects=[])

st.markdown("#### 4 · Exports (stable output contract)")
metadata = {
    "app": "TALA — Text And Location Analytics",
    "crs": "EPSG:4326",
    "clip": clip_info,
    "n_features_exported": int(len(clipped)),
    "generalized_features": int(len(gen)) if gen is not None else 0,
    "dbscan": {"eps_m": None, "min_samples": None},
}
e1, e2, e3 = st.columns(3)
e1.download_button("⬇️ Clipped layer (GeoJSON)", clipped.to_json(),
                   "tala_clipped.geojson", "application/geo+json")
e2.download_button("⬇️ Map (PNG)", png_buf.getvalue(), "tala_map.png", "image/png")
e3.download_button("⬇️ metadata.json", json.dumps(metadata, indent=2),
                   "tala_metadata.json", "application/json")

ui.learn(
    "Land clipping & the output contract (Lab 4)",
    "The bogus coordinates (London, California…) are only removed **now**, by "
    "spatially clipping to the **Philippine land polygon** from Natural Earth — a "
    "principled geometric filter, not an arbitrary bounding box. The finished layer "
    "is exported as GeoJSON + a static PNG + a `metadata.json` that records the CRS "
    "and parameters, so downstream steps consume a **stable, documented contract**.\n\n"
    "Note the deployment pattern: the boundary is derived from Natural Earth **once, "
    "at build time**, and shipped as an 11 KB simplified GeoJSON. Fetching and "
    "dissolving a global land layer inside the app would repeat that work in every "
    "container and add a network dependency to the request path.",
    code=(
        "# Build step (run once, offline):\n"
        "import geopandas as gpd, geodatasets\n"
        "world = gpd.read_file(geodatasets.get_path('naturalearth.land')).to_crs(4326)\n"
        "ph = world.clip(box(*PH_BBOX)).geometry.union_all().buffer(0.15)\n"
        "gpd.GeoSeries([ph.simplify(0.01)], crs=4326).to_file('data/ph_land.geojson')\n\n"
        "# App step (every run, no network):\n"
        "ph_land = gpd.read_file('data/ph_land.geojson').geometry.iloc[0]\n"
        "kept = gdf[gdf.geometry.within(ph_land)]          # spatial clip\n"
        "kept.to_file('map.geojson', driver='GeoJSON')"
    ),
)
