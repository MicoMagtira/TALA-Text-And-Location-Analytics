"""pydeck map builders (replaces folium / streamlit-folium / branca).

Why pydeck: it ships with Streamlit's own chart stack, renders on the GPU in the
browser (so tens of thousands of points stay smooth), and ``st.pydeck_chart`` can
report clicks back to the server, which folium could not do cheaply.

House rules this module follows:

* ``pydeck`` is imported **inside** each function (never at module top level), so
  the text-only pages never pay for it.
* pydeck only ever sees **plain** DataFrames / dicts. :func:`to_frame` strips the
  geometry column down to ``lon``/``lat`` floats; shapely objects never reach it.
* Nothing here mutates its input. The GeoDataFrames come from shared
  ``cache_resource`` entries (see ``core/geo.py``), so one in-place edit would
  corrupt every other session's view.
* ``map_style=None`` in :func:`deck`, so Streamlit swaps in its theme-aware Carto
  basemap (light or dark) by itself.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

import html as _html

from . import viz

PH_FALLBACK = (12.8, 121.8, 5)  # lat, lon, zoom: the Philippines as a whole
NOISE_RGBA = (153, 153, 153, 120)
NOISE_RADIUS_PX = 2
CLUSTER_RADIUS_PX = 4
TIP_MAX = 90

# Layer ids matter: ``st.pydeck_chart(on_select=...)`` keys the selection by id.
CLUSTER_LAYER_ID = "clusters"


def view_for(lonlat_df):
    """Fit the camera to where the points actually are, falling back to the Philippines.

    ``lonlat_df`` needs ``lon`` and ``lat`` columns. The fit is deliberately
    robust: the centre is the median and the extent comes from the interquartile
    range. TALA's bundled data is dirty on purpose (about 30% of coordinates fall
    outside the Philippines, scattered worldwide), and a min/max or mean-based
    fit such as ``pdk.data_utils.compute_view`` zooms out to half the globe. The
    trainee can still pan out to see the stray points."""
    import numpy as np
    import pydeck as pdk

    lat, lon, zoom = PH_FALLBACK
    if lonlat_df is not None and len(lonlat_df):
        xs = lonlat_df["lon"].to_numpy(dtype=float)
        ys = lonlat_df["lat"].to_numpy(dtype=float)
        ok = np.isfinite(xs) & np.isfinite(ys)
        if ok.any():
            xs, ys = xs[ok], ys[ok]
            span = max(float(np.subtract(*np.percentile(xs, [75, 25]))),
                       1.3 * float(np.subtract(*np.percentile(ys, [75, 25]))))
            span = max(span * 3.5, 0.05)  # IQR covers half the points; widen to frame them
            # 256 * 2**zoom px span 360 degrees; aim for ~1100 px across the extent.
            zoom = float(np.clip(np.log2(1100 * 360 / (256 * span)), 3, 14))
            return pdk.ViewState(latitude=float(np.median(ys)),
                                 longitude=float(np.median(xs)), zoom=zoom)
    return pdk.ViewState(latitude=lat, longitude=lon, zoom=zoom)


def to_frame(gdf, extra_cols=(), tip=None, cap: int = 50_000) -> pd.DataFrame:
    """GeoDataFrame -> plain DataFrame for pydeck.

    Columns: ``lon``, ``lat`` (float), the requested ``extra_cols`` and, when
    ``tip`` is given, a ``tip`` string of at most 90 characters. ``tip`` is either
    a column name or a callable taking the (possibly sampled) source frame and
    returning an iterable of strings.

    Samples down to ``cap`` rows with a stable ``random_state=1`` so a rerun does
    not make the map shimmer. The result carries ``attrs["sampled"]`` (bool) and
    ``attrs["total"]`` (rows before sampling) so the page can caption it.
    Never mutates ``gdf``."""
    total = 0 if gdf is None else len(gdf)
    if not total:
        cols = ["lon", "lat", *extra_cols] + (["tip"] if tip is not None else [])
        out = pd.DataFrame({c: [] for c in cols})
        out.attrs.update(sampled=False, total=0)
        return out

    src = gdf
    sampled = total > cap
    if sampled:
        src = gdf.sample(cap, random_state=1)

    out = pd.DataFrame({
        "lon": src.geometry.x.to_numpy(dtype=float),
        "lat": src.geometry.y.to_numpy(dtype=float),
    })
    for c in extra_cols:
        out[c] = src[c].to_numpy()
    if tip is not None:
        raw = tip(src) if callable(tip) else src[tip]
        out["tip"] = [str(s)[:TIP_MAX] for s in raw]
    out.attrs.update(sampled=sampled, total=total)
    return out


def bounds_frame(gdf) -> pd.DataFrame:
    """Two-row ``lon``/``lat`` frame (opposite bbox corners) so :func:`view_for`
    can fit polygon layers such as the grid cells."""
    if gdf is None or not len(gdf):
        return pd.DataFrame({"lon": [], "lat": []})
    minx, miny, maxx, maxy = (float(v) for v in gdf.total_bounds)
    return pd.DataFrame({"lon": [minx, maxx], "lat": [miny, maxy]})


def points_layer(df, color=(53, 64, 142, 180), radius_px: int = 3):
    """Plain points. ``df`` is a :func:`to_frame` result (``lon``/``lat``)."""
    import pydeck as pdk

    return pdk.Layer(
        "ScatterplotLayer", id="points", data=df, get_position="[lon, lat]",
        get_fill_color=list(color), get_radius=radius_px, radius_units="'pixels'",
        radius_min_pixels=1, pickable="tip" in df.columns,
    )


def cluster_frame(gdf, palette_hexes, cap: int = 50_000) -> pd.DataFrame:
    """The plain frame behind :func:`cluster_layer`: ``lon``, ``lat``,
    ``cluster_id``, ``color`` (RGBA list), ``radius`` (px) and ``tip``.

    Pages call this themselves when they also need the frame (camera fit,
    "sampled" caption); pydeck turns a layer's DataFrame into records, so it can
    no longer be read back from the layer."""
    df = to_frame(gdf, extra_cols=("cluster_id",), cap=cap)
    ids = (df["cluster_id"].astype(int).to_numpy() if len(df)
           else np.array([], dtype=int))
    df["color"] = [
        list(viz.hex_to_rgba(palette_hexes[i % len(palette_hexes)], 200))
        if i != -1 else list(NOISE_RGBA) for i in ids]
    df["radius"] = np.where(ids == -1, NOISE_RADIUS_PX, CLUSTER_RADIUS_PX)
    df["tip"] = ["Noise" if i == -1 else f"Cluster C{i}" for i in ids]
    return df


def cluster_layer(gdf, palette_hexes, cap: int = 50_000, frame=None):
    """Points coloured by ``cluster_id``; noise (-1) is grey and smaller.

    Keeps ``cluster_id`` per point so a click (``on_select``) can tell the page
    which cluster was picked. Pass ``frame`` (from :func:`cluster_frame`) to
    reuse one already built."""
    import pydeck as pdk

    df = frame if frame is not None else cluster_frame(gdf, palette_hexes, cap)
    return pdk.Layer(
        "ScatterplotLayer", id=CLUSTER_LAYER_ID, data=df,
        get_position="[lon, lat]", get_fill_color="color", get_radius="radius",
        radius_units="'pixels'", pickable=True, auto_highlight=True,
    )


def grid_layer(cells_gdf, seq_hexes):
    """Occupied grid cells filled by ``n_points`` (light to dark along ``seq_hexes``).

    Only cells the server already computed are drawn, so the payload stays small
    however fine the grid is. Tooltip field is ``{properties.n_points}``."""
    import pydeck as pdk

    n = (cells_gdf["n_points"].to_numpy(dtype=float) if len(cells_gdf)
         else np.array([]))
    vmax = float(n.max()) if len(n) else 1.0
    stops = max(len(seq_hexes) - 1, 1)
    feats = (json.loads(cells_gdf.to_json()) if len(cells_gdf)
             else {"type": "FeatureCollection", "features": []})
    for f, v in zip(feats["features"], n):
        idx = min(int(round(v / vmax * stops)), stops)
        f["properties"] = {"n_points": int(v),
                           "fill": viz.hex_to_rgba(seq_hexes[idx], 190)}
    return pdk.Layer(
        "GeoJsonLayer", id="grid", data=feats,
        get_fill_color="properties.fill", get_line_color=[85, 85, 85, 90],
        line_width_min_pixels=1, stroked=True, filled=True, pickable=True,
        auto_highlight=True,
    )


def centroid_layer(cent_gdf, color_by=None):
    """One disc per cluster, radius scaled by ``n_points`` (metres).

    ``cent_gdf`` is either a GeoDataFrame of points with ``n_points`` or a ready
    :func:`to_frame` result (``lon``/``lat``/``n_points`` plus any ``tip``). When
    ``color_by`` (``{sentiment: "#hex"}``) is given, discs are coloured from the
    frame's ``sentiment`` column; others fall back to navy."""
    import pydeck as pdk

    if isinstance(cent_gdf, pd.DataFrame) and "lon" in cent_gdf.columns:
        df = cent_gdf.copy()
    else:
        cols = [c for c in ("cluster_id", "n_points", "sentiment")
                if c in cent_gdf.columns]
        df = to_frame(cent_gdf, extra_cols=cols)
    if "tip" not in df.columns and "cluster_id" in df.columns:
        df["tip"] = [f"Cluster {int(c)} - {int(n)} pts"
                     for c, n in zip(df["cluster_id"], df["n_points"])]
    npts = df["n_points"].to_numpy(dtype=float)
    vmax = float(npts.max()) if len(npts) else 1.0
    df["radius_m"] = 4000 + 20000 * np.sqrt(npts / vmax) if len(npts) else []
    mapping = color_by or {}
    sent = df["sentiment"] if "sentiment" in df.columns else [None] * len(df)
    df["color"] = [list(viz.hex_to_rgba(mapping.get(s, viz.NU_NAVY), 165))
                   for s in sent]
    return pdk.Layer(
        "ScatterplotLayer", id="centroids", data=df, get_position="[lon, lat]",
        get_fill_color="color", get_radius="radius_m", radius_units="'meters'",
        radius_min_pixels=4, stroked=True, get_line_color=[53, 64, 142, 230],
        line_width_min_pixels=1, pickable=True, auto_highlight=True,
    )


