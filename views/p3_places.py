"""Step 3 (Lugar): group comments into places, by Region or by DBSCAN Cluster.

The unit toggle writes ``places.SS_UNIT`` and the DBSCAN sliders write
``dl.SS_CLUSTER_PARAMS``; Chapter 2 reads both through ``places.params()``.
Widgets use local keys (a widget not drawn on another page loses its state) and
the journey keys are written from their values on every run."""
import numpy as np
import plotly.express as px
import streamlit as st

from core import audio, places, tracks, ui, viz
from core import data_loader as dl

PAGE = "p3_places"
_t = ui._t

ui.page_header(PAGE, "where")
ui.auto_ran(PAGE)
ui.learn_page(
    PAGE,
    code=(
        "from sklearn.cluster import DBSCAN\n"
        "from sklearn.neighbors import NearestNeighbors\n"
        "from core import places\n\n"
        "# Region: the region of the place each comment names\n"
        "region = places.assign_place(located, parsed, unit='region')\n\n"
        "# Cluster: DBSCAN on projected metres, eps in metres\n"
        "xy = to_metres(located.dropna())              # UTM, not degrees\n"
        "d, _ = NearestNeighbors(n_neighbors=11).fit(xy).kneighbors(xy)\n"
        "kdist = np.sort(d[:, 10])                     # plot it; eps sits at the elbow\n"
        "labels = DBSCAN(eps=15000, min_samples=10).fit_predict(xy)   # -1 = noise"
    ),
)

if not places.has_geo():
    ui.locked(_t("p3_places.no_geo", "This dataset has no coordinates yet."),
              "p1_data", _t("p3_places.pick_coords", "Pick the longitude and latitude columns"))

K_UNIT, K_EPS, K_MIN, K_K = "p3_unit", "p3_eps", "p3_min", "p3_k"
TOP_N = 20


def _unit_label(unit: str) -> str:
    return {"region": _t("p3_places.unit_region", "Region"),
            "cluster": _t("p3_places.unit_cluster", "Cluster")}[unit]


def _reset_defaults() -> None:
    st.session_state[K_EPS] = dl.DEFAULT_EPS_M / 1000
    st.session_state[K_MIN] = dl.DEFAULT_MIN_SAMPLES


@st.cache_data(show_spinner=False, max_entries=8, ttl=1800)
def _kdistance(source_key: str, lon_col: str, lat_col: str, text_col: str,
               km: float, mode: str, k: int) -> np.ndarray:
    """Sorted k-th neighbour distance (metres) of the *located* points.

    Keyed on the dataset and parameters, never on language or session."""
    import geopandas as gpd

    from core import geo

    located = places.locate_for(source_key, lon_col, lat_col, text_col, km, mode)
    ok = located["lon"].notna().to_numpy()
    if ok.sum() <= k:
        return np.array([])
    pts = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(located["lon"][ok], located["lat"][ok]), crs="EPSG:4326")
    return geo.k_distance(geo.to_metric(pts), k)


