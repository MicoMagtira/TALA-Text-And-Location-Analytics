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
# The Chapter 2 pages (p4-p9) all start from the same few expensive results:
# VADER per comment, the cleaned documents, aspect sentences, themes and the
# grid + Gi* cells. They live here, keyed on the dataset key and parameters
# only (never language, never a DataFrame in session state), so a page opened
# cold pays once and every other page reuses it. Returned frames are shared and
# read-only: copy before modifying.
import html as _html  # noqa: E402

import streamlit as st  # noqa: E402

HOT_ALPHA = {99: 235, 95: 190, 90: 140}     # stronger evidence = more opaque
_SHARED_MAX, _SHARED_TTL = 8, 1800


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


# ---------------------------------------------------------------------------
# Shared analytics (cached on dataset key + parameters)
# ---------------------------------------------------------------------------
def _dataset(source_key: str):
    from . import data_loader as dl

    return dl.dataset(source_key)


def stopword_key() -> tuple[str, bool]:
    """``(custom stopword text, use Filipino list)``: the part of the stopword
    settings that changes the cleaned documents, as a hashable cache key."""
    from . import ui

    return (str(st.session_state.get(ui.SS_CUSTOM_SW, "")),
            bool(st.session_state.get(ui.SS_USE_TL, True)))


@st.cache_resource(show_spinner=False, max_entries=_SHARED_MAX, ttl=_SHARED_TTL)
def sentiment_for(source_key: str, text_col: str) -> np.ndarray:
    """VADER compound per row, computed once per dataset and reused by p5/p6/p8/p9."""
    from . import compare

    df = _dataset(source_key)
    out = compare.vader_compound(df[text_col].fillna("").astype(str))
    out.flags.writeable = False
    return out


@st.cache_resource(show_spinner=False, max_entries=_SHARED_MAX, ttl=_SHARED_TTL)
def place_tokens(source_key: str, text_col: str) -> frozenset:
    """Words that appear in region, province and city names (and their aliases), plus
    the names the geoparser actually found in this dataset (so towns count too).

    Used to hide toponyms from keywords and themes: they separate places
    trivially (a Davao comment says "Davao") and tell us nothing new."""
    from . import places, preprocess

    gz = places.load_gazetteer()
    gz = gz[gz["kind"].isin(["region", "province", "city"])]
    eng = preprocess.english_stopwords()
    forms = []
    for name, aliases in zip(gz["name"], gz["aliases"]):
        forms += [name] + [a for a in str(aliases).split("|") if a]
    parsed = places.parsed_for(source_key, text_col)
    if parsed is not None:
        forms += parsed.loc[parsed["status"] == "found", "place"].unique().tolist()
    toks = set()
    for form in forms:
        toks |= {t for t in preprocess.clean_text(form).split() if len(t) >= 3}
    return frozenset(toks - set(eng))


@st.cache_resource(show_spinner=False, max_entries=_SHARED_MAX, ttl=_SHARED_TTL)
def docs_for(source_key: str, text_col: str, custom_sw: str, use_tl: bool,
             drop_places: bool) -> list[str]:
    """Cleaned, stopword-filtered documents (one per row; blanks stay blank so row
    indices line up with the dataset). Optionally without place names."""
    from . import preprocess

    df = _dataset(source_key)
    sw = preprocess.build_stopwords(custom_sw, use_tl)
    if drop_places:
        sw = sw | set(place_tokens(source_key, text_col))
    return preprocess.clean_corpus(df[text_col].fillna("").astype(str), sw)


@st.cache_resource(show_spinner=False, max_entries=_SHARED_MAX, ttl=_SHARED_TTL)
def logodds_for(source_key: str, text_col: str, custom_sw: str, use_tl: bool,
                lon_col: str, lat_col: str, km: float, mode: str, unit: str,
                eps_m: float, min_samples: int, place_a: str, place_b: str = ""):
    """Weighted log-odds of ``place_a`` against ``place_b`` (empty = every other
    place). The background prior is every assigned comment. Shared by p4 and the
    p9 report cards, so a card costs nothing once p4 has shown the same place."""
    from . import compare, places

    labels = places.assign_place_for(source_key, lon_col, lat_col, text_col, km, mode,
                                     unit, eps_m, min_samples).to_numpy(object)
    docs = docs_for(source_key, text_col, custom_sw, use_tl, False)
    assigned = labels != ""
    a = [d for d, lab in zip(docs, labels) if lab == place_a]
    if place_b:
        b = [d for d, lab in zip(docs, labels) if lab == place_b]
    else:
        b = [d for d, lab, ok in zip(docs, labels, assigned) if ok and lab != place_a]
    bg = [d for d, ok in zip(docs, assigned) if ok]
    return compare.log_odds(a, b, prior=bg, min_count=1)


