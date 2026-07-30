"""Geospatial pipeline for TALA (ports Labs 1-5).

Lab 1 ingest + CRS validation -> Lab 2 DBSCAN -> Lab 3 generalization ->
Lab 4 PH-land clip + map/exports -> Lab 5 NLP per cluster. GeoDataFrames are
chained through st.session_state by the pages, mirroring the notebooks'
outputs/*.geojson hand-off.

Heavy geo deps (geopandas/shapely/pyproj/folium/geodatasets) import lazily.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st


# ---------------------------------------------------------------------------
# Lab 1 - Ingest & CRS correctness
# ---------------------------------------------------------------------------
def build_points(df: pd.DataFrame, lon_col: str, lat_col: str,
                 text_col: str | None = None):
    """Validate lon/lat, drop null/out-of-range, return (gdf_wgs84, report)."""
    import geopandas as gpd

    work = df.copy()
    n0 = len(work)
    work[lon_col] = pd.to_numeric(work[lon_col], errors="coerce")
    work[lat_col] = pd.to_numeric(work[lat_col], errors="coerce")
    n_null = work[[lon_col, lat_col]].isna().any(axis=1).sum()
    work = work.dropna(subset=[lon_col, lat_col])
    in_range = work[lon_col].between(-180, 180) & work[lat_col].between(-90, 90)
    n_oob = int((~in_range).sum())
    work = work[in_range]
    keep = [c for c in ({lon_col, lat_col} | ({text_col} if text_col else set())
                        | ({"id"} if "id" in work.columns else set())) if c in work.columns]
    gdf = gpd.GeoDataFrame(
        work[keep].reset_index(drop=True),
        geometry=gpd.points_from_xy(work[lon_col], work[lat_col]),
        crs="EPSG:4326",
    )
    report = {"input_rows": n0, "dropped_null": int(n_null),
              "dropped_out_of_range": n_oob, "valid_rows": len(gdf)}
    return gdf, report


def utm_epsg(gdf) -> int:
    lon = float(gdf.geometry.x.median())
    lat = float(gdf.geometry.y.median())
    zone = int((lon + 180) // 6) + 1
    return (32600 if lat >= 0 else 32700) + zone


def to_metric(gdf):
    return gdf.to_crs(epsg=utm_epsg(gdf))


def nn_distance_stats(gdf_metric) -> dict:
    from sklearn.neighbors import NearestNeighbors

    xy = np.column_stack([gdf_metric.geometry.x, gdf_metric.geometry.y])
    if len(xy) < 2:
        return {}
    nn = NearestNeighbors(n_neighbors=2).fit(xy)
    d, _ = nn.kneighbors(xy)
    nd = d[:, 1]
    return {"min_m": float(nd.min()), "median_m": float(np.median(nd)),
            "mean_m": float(nd.mean()), "max_m": float(nd.max())}


# ---------------------------------------------------------------------------
# Lab 2 - DBSCAN
# ---------------------------------------------------------------------------
def k_distance(gdf_metric, k: int = 10) -> np.ndarray:
    """Sorted distance to the k-th neighbor (for the elbow that sets eps)."""
    from sklearn.neighbors import NearestNeighbors

    xy = np.column_stack([gdf_metric.geometry.x, gdf_metric.geometry.y])
    nn = NearestNeighbors(n_neighbors=k + 1).fit(xy)
    d, _ = nn.kneighbors(xy)
    return np.sort(d[:, k])


def run_dbscan(gdf, eps_m: float = 15000, min_samples: int = 10):
    """DBSCAN on projected metric coords. Returns WGS84 gdf with cluster_id."""
    from sklearn.cluster import DBSCAN

    gm = to_metric(gdf)
    xy = np.column_stack([gm.geometry.x, gm.geometry.y])
    labels = DBSCAN(eps=eps_m, min_samples=min_samples).fit_predict(xy)
    out = gdf.copy()
    out["cluster_id"] = labels
    n_clusters = len({c for c in labels if c != -1})
    n_noise = int((labels == -1).sum())
    return out, {"n_clusters": n_clusters, "n_noise": n_noise,
                 "eps_m": eps_m, "min_samples": min_samples}


# ---------------------------------------------------------------------------
# Lab 3 - Generalization
# ---------------------------------------------------------------------------
def grid_aggregate(gdf, cell_m: float = 20000, max_cells: int = 20000):
    import geopandas as gpd
    from shapely.geometry import box

    gm = to_metric(gdf)
    xy = np.column_stack([gm.geometry.x, gm.geometry.y])
    # Robust bounds: use the 1st-99th percentile so the deliberately dirty
    # far-off points (London, California, impossible coords) — which are not
    # removed until the land-clip step — cannot explode the projected extent.
    xmin, xmax = np.percentile(xy[:, 0], [1, 99])
    ymin, ymax = np.percentile(xy[:, 1], [1, 99])
    span_x, span_y = max(xmax - xmin, cell_m), max(ymax - ymin, cell_m)
    # Enlarge the cell if the grid would exceed the hard cell cap.
    est_cells = (span_x / cell_m + 1) * (span_y / cell_m + 1)
    if est_cells > max_cells:
        cell_m = float(np.sqrt(span_x * span_y / max_cells))
    xs = np.arange(xmin, xmax + cell_m, cell_m)
    ys = np.arange(ymin, ymax + cell_m, cell_m)
    cells, counts = [], []
    for x0 in xs[:-1]:
        for y0 in ys[:-1]:
            mask = (xy[:, 0] >= x0) & (xy[:, 0] < x0 + cell_m) & \
                   (xy[:, 1] >= y0) & (xy[:, 1] < y0 + cell_m)
            n = int(mask.sum())
            if n:
                cells.append(box(x0, y0, x0 + cell_m, y0 + cell_m))
                counts.append(n)
    grid = gpd.GeoDataFrame({"n_points": counts}, geometry=cells, crs=gm.crs)
    return grid.to_crs(epsg=4326)


def cluster_centroids(gdf, exclude_noise: bool = True):
    import geopandas as gpd
    from shapely.geometry import Point

    gm = to_metric(gdf)
    rows = []
    for cid, grp in gm.groupby("cluster_id"):
        if exclude_noise and cid == -1:
            continue
        rows.append({"cluster_id": int(cid), "n_points": len(grp),
                     "geometry": Point(grp.geometry.x.mean(), grp.geometry.y.mean())})
    cent = gpd.GeoDataFrame(rows, geometry="geometry", crs=gm.crs)
    return cent.to_crs(epsg=4326)


# ---------------------------------------------------------------------------
# Lab 4 - PH land clip
# ---------------------------------------------------------------------------
PH_BBOX = (116.0, 4.5, 127.0, 21.5)  # lon/lat window around the Philippines


@st.cache_resource(show_spinner="Loading Philippines land boundary…")
def ph_land():
    """Philippine land polygon: Natural Earth land clipped to the PH window.

    geodatasets only ships global `naturalearth.land` (no per-country names), so
    we intersect it with the PH bounding box to get the actual island landmass,
    then buffer it slightly so the coarse 110m coastline does not drop legitimate
    coastal points. Falls back to the plain bounding box if the download fails
    (keeps the app usable offline)."""
    from shapely.geometry import box

    ph_box = box(*PH_BBOX)
    try:
        import geodatasets
        import geopandas as gpd

        land = gpd.read_file(geodatasets.get_path("naturalearth.land")).to_crs(4326)
        clipped = land.clip(ph_box)
        geom = clipped.geometry.union_all().buffer(0.15)  # ~15 km grace on coasts
        if geom and not geom.is_empty:
            return geom
    except Exception:
        pass
    return ph_box


def clip_to_ph(gdf):
    land = ph_land()
    if land is None:
        return gdf, {"clipped": False}
    before = len(gdf)
    out = gdf[gdf.geometry.within(land)].copy()
    return out, {"clipped": True, "before": before, "after": len(out),
                 "removed": before - len(out)}


# ---------------------------------------------------------------------------
# Lab 5 - NLP per cluster (privacy-safe: aggregates only)
# ---------------------------------------------------------------------------
def per_cluster_nlp(gdf, text_col: str, top_terms: int = 8) -> pd.DataFrame:
    from sklearn.feature_extraction.text import TfidfVectorizer

    from . import preprocess
    from .nlp import _vader

    sia = _vader()
    rows = []
    for cid, grp in gdf.groupby("cluster_id"):
        if cid == -1 or text_col not in grp.columns:
            continue
        cleaned = preprocess.clean_corpus(grp[text_col].dropna().astype(str))
        cleaned = [c for c in cleaned if c.strip()]
        top = []
        if cleaned:
            try:
                vec = TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_features=400)
                X = vec.fit_transform(cleaned)
                terms = vec.get_feature_names_out()
                scores = np.asarray(X.mean(axis=0)).ravel()
                top = [terms[i] for i in scores.argsort()[::-1][:top_terms]]
            except ValueError:
                top = []
        comps = [sia.polarity_scores(str(t))["compound"]
                 for t in grp[text_col].dropna().astype(str)]
        pos = sum(1 for c in comps if c >= 0.05)
        neg = sum(1 for c in comps if c <= -0.05)
        neu = len(comps) - pos - neg
        majority = max([("positive", pos), ("negative", neg), ("neutral", neu)],
                       key=lambda kv: kv[1])[0] if comps else "n/a"
        rows.append({"cluster_id": int(cid), "n_points": len(grp),
                     "top_terms": ", ".join(top), "tag": _auto_tag(top),
                     "sentiment": majority,
                     "pos_%": round(100 * pos / len(comps), 1) if comps else 0,
                     "neg_%": round(100 * neg / len(comps), 1) if comps else 0,
                     "neu_%": round(100 * neu / len(comps), 1) if comps else 0})
    return pd.DataFrame(rows).sort_values("n_points", ascending=False)


def _auto_tag(terms: list[str]) -> str:
    text = " ".join(terms).lower()
    rules = [("staff", "Staff Experience"), ("wait", "Waiting Time"),
             ("clean", "Facility & Cleanliness"), ("doctor", "Clinical Care"),
             ("medicine", "Medicines & Supplies"), ("appointment", "Scheduling"),
             ("kind", "Staff Experience"), ("service", "Service Quality")]
    for kw, tag in rules:
        if kw in text:
            return tag
    return "General Feedback"


# ---------------------------------------------------------------------------
# Folium map helpers
# ---------------------------------------------------------------------------
def base_map(gdf=None, zoom_start: int = 6):
    import folium

    if gdf is not None and len(gdf):
        # total_bounds works for any geometry type (points, polygons, grids).
        minx, miny, maxx, maxy = gdf.total_bounds
        center = [float((miny + maxy) / 2), float((minx + maxx) / 2)]
    else:
        center = [12.8, 121.8]  # Philippines
    return folium.Map(location=center, zoom_start=zoom_start,
                      tiles="CartoDB positron", control_scale=True)


def cluster_marker_map(gdf, palette_hexes: list[str], max_points: int = 4000):
    import folium
    from folium.plugins import MarkerCluster

    m = base_map(gdf)
    mc = MarkerCluster().add_to(m)
    sample = gdf.sample(min(len(gdf), max_points), random_state=1) if len(gdf) > max_points else gdf
    for _, r in sample.iterrows():
        cid = int(r.get("cluster_id", 0))
        color = "#999999" if cid == -1 else palette_hexes[cid % len(palette_hexes)]
        folium.CircleMarker(
            location=[r.geometry.y, r.geometry.x], radius=4,
            color=color, fill=True, fill_opacity=0.8, weight=1,
            tooltip=f"Cluster {cid}" if cid != -1 else "Noise",
        ).add_to(mc)
    return m