def land_layer():
    """Faint Philippine land polygon with an outline (context for CRS/clip lessons)."""
    import pydeck as pdk
    from shapely.geometry import mapping

    from . import geo

    feats = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {}, "geometry": mapping(geo.ph_land())}]}
    return pdk.Layer(
        "GeoJsonLayer", id="land", data=feats, stroked=True, filled=True,
        get_fill_color=[53, 64, 142, 18], get_line_color=[53, 64, 142, 140],
        line_width_min_pixels=1, pickable=False,
    )


def deck(layers, view, tooltip_html=None):
    """Assemble the ``pdk.Deck``. ``map_style=None`` keeps Streamlit's themed basemap."""
    import pydeck as pdk

    tooltip = None
    if tooltip_html:
        tooltip = {"html": tooltip_html,
                   "style": {"backgroundColor": "#35408E", "color": "white",
                             "fontSize": "12px", "maxWidth": "320px"}}
    return pdk.Deck(layers=list(layers), initial_view_state=view,
                    map_style=None, tooltip=tooltip)


# ===========================================================================
# Chapter 2 (Salita): bubble / hotspot layers and the shared, cached analytics
# ===========================================================================
# Bubble and hotspot layers for the Chapter 2 pages. The cached analytics they
# draw live in core/salita.py.

