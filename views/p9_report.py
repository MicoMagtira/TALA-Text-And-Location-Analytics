"""Step 9 (p9_report): place report.

A privacy-safe, generalized map; one report card per place that pulls Chapter 2 together
(distinctive words, sentiment, worst aspect, main theme, hotspot flag); and exports.
Everything shown or exported is an aggregate: no comment text, no individual points.
"""
import html
import json

import numpy as np
import pandas as pd
import streamlit as st

from core import audio, compare, i18n, maps, places, tracks, ui, viz
from core import data_loader as dl

PAGE = "p9_report"
T = ui._t
ASPECTS = ["waiting", "staff", "cost", "medicine", "facilities", "access"]
ASPECT_DEFAULT = {"waiting": "Waiting", "staff": "Staff", "cost": "Cost",
                  "medicine": "Medicine", "facilities": "Facilities", "access": "Access"}
HOT_SHARE_FLAG = 0.30      # a place is flagged when this share of its comments sit in hot cells
MIN_ASPECT_N = 15
THEME_K = 4

dl.ensure_loaded()
ui.page_header(PAGE, "what")
if i18n.t(f"{PAGE}.blurb") == f"{PAGE}.blurb":
    st.markdown(T(f"{PAGE}.blurb", "One privacy-safe summary per place, ready to share."))
ui.auto_ran(PAGE)
ui.learn_page(
    PAGE,
    code=(
        "import numpy as np, pandas as pd\n\n"
        "# 1. bin points into square cells (metres), 2. keep cells with >= k comments\n"
        "cell = 20_000\n"
        "ij = np.floor(xy / cell).astype(int)\n"
        "cells, inv, n = np.unique(ij, axis=0, return_inverse=True, return_counts=True)\n"
        "safe = n >= 10                        # k-anonymity-style suppression\n"
        "share_neg = np.bincount(inv, weights=neg) / n\n\n"
        "# 3. export aggregates only\n"
        "gdf = gpd.GeoDataFrame({'n_points': n[safe], 'pct_negative': 100*share_neg[safe]},\n"
        "                       geometry=boxes[safe], crs='EPSG:4326')\n"
        "gdf.to_file('tala_generalized.geojson', driver='GeoJSON')"
    ),
)

if not places.has_geo():
    ui.locked(T("ch2.locked", "This step needs a text column and longitude/latitude columns."),
              "p1_data", T("ch2.locked_link", "Go to Data"))

p = places.params()
labels = places.active_places()
located = places.active_located()
if labels is None or not (labels != "").any():
    ui.info(T("ch2.no_places", "No comments could be assigned to a place."))
    ui.page_done(PAGE)
    ui.track_footer(PAGE)
    st.stop()

cat = viz.categorical(ui.palette(), 2)
seq = viz.sequential_hexes(ui.seq_palette(), 6)
sw_custom, sw_tl = maps.stopword_key()
asp_names = {a: T(f"asp.{a}", n) for a, n in ASPECT_DEFAULT.items()}
NEG = -0.05
lab_arr = labels.to_numpy(object)
n_rows = len(labels)
comp = maps.sentiment_for(p["source_key"], p["text_col"])
neg_row = comp <= NEG
has_xy = located["lon"].notna().to_numpy()