def drop_place_terms(table: pd.DataFrame, source_key: str, text_col: str) -> pd.DataFrame:
    """Remove log-odds rows where any word of the term is a place-name word."""
    pt = place_tokens(source_key, text_col)
    keep = [not any(w in pt for w in t.split()) for t in table["term"]]
    return table[keep]


@st.cache_resource(show_spinner=False, max_entries=_SHARED_MAX, ttl=_SHARED_TTL)
def aspect_rows_for(source_key: str, text_col: str) -> pd.DataFrame:
    """One row per (sentence mentioning an aspect, aspect): ``row, aspect, c``.

    ``row`` is the comment's position in the dataset and ``c`` the VADER compound of
    that sentence. Built once per dataset; only sentences that match some aspect are
    scored, which keeps it to about a second for the bundled 12,000 comments."""
    from . import compare

    df = _dataset(source_key)
    rows, sents = [], []
    for i, t in enumerate(df[text_col].fillna("").astype(str)):
        for s in compare._SENT_SPLIT.split(t):
            if s.strip():
                rows.append(i)
                sents.append(s)
    lex = compare.load_aspects()
    hits = {a: np.fromiter((bool(rx.search(s)) for s in sents), bool, len(sents))
            for a, rx in ((a, compare._aspect_regex(t)) for a, t in lex.items())}
    any_hit = np.zeros(len(sents), bool)
    for m in hits.values():
        any_hit |= m
    idx = np.flatnonzero(any_hit)
    comp = np.full(len(sents), np.nan)
    comp[idx] = compare.vader_compound([sents[i] for i in idx])
    rows = np.asarray(rows)
    parts = [pd.DataFrame({"row": rows[m], "aspect": a, "c": comp[m]}) for a, m in hits.items()]
    return pd.concat(parts, ignore_index=True)


def aspect_by_place(aspect_rows: pd.DataFrame, labels, min_n: int = 1) -> pd.DataFrame:
    """Aggregate :func:`aspect_rows_for` to ``place, aspect, n, pct_neg`` (n = sentences)."""
    from .nlp import VADER_THRESHOLD

    lab = np.asarray(labels, dtype=object)[aspect_rows["row"].to_numpy()]
    df = pd.DataFrame({"place": lab, "aspect": aspect_rows["aspect"].to_numpy(),
                       "neg": aspect_rows["c"].to_numpy() <= -VADER_THRESHOLD})
    df = df[df["place"] != ""]
    g = df.groupby(["place", "aspect"]).agg(n=("neg", "size"), neg=("neg", "sum")).reset_index()
    g["pct_neg"] = 100 * g["neg"] / g["n"]
    return g[g["n"] >= min_n].drop(columns="neg").reset_index(drop=True)


def aspect_row_flags(aspect_rows: pd.DataFrame, aspect: str, n_rows: int):
    """For one aspect: ``(mentions, negative)`` boolean arrays over dataset rows.

    A comment counts as negative about the aspect when the mean compound of its
    matching sentences is at or below VADER's -0.05 cut-off."""
    from .nlp import VADER_THRESHOLD

    sub = aspect_rows[aspect_rows["aspect"] == aspect]
    g = sub.groupby("row")["c"].mean()
    has = np.zeros(n_rows, bool)
    neg = np.zeros(n_rows, bool)
    has[g.index.to_numpy()] = True
    neg[g.index.to_numpy()] = g.to_numpy() <= -VADER_THRESHOLD
    return has, neg


def theme_label(terms, aspect_names: dict | None = None) -> str:
    """A short auto-label for a theme from its top terms.

    Scores each aspect (waiting, staff, ...) by rank-weighted matches among the top
    terms and names the theme after the best one; falls back to the first two terms.
    ``aspect_names`` maps aspect ids to localized names."""
    from . import compare

    terms = list(terms)
    names = aspect_names or {}
    best, best_score = None, 0
    for aspect, lex in compare.load_aspects().items():
        rx = compare._aspect_regex(lex)
        score = sum(len(terms) - i for i, t in enumerate(terms) if rx.search(t))
        if score > best_score:
            best, best_score = aspect, score
    if best:
        return names.get(best, best)
    return " / ".join(terms[:2]) if terms else "?"


def theme_names(top_terms: dict, aspect_names: dict | None = None) -> list[str]:
    """Labels for every theme, made unique by adding the strongest term to duplicates."""
    names = [theme_label(top_terms[i], aspect_names) for i in range(len(top_terms))]
    for name in set(names):
        idx = [i for i, n in enumerate(names) if n == name]
        if len(idx) > 1:
            for i in idx:
                names[i] = f"{name} · {top_terms[i][0]}"
    return names