HOT_ALPHA = {99: 235, 95: 190, 90: 140}     # stronger evidence = more opaque


def _rgba(hexcolor: str, alpha: int) -> list[int]:
    return list(viz.hex_to_rgba(hexcolor, alpha))


def bubble_frame(df, value_col: str, hexes, vmin=None, vmax=None, size_col: str = "n",
                 ok_col: str | None = "ok", tip_col: str = "tip",
                 max_px: float = 34.0, min_px: float = 6.0) -> pd.DataFrame:
    """Plain frame for :func:`bubble_layer`: ``lon, lat, radius, color, tip``.

    Radius grows with the square root of ``size_col`` (area is proportional to
    count); colour runs along ``hexes`` from ``vmin`` to ``vmax`` of ``value_col``.
    Rows where ``ok_col`` is False are drawn grey. Never mutates ``df``."""
    out = pd.DataFrame({"lon": df["lon"].to_numpy(float), "lat": df["lat"].to_numpy(float)})
    n = df[size_col].to_numpy(float)
    nmax = max(float(np.nanmax(n)) if len(n) else 1.0, 1.0)
    out["radius"] = min_px + (max_px - min_px) * np.sqrt(np.clip(n, 0, None) / nmax)
    v = df[value_col].to_numpy(float)
    ok = np.ones(len(df), bool) if ok_col is None else df[ok_col].to_numpy(bool)
    good = v[ok & np.isfinite(v)]
    lo = float(good.min()) if vmin is None and len(good) else (vmin or 0.0)
    hi = float(good.max()) if vmax is None and len(good) else (vmax or 1.0)
    stops = len(hexes) - 1
    cols = []
    for val, is_ok in zip(v, ok):
        if not is_ok or not np.isfinite(val):
            cols.append(list(NOISE_RGBA))
        else:
            t = 0.0 if hi <= lo else (val - lo) / (hi - lo)
            cols.append(_rgba(hexes[int(round(min(max(t, 0.0), 1.0) * stops))], 215))
    out["color"] = cols
    out["tip"] = df[tip_col].to_numpy(object) if tip_col in df.columns else ""
    return out