# ---------------------------------------------------------------------------
# 1. Generalized map + GeoJSON + metadata
# ---------------------------------------------------------------------------
@st.fragment
def _generalize():
    grid_label = T("p9_report.grid", "Grid cells")
    cent_label = T("p9_report.centroids", "Place centroids")
    method = st.radio(T("p9_report.method", "Generalize the map as"), [grid_label, cent_label],
                      horizontal=True, key="p9_method")
    c1, c2 = st.columns(2)
    # k: cells or places with fewer comments than this are hidden, so no marker can
    # point at a handful of people.
    k_min = c2.slider(T("p9_report.k_min", "Hide groups smaller than"), 3, 50, 10, 1, key="p9_k")
    import geopandas as gpd

    if method == grid_label:
        cell_km = c1.slider(T("p9_report.cell", "Grid cell size (km)"), 5, 100, 20, 5, key="p9_cell")
        with audio.result(tracks.SIGNATURE[PAGE], (p["source_key"], p["mode"], p["km"], cell_km, k_min, "g")):
            rows = np.flatnonzero(has_xy)
            cells, _ = maps.grid_cells(located["lon"].to_numpy()[rows], located["lat"].to_numpy()[rows],
                                       neg_row[rows], cell_km * 1000.0)
        cells = cells[cells["n_points"] >= k_min]
        gen = gpd.GeoDataFrame(
            {"n_points": cells["n_points"].to_numpy(),
             "pct_negative": (100 * cells["share_neg"]).round(1).to_numpy()},
            geometry=cells.geometry.to_numpy(), crs="EPSG:4326")
        generalization = ["grid", cell_km * 1000]
        if len(gen):
            vmax = int(gen["n_points"].max())
            hexes = viz.sequential_hexes(ui.seq_palette(), 6)
            tip = (f"{T('p9_report.tip_points', 'Comments')}: {{properties.n_points}}<br>"
                   f"{T('p9_report.tip_neg', '% negative')}: {{properties.pct_negative}}")
            st.pydeck_chart(maps.deck([maps.grid_layer(gen, hexes)],
                                      maps.view_for(maps.bounds_frame(gen)), tip),
                            height=480, width="stretch")
            st.markdown(maps.gradient_legend_html(
                hexes, f"{k_min}", f"{vmax:,}", T("p9_report.legend", "Comments per cell")),
                unsafe_allow_html=True)
    else:
        with audio.result(tracks.SIGNATURE[PAGE], (p["source_key"], p["mode"], p["km"], p["unit"], k_min, "c")):
            pts = places.place_points(located, labels, p["unit"])
            tab = compare.place_sentiment(comp, lab_arr, min_n=1)[["place", "pct_neg"]]
            pts = pts.merge(tab, on="place")
        pts = pts[pts["n"] >= k_min].reset_index(drop=True)
        gen = gpd.GeoDataFrame(
            {"place": pts["place"].to_numpy(), "n_points": pts["n"].to_numpy(),
             "pct_negative": pts["pct_neg"].round(1).to_numpy()},
            geometry=gpd.points_from_xy(pts["lon"], pts["lat"]), crs="EPSG:4326")
        generalization = ["centroids", True]
        if len(pts):
            frame = pd.DataFrame({"lon": pts["lon"], "lat": pts["lat"], "n_points": pts["n"],
                                  "tip": [f"<b>{html.escape(r.place)}</b><br>{r.n:,} "
                                          f"{T('p9_report.comments', 'comments')}, {r.pct_neg:.0f}% "
                                          f"{T('p9_report.negative', 'negative')}" for r in pts.itertuples()]})
            st.pydeck_chart(maps.deck([maps.centroid_layer(frame)], maps.view_for(frame), "{tip}"),
                            height=480, width="stretch")
    st.caption(T("p9_report.privacy",
                 ":material/lock: Only counts and percentages are shown or exported; every marker stands for at least {k} comments.",
                 k=k_min))
    if not len(gen):
        ui.info(T("p9_report.empty", "Nothing left after hiding small groups. Lower the minimum."))
        return

    # The export payload is deliberately NOT localized: worksheets and shared analyses
    # depend on identical field names whatever the UI language. Original contract kept
    # (app, crs, clip, n_features_exported, generalization, dbscan); new fields added.
    metadata = {
        "app": "TALA — Text And Location Analytics",
        "crs": "EPSG:4326",
        "clip": {"clipped": True, "before": int(n_rows), "after": int(has_xy.sum()),
                 "removed": int(n_rows - has_xy.sum())},
        "n_features_exported": int(len(gen)),
        "generalization": generalization,
        "dbscan": {"eps_m": p["eps_m"], "min_samples": p["min_samples"]},
        "place_unit": p["unit"],
        "location_source": p["mode"],
        "text_vs_gps_km": p["km"],
        "min_group_size": int(k_min),
        "sentiment": {"method": "VADER", "negative_if_compound_at_most": NEG},
        "hotspot": dict(zip(("cell_km", "radius_km", "min_comments", "aspect"),
                            st.session_state.get("p8_params", (20, 50, 10, "")))),
        "theme_k": THEME_K,
    }
    d1, d2 = st.columns(2)
    d1.download_button(T("p9_report.dl_geojson", "Download GeoJSON"), gen.to_json(),
                       "tala_generalized.geojson", "application/geo+json", key="p9_dl_geo")
    d2.download_button(T("p9_report.dl_meta", "Download metadata.json"), json.dumps(metadata, indent=2),
                       "tala_metadata.json", "application/json", key="p9_dl_meta")


st.markdown(f"##### {T('p9_report.map_head', 'A map that cannot point at a person')}")
_generalize()

# ---------------------------------------------------------------------------
# 2. Report cards + CSV summary
# ---------------------------------------------------------------------------
st.markdown(f"##### {T('p9_report.cards_head', 'Report cards')}")