@st.cache_resource(show_spinner=False, max_entries=_SHARED_MAX, ttl=_SHARED_TTL)
def themes_for(source_key: str, text_col: str, custom_sw: str, use_tl: bool,
               drop_places: bool, k: int):
    """K-Means themes over the cleaned documents: a dict with ``labels`` (one per row,
    -1 for blanks), ``top_terms``, ``sizes`` and ``silhouette``; ``None`` if too little
    text. Reuses ``core.nlp.tfidf_kmeans`` through ``compare.theme_labels``."""
    from . import compare

    docs = docs_for(source_key, text_col, custom_sw, use_tl, drop_places)
    labels, res = compare.theme_labels(docs, k=k)
    if labels is None:
        return None
    sil = compare.silhouette(docs, labels)
    labels.flags.writeable = False
    return {"labels": labels, "top_terms": res["top_terms"], "sizes": res["sizes"],
            "silhouette": sil}


def grid_cells(lon, lat, neg, cell_m: float):
    """Bin points into occupied square cells of ``cell_m`` metres (UTM).

    Returns ``(cells, inverse)``: ``cells`` is a GeoDataFrame (EPSG:4326) with
    ``n_points, n_neg, share_neg`` plus ``cx, cy`` (cell centre in metres, for Gi*), and
    ``inverse`` maps every input point to its row in ``cells``. Occupied cells only."""
    import geopandas as gpd
    import shapely

    from . import geo

    lon = np.asarray(lon, float)
    lat = np.asarray(lat, float)
    neg = np.asarray(neg, bool)
    pts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(lon, lat), crs="EPSG:4326")
    gm = geo.to_metric(pts)
    x = gm.geometry.x.to_numpy()
    y = gm.geometry.y.to_numpy()
    ij = np.floor(np.column_stack([x, y]) / cell_m).astype(np.int64)
    uniq, inv = np.unique(ij, axis=0, return_inverse=True)
    inv = np.asarray(inv).reshape(-1)
    n = np.bincount(inv, minlength=len(uniq))
    nn = np.bincount(inv, weights=neg.astype(float), minlength=len(uniq))
    x0, y0 = uniq[:, 0] * cell_m, uniq[:, 1] * cell_m
    cells = gpd.GeoDataFrame(
        {"n_points": n, "n_neg": nn.astype(int), "share_neg": nn / n,
         "cx": x0 + cell_m / 2, "cy": y0 + cell_m / 2},
        geometry=shapely.box(x0, y0, x0 + cell_m, y0 + cell_m), crs=gm.crs).to_crs(epsg=4326)
    return cells, inv


@st.cache_resource(show_spinner=False, max_entries=_SHARED_MAX, ttl=_SHARED_TTL)
def hotspots_for(source_key: str, text_col: str, lon_col: str, lat_col: str, km: float,
                 mode: str, cell_km: float, radius_km: float, min_n: int, aspect: str = ""):
    """Getis-Ord Gi* hotspots of the share of negative comments on a square grid.

    Cells with fewer than ``min_n`` comments are dropped *before* Gi* (a share from
    three comments is noise). With ``aspect`` set, only comments that mention it count
    and "negative" refers to that aspect. Returns ``{"cells", "row_class", "n_used"}``:
    ``cells`` has ``n_points, share_neg, z, hot_class``; ``row_class`` gives each
    dataset row its cell's class (``""`` when the row is not in a kept cell)."""
    from . import compare, places
    from .nlp import VADER_THRESHOLD

    located = places.locate_for(source_key, lon_col, lat_col, text_col, km, mode)
    n_rows = len(located)
    comp = sentiment_for(source_key, text_col)
    neg = comp <= -VADER_THRESHOLD
    use = located["lon"].notna().to_numpy()
    if aspect:
        has, aneg = aspect_row_flags(aspect_rows_for(source_key, text_col), aspect, n_rows)
        use &= has
        neg = aneg
    empty = {"cells": None, "row_class": np.full(n_rows, "", dtype=object),
             "n_used": int(use.sum())}
    if use.sum() < 2:
        return empty
    rows = np.flatnonzero(use)
    cells, inv = grid_cells(located["lon"].to_numpy()[rows], located["lat"].to_numpy()[rows],
                            neg[rows], cell_km * 1000.0)
    keep = (cells["n_points"] >= min_n).to_numpy()
    if keep.sum() < 2:
        empty["cells"] = cells[keep].assign(z=0.0, hot_class="ns")
        return empty
    kept = cells[keep].copy()
    z = compare.gi_star(kept["share_neg"].to_numpy(), kept[["cx", "cy"]].to_numpy(),
                        radius_km * 1000.0)
    kept["z"] = z
    kept["hot_class"] = compare.hotspot_class(z)
    cls_all = np.full(len(cells), "", dtype=object)
    cls_all[keep] = kept["hot_class"].to_numpy()
    row_class = np.full(n_rows, "", dtype=object)
    row_class[rows] = cls_all[inv]
    return {"cells": kept.reset_index(drop=True), "row_class": row_class,
            "n_used": int(use.sum())}
