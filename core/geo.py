"""Geospatial pipeline for TALA (ports Labs 1-5).

Lab 1 ingest + CRS validation -> Lab 2 DBSCAN -> Lab 3 generalization ->
Lab 4 PH-land clip + map/exports -> Lab 5 NLP per cluster. GeoDataFrames are
chained through st.session_state by the pages, mirroring the notebooks'
outputs/*.geojson hand-off.

Heavy geo deps (geopandas/shapely/pyproj/folium) import lazily, so the text
pages never pay for them.

Concurrency model
-----------------
An 11,715-point GeoDataFrame is ~14 MB live, and the walkthrough produces two of
them (points, clusters) plus the generalized layer. Parking those in
``st.session_state`` cost every trainee ~30 MB of private memory for results that
are, in fact, a pure function of (dataset, columns, parameters) — thirty trainees
running the lab defaults built thirty identical copies.

So the ``*_for()`` helpers below are the pipeline's public entry points. They are
``cache_resource``-backed and keyed on those parameters, which means a cohort all
running the Lab defaults shares exactly one copy of each layer. Session state
keeps only which parameters the trainee chose (see ``data_loader.SS_*``).

Caches are bounded: trainees sweep ``eps``/``min_samples`` while exploring, and an
unbounded cache of 14 MB layers would fill the container. Entries also expire, so
an abandoned parameter set does not hold memory for the rest of the day.

Everything returned here is **read-only and shared**. The transforms already
respect that (``build_points`` and ``run_dbscan`` copy before writing), and
``tests/test_concurrency.py`` enforces it.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# Cache sizing. points_for varies only with the dataset + column choice, so one
# entry serves a whole cohort; the parameterised stages get a little more room.
_POINTS_MAX, _POINTS_TTL = 4, 3600
_DERIVED_MAX, _DERIVED_TTL = 6, 1800


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
def grid_aggregate(gdf, cell_m: float = 20000):
    """Aggregate points into occupied cells of exactly ``cell_m`` metres.

    Only cells containing at least one point are materialized. This avoids building a
    huge empty grid when a dataset includes far-apart records, while preserving the
    cell size selected by the user.
    """
    import geopandas as gpd
    from shapely.geometry import box

    gm = to_metric(gdf)
    xy = np.column_stack([gm.geometry.x, gm.geometry.y])
    if not len(xy):
        return gpd.GeoDataFrame({"n_points": []}, geometry=[], crs=gm.crs)

    # Anchor to a cell boundary and group directly by grid index. Unlike iterating
    # over every coordinate between the bounds, this remains compact for sparse or
    # globally spread records and never needs to silently enlarge the requested cell.
    xmin = np.floor(xy[:, 0].min() / cell_m) * cell_m
    ymin = np.floor(xy[:, 1].min() / cell_m) * cell_m
    cell_ids = np.floor((xy - [xmin, ymin]) / cell_m).astype(np.int64)
    occupied, counts = np.unique(cell_ids, axis=0, return_counts=True)
    cells = [
        box(xmin + ix * cell_m, ymin + iy * cell_m,
            xmin + (ix + 1) * cell_m, ymin + (iy + 1) * cell_m)
        for ix, iy in occupied
    ]
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


PH_LAND_FILE = Path(__file__).resolve().parent.parent / "data" / "ph_land.geojson"


@st.cache_resource(show_spinner="Loading Philippines land boundary…")
def ph_land():
    """Philippine land polygon: Natural Earth land clipped to the PH window.

    Precomputed and vendored as data/ph_land.geojson (~11 KB). It was built by
    intersecting global `naturalearth.land` with the PH bounding box, buffering
    ~15 km so the coarse 110m coastline does not drop legitimate coastal points,
    and simplifying at 0.01° — ample for the `within()` mask this feeds.

    Doing it at build time rather than on first use removes a multi-megabyte
    download from the user's session, which on a cold free-tier container was
    both the slowest step on this page and the one most likely to fail.
    Falls back to the plain bounding box if the file is missing."""
    from shapely.geometry import box

    ph_box = box(*PH_BBOX)
    try:
        import geopandas as gpd

        geom = gpd.read_file(PH_LAND_FILE).geometry.iloc[0]
        if geom is not None and not geom.is_empty:
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


# ---------------------------------------------------------------------------
# Shared pipeline entry points
# ---------------------------------------------------------------------------
# The pages call these rather than the raw transforms above. Each is a pure
# function of its arguments, so identical parameters resolve to one shared layer
# no matter how many sessions ask for it. See the module docstring.

@st.cache_resource(show_spinner="Validating coordinates and building points…",
                   max_entries=_POINTS_MAX, ttl=_POINTS_TTL)
def points_for(source_key: str, lon_col: str, lat_col: str,
               text_col: str | None):
    """Lab 1: validated WGS84 points. Returns ``(gdf, report)`` — read-only."""
    from . import data_loader as dl

    df = dl.dataset(source_key)
    if df is None:
        return None, {}
    return build_points(df, lon_col, lat_col, text_col)


@st.cache_resource(show_spinner="Running DBSCAN…",
                   max_entries=_DERIVED_MAX, ttl=_DERIVED_TTL)
def clusters_for(source_key: str, lon_col: str, lat_col: str,
                 text_col: str | None, eps_m: float, min_samples: int):
    """Lab 2: DBSCAN labels. Returns ``(gdf, info)`` — read-only."""
    gdf, _ = points_for(source_key, lon_col, lat_col, text_col)
    if gdf is None:
        return None, {}
    return run_dbscan(gdf, eps_m=eps_m, min_samples=min_samples)


@st.cache_resource(show_spinner="Aggregating to a grid…",
                   max_entries=_DERIVED_MAX, ttl=_DERIVED_TTL)
def grid_for(source_key: str, lon_col: str, lat_col: str, text_col: str | None,
             cell_m: float):
    """Lab 3a: grid counts over the validated points — read-only."""
    gdf, _ = points_for(source_key, lon_col, lat_col, text_col)
    if gdf is None:
        return None
    return grid_aggregate(gdf, cell_m=cell_m)


@st.cache_resource(show_spinner="Computing cluster centroids…",
                   max_entries=_DERIVED_MAX, ttl=_DERIVED_TTL)
def centroids_for(source_key: str, lon_col: str, lat_col: str,
                  text_col: str | None, eps_m: float, min_samples: int,
                  exclude_noise: bool):
    """Lab 3b: one representative point per cluster — read-only."""
    clustered, _ = clusters_for(source_key, lon_col, lat_col, text_col,
                                eps_m, min_samples)
    if clustered is None:
        return None
    return cluster_centroids(clustered, exclude_noise=exclude_noise)


@st.cache_resource(show_spinner="Clipping to Philippine land…",
                   max_entries=_DERIVED_MAX, ttl=_DERIVED_TTL)
def clipped_for(source_key: str, lon_col: str, lat_col: str,
                text_col: str | None, eps_m: float | None, min_samples: int | None):
    """Lab 4: land-clipped layer. Returns ``(gdf, info)`` — read-only.

    ``eps_m``/``min_samples`` may be ``None``, meaning the trainee reached this
    page without running DBSCAN; the raw validated points get clipped instead."""
    if eps_m is None:
        src, _ = points_for(source_key, lon_col, lat_col, text_col)
    else:
        src, _ = clusters_for(source_key, lon_col, lat_col, text_col,
                              eps_m, min_samples)
    if src is None:
        return None, {}
    return clip_to_ph(src)


@st.cache_resource(show_spinner="Summarizing text per cluster…",
                   max_entries=_DERIVED_MAX, ttl=_DERIVED_TTL)
def cluster_text_for(source_key: str, lon_col: str, lat_col: str, text_col: str,
                     eps_m: float, min_samples: int, top_terms: int):
    """Lab 5: per-cluster TF-IDF profile. Aggregates only — read-only."""
    clustered, _ = clusters_for(source_key, lon_col, lat_col, text_col,
                                eps_m, min_samples)
    if clustered is None:
        return pd.DataFrame()
    return per_cluster_nlp(clustered, text_col, top_terms=top_terms)