@st.fragment
def _cards():
    sizes = labels[labels != ""].value_counts()
    top_n = st.slider(T("p9_report.top_n", "Places with a card"), 3, min(12, max(3, len(sizes))),
                      min(6, max(3, len(sizes))), key="p9_top") if len(sizes) > 3 else len(sizes)
    hot_params = st.session_state.get("p8_params", (20, 50, 10, ""))
    key = (p["source_key"], p["mode"], p["unit"], p["eps_m"], p["min_samples"], sw_custom, sw_tl, top_n,
           tuple(hot_params))
    with audio.result(tracks.SIGNATURE[PAGE], key):
        sent = compare.place_sentiment(comp, lab_arr, min_n=1).set_index("place")
        asp = maps.aspect_by_place(maps.aspect_rows_for(p["source_key"], p["text_col"]),
                                   lab_arr, min_n=MIN_ASPECT_N)
        worst = asp.sort_values("pct_neg", ascending=False).drop_duplicates("place").set_index("place")
        th = maps.themes_for(p["source_key"], p["text_col"], sw_custom, sw_tl, True, THEME_K)
        names = maps.theme_names(th["top_terms"], asp_names) if th else []
        share = compare.theme_share(th["labels"], lab_arr) if th else pd.DataFrame()
        hs = maps.hotspots_for(p["source_key"], p["text_col"], p["lon_col"], p["lat_col"], p["km"],
                               p["mode"], float(hot_params[0]), float(hot_params[1]),
                               int(hot_params[2]), hot_params[3])
        rc = hs["row_class"]
        hot_row = np.array([c in ("hot_95", "hot_99") for c in rc])
        tested = rc != ""
        terms = {}
        for place in sizes.index[:top_n]:
            tbl = maps.logodds_for(p["source_key"], p["text_col"], sw_custom, sw_tl, p["lon_col"],
                                   p["lat_col"], p["km"], p["mode"], p["unit"], p["eps_m"],
                                   p["min_samples"], place, "")
            tbl = tbl[(tbl["z"] > 0) & (tbl["count_a"] >= 10)]
            tbl = maps.drop_place_terms(tbl, p["source_key"], p["text_col"])
            terms[place] = tbl["term"].head(5).tolist()

    rows = []
    for place, n in sizes.items():
        s = sent.loc[place]
        w = worst.loc[place] if place in worst.index else None
        theme_txt, theme_pct = "", np.nan
        if th is not None and place in share.index:
            tid = int(share.loc[place].idxmax())
            theme_txt, theme_pct = names[tid], 100 * float(share.loc[place].max())
        m = (lab_arr == place) & tested
        hot_pct = 100 * float(hot_row[m].mean()) if m.any() else np.nan
        rows.append({
            "place": place, "n": int(n), "pct_negative": round(float(s["pct_neg"]), 1),
            "ci_low": round(float(s["lo"]), 1), "ci_high": round(float(s["hi"]), 1),
            "worst_aspect": asp_names[w["aspect"]] if w is not None else "",
            "worst_aspect_pct_negative": round(float(w["pct_neg"]), 1) if w is not None else np.nan,
            "main_theme": theme_txt, "main_theme_share": round(theme_pct, 1) if theme_pct == theme_pct else np.nan,
            "pct_comments_in_hot_cells": round(hot_pct, 1) if hot_pct == hot_pct else np.nan,
            "hotspot_flag": bool(hot_pct >= 100 * HOT_SHARE_FLAG) if hot_pct == hot_pct else False,
            "distinctive_terms": ", ".join(terms.get(place, [])),
        })
    summary = pd.DataFrame(rows)

    shown = summary.head(top_n)
    for start in range(0, len(shown), 2):
        cols = st.columns(2)
        for col, r in zip(cols, shown.iloc[start:start + 2].itertuples()):
            with col, st.container(border=True):
                st.markdown(f"**{r.place}** · {r.n:,} {T('p9_report.comments', 'comments')}")
                st.markdown(
                    f"- {T('p9_report.c_neg', 'Negative')}: **{r.pct_negative:.0f}%** "
                    f"({r.ci_low:.0f}–{r.ci_high:.0f}%)")
                if r.worst_aspect:
                    st.markdown(f"- {T('p9_report.c_worst', 'Most faulted')}: **{r.worst_aspect}** "
                                f"({r.worst_aspect_pct_negative:.0f}% {T('p9_report.negative', 'negative')})")
                if r.main_theme:
                    st.markdown(f"- {T('p9_report.c_theme', 'Main theme')}: **{r.main_theme}** "
                                f"({r.main_theme_share:.0f}%)")
                if r.pct_comments_in_hot_cells == r.pct_comments_in_hot_cells:
                    flag = (T("p9_report.hot_yes", "Hotspot") if r.hotspot_flag
                            else T("p9_report.hot_no", "No hotspot"))
                    st.markdown(f"- {T('p9_report.c_hot', 'Complaint hotspot')}: **{flag}** "
                                f"({r.pct_comments_in_hot_cells:.0f}% {T('p9_report.in_hot', 'of comments in hot cells')})")
                if r.distinctive_terms:
                    st.markdown(f"- {T('p9_report.c_terms', 'Distinctive words')}: {r.distinctive_terms}")

    st.download_button(T("p9_report.dl_csv", "Download place summary (CSV)"),
                       summary.to_csv(index=False), "tala_place_summary.csv", "text/csv", key="p9_dl_csv")


_cards()
ui.page_done(PAGE)
ui.track_footer(PAGE)