def _cluster_controls() -> None:
    cur_eps, cur_min = dl.cluster_params()
    st.session_state.setdefault(K_EPS, float(min(100.0, max(1.0, cur_eps / 1000))))
    st.session_state.setdefault(K_MIN, int(min(50, max(2, cur_min))))
    c1, c2, c3 = st.columns([2, 2, 1])
    eps_km = c1.slider(_t("p3_places.eps", "Neighbourhood radius, eps (km)"),
                       1.0, 100.0, step=1.0, key=K_EPS)
    min_samples = c2.slider(_t("p3_places.min_samples", "Minimum comments per cluster"),
                            2, 50, key=K_MIN)
    c3.button(_t("p3_places.defaults", "Reset to defaults"), on_click=_reset_defaults)
    st.session_state[dl.SS_CLUSTER_PARAMS] = (float(eps_km) * 1000, int(min_samples))

    p = places.params()
    with st.expander(_t("p3_places.kdist_head", "Choosing eps: the k-distance elbow"), expanded=False):
        k = st.slider(_t("p3_places.k", "k (neighbours)"), 3, 20, key=K_K,
                      value=int(min(20, max(3, min_samples))))
        kd = _kdistance(p["source_key"], p["lon_col"], p["lat_col"], p["text_col"],
                        p["km"], p["mode"], k)
        if len(kd):
            fig = px.line(x=np.arange(len(kd)), y=kd / 1000,
                          color_discrete_sequence=[viz.categorical(ui.palette())[0]])
            fig.add_hline(y=eps_km, line_dash="dash", line_color=viz.NU_GOLD_DEEP,
                          annotation_text=f"eps = {eps_km:g} km")
            fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=300,
                              xaxis_title=_t("p3_places.kd_x", "Points, sorted by distance"),
                              yaxis_title=_t("p3_places.kd_y", "Distance to neighbour {k} (km)", k=k))
            st.plotly_chart(fig, width="stretch")
        else:
            st.caption(_t("p3_places.kd_none", "Not enough located points for this chart."))


@st.fragment
def _places_page() -> None:
    from core import maps

    st.session_state.setdefault(K_UNIT, places.params()["unit"])
    unit = st.radio(_t("p3_places.unit", "Group comments by"), list(places.UNITS),
                    key=K_UNIT, format_func=_unit_label, horizontal=True)
    st.session_state[places.SS_UNIT] = unit
    if unit == "cluster":
        _cluster_controls()

    p = places.params()
    with audio.result(tracks.SIGNATURE[PAGE],
                      (p["source_key"], p["km"], p["mode"], unit,
                       p["eps_m"] if unit == "cluster" else 0,
                       p["min_samples"] if unit == "cluster" else 0)):
        located = places.active_located()
        labels = places.active_places()
    if located is None or labels is None:
        ui.locked(_t("p3_places.gone", "The dataset changed. Pick the columns again."),
                  "p1_data", _t("p3_places.pick_coords", "Pick the longitude and latitude columns"))

    pts = places.place_points(located, labels, unit)
    total = len(labels)
    n_none = int((labels == "").sum())

    m1, m2, m3 = st.columns(3)
    m1.metric(_t("p3_places.m_places", "Places"), f"{len(pts):,}")
    m2.metric(_t("p3_places.m_assigned", "Comments in a place"), f"{total - n_none:,}")
    m3.metric(_t("p3_places.m_none", "Unassigned or noise"),
              f"{n_none:,} ({100 * n_none / max(total, 1):.0f}%)")
    if not len(pts):
        ui.info(_t("p3_places.no_places", "No places found. Try a larger eps or fewer comments per cluster."))
        return

    cat = viz.categorical(ui.palette())
    top = pts.head(TOP_N)
    fig = px.bar(top, x="n", y="place", orientation="h", color_discrete_sequence=[cat[0]])
    layout = viz.plotly_template(ui.palette())["layout"]
    layout["yaxis"] = {**layout["yaxis"], "categoryorder": "total ascending", "title": ""}
    fig.update_layout(**layout, height=max(260, 24 * len(top) + 80), showlegend=False,
                      xaxis_title=_t("p3_places.bar_x", "Comments"))
    st.markdown(_t("p3_places.bar_head", "#### Comments per place (top {n})", n=len(top)))
    st.plotly_chart(fig, width="stretch")

    st.markdown(_t("p3_places.map_head", "#### Where the places are"))
    frame = pts.rename(columns={"n": "n_points"}).copy()
    frame["tip"] = [f"{pl}: {n:,}" for pl, n in zip(pts["place"], pts["n"])]
    st.pydeck_chart(
        maps.deck([maps.land_layer(), maps.centroid_layer(frame)], maps.view_for(frame), "{tip}"),
        height=460, width="stretch")


_places_page()

ui.page_done(PAGE)
ui.track_footer(PAGE)
