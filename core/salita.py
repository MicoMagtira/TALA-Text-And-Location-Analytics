"""Shared, cached Chapter 2 (Salita) analytics for pages p4-p9.

Why it exists: the Salita pages all start from the same few expensive results:
VADER per comment, the cleaned documents, aspect sentences, themes and the grid
plus Gi* cells. They live here (not in the page files, not in ``core/maps.py``,
which only builds map layers) so a page opened cold pays once and every other
page reuses the result.

Caching and concurrency rules:

* Every cached function is a ``st.cache_resource`` keyed on the dataset key and
  plain parameters only. Never a DataFrame, never the UI language, never session
  state objects. The dataset itself is fetched through ``data_loader.dataset``.
* Entries are shared by every session, so returned frames / arrays are
  **read-only by convention**: copy before modifying (arrays are also flagged
  non-writeable where cheap).
* Nothing here writes to ``st.session_state``; the only read is
  :func:`stopword_key`, which turns the stopword settings into a hashable key.
* Cache sizes are bounded (``max_entries`` / ``ttl``) for the ~1 GB container.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

_SHARED_MAX, _SHARED_TTL = 8, 1800

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
