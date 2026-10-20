"""Geospatial primitives for TALA: point validation, DBSCAN, the PH land polygon.

``core/places.py`` and ``core/salita.py`` build on these. Heavy geo deps
(geopandas/shapely/pyproj) import lazily, so the text-only paths never pay for
them. The grid, centroid, land-clip and per-cluster-text stages of the earlier
lab-style pipeline were dropped with the place-first redesign.

Concurrency model
-----------------
An 11,715-point GeoDataFrame is ~14 MB live, and the walkthrough produces two of
them (points, clusters) plus the generalized layer. Parking those in
``st.session_state`` cost every trainee ~30 MB of private memory for results that
are, in fact, a pure function of (dataset, columns, parameters) — thirty trainees
running the lab defaults built thirty identical copies.

So the ``*_for()`` helpers below are the public entry points. They are
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

from . import i18n

# Cache sizing. points_for varies only with the dataset + column choice, so one
# entry serves a whole cohort; the parameterised stages get a little more room.
_POINTS_MAX, _POINTS_TTL = 4, 3600
_DERIVED_MAX, _DERIVED_TTL = 6, 1800


# ---------------------------------------------------------------------------
# Ingest & CRS correctness
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


# ---------------------------------------------------------------------------
# DBSCAN
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
# PH land polygon
# ---------------------------------------------------------------------------
PH_BBOX = (116.0, 4.5, 127.0, 21.5)  # lon/lat window around the Philippines


PH_LAND_FILE = Path(__file__).resolve().parent.parent / "data" / "ph_land.geojson"


@i18n.localized_spinner("spin.ph_land")
@st.cache_resource(show_spinner=False)
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


# ---------------------------------------------------------------------------
# Shared pipeline entry points
# ---------------------------------------------------------------------------
# The pages call these rather than the raw transforms above. Each is a pure
# function of its arguments, so identical parameters resolve to one shared layer
# no matter how many sessions ask for it. See the module docstring.

@i18n.localized_spinner("spin.points")
@st.cache_resource(show_spinner=False,
                   max_entries=_POINTS_MAX, ttl=_POINTS_TTL)
def points_for(source_key: str, lon_col: str, lat_col: str,
               text_col: str | None):
    """Validated WGS84 points. Returns ``(gdf, report)`` — read-only."""
    from . import data_loader as dl

    df = dl.dataset(source_key)
    if df is None:
        return None, {}
    return build_points(df, lon_col, lat_col, text_col)


@i18n.localized_spinner("spin.dbscan")
@st.cache_resource(show_spinner=False,
                   max_entries=_DERIVED_MAX, ttl=_DERIVED_TTL)
def clusters_for(source_key: str, lon_col: str, lat_col: str,
                 text_col: str | None, eps_m: float, min_samples: int):
    """DBSCAN labels. Returns ``(gdf, info)`` — read-only."""
    gdf, _ = points_for(source_key, lon_col, lat_col, text_col)
    if gdf is None:
        return None, {}
    return run_dbscan(gdf, eps_m=eps_m, min_samples=min_samples)