def bubble_layer(frame):
    """One disc per place (pixels). ``frame`` comes from :func:`bubble_frame`."""
    import pydeck as pdk

    return pdk.Layer(
        "ScatterplotLayer", id="bubbles", data=frame, get_position="[lon, lat]",
        get_fill_color="color", get_radius="radius", radius_units="'pixels'",
        stroked=True, get_line_color=[255, 255, 255, 220], line_width_min_pixels=1,
        pickable=True, auto_highlight=True,
    )


def hotspot_layer(cells_gdf, hot_hex: str, cold_hex: str, ns_hex: str = "#999999"):
    """Grid cells coloured by Gi* class: warm = hot, cool = cold, grey = not significant.

    Opacity encodes the confidence level (99 % strongest). ``cells_gdf`` needs
    ``hot_class`` and optionally ``tip`` (HTML). Tooltip field: ``{properties.tip}``."""
    import pydeck as pdk

    n = len(cells_gdf)
    feats = (json.loads(cells_gdf.to_json()) if n
             else {"type": "FeatureCollection", "features": []})
    for f in feats["features"]:
        cls = f["properties"].get("hot_class", "ns")
        if cls == "ns":
            fill = _rgba(ns_hex, 55)
        else:
            kind, level = cls.split("_")
            fill = _rgba(hot_hex if kind == "hot" else cold_hex, HOT_ALPHA[int(level)])
        f["properties"]["fill"] = fill
    return pdk.Layer(
        "GeoJsonLayer", id="hotspots", data=feats, get_fill_color="properties.fill",
        get_line_color=[255, 255, 255, 60], line_width_min_pixels=1,
        stroked=True, filled=True, pickable=True, auto_highlight=True,
    )


def gradient_legend_html(hexes, lo_label: str, hi_label: str, caption: str = "") -> str:
    """A small gradient bar with its end labels, for bubble maps."""
    cap = f"<div style='font-size:12px;opacity:.8'>{_html.escape(caption)}</div>" if caption else ""
    return (f"{cap}<div style='display:flex;align-items:center;gap:8px;max-width:360px'>"
            f"<span style='font-size:12px'>{_html.escape(lo_label)}</span>"
            f"<div style='flex:1;height:10px;border-radius:5px;"
            f"background:linear-gradient(to right,{','.join(hexes)})'></div>"
            f"<span style='font-size:12px'>{_html.escape(hi_label)}</span></div>")


def hotspot_legend_html(hot_hex: str, cold_hex: str, labels: dict) -> str:
    """Legend chips for the hot/cold classes. ``labels`` maps ``hot``, ``cold``,
    ``ns`` and ``level`` (a template such as "{level}%") to localized text."""
    def chip(hexcolor, alpha, text):
        r, g, b = (int(hexcolor[i:i + 2], 16) for i in (1, 3, 5))
        return (f"<span style='display:inline-flex;align-items:center;gap:5px;margin:2px 12px 2px 0;"
                f"font-size:12px'><i style='display:inline-block;width:14px;height:14px;"
                f"border-radius:3px;background:rgba({r},{g},{b},{alpha / 255:.2f});"
                f"border:1px solid rgba(128,128,128,.5)'></i>{_html.escape(text)}</span>")

    rows = []
    for kind, hexcolor in (("hot", hot_hex), ("cold", cold_hex)):
        chips = "".join(chip(hexcolor, HOT_ALPHA[lv], labels["level"].format(level=lv))
                        for lv in (99, 95, 90))
        rows.append(f"<div><b style='font-size:12px;margin-right:8px'>"
                    f"{_html.escape(labels[kind])}</b>{chips}</div>")
    rows.append(f"<div>{chip('#999999', 55, labels['ns'])}</div>")
    return "".join(rows)
