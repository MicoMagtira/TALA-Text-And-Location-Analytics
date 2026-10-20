"""Step 8 (p8_hotspots): where complaints cluster.

Getis-Ord Gi* on a square grid: each cell holds the share of its comments that are
negative, and Gi* asks whether a cell and its neighbours are higher (hot) or lower
(cold) than chance would give. Classes at 90 / 95 / 99 % confidence.
"""
import html

import numpy as np
import streamlit as st

from core import audio, i18n, maps, places, salita, tracks, ui, viz
from core import data_loader as dl

PAGE = "p8_hotspots"
T = ui._t
SS_PARAMS = "p8_params"        # (cell_km, radius_km, min_n, aspect): read by the Place report
ASPECTS = ["waiting", "staff", "cost", "medicine", "facilities", "access"]
ASPECT_DEFAULT = {"waiting": "Waiting", "staff": "Staff", "cost": "Cost",
                  "medicine": "Medicine", "facilities": "Facilities", "access": "Access"}

dl.ensure_loaded()
ui.page_header(PAGE, "what")
if i18n.t(f"{PAGE}.blurb") == f"{PAGE}.blurb":
    st.markdown(T(f"{PAGE}.blurb", "Where are complaints bunched together more than chance would explain?"))
ui.auto_ran(PAGE)
ui.learn_page(
    PAGE,
    code=(
        "import numpy as np\n"
        "from sklearn.neighbors import BallTree\n\n"
        "# x = share of negative comments per grid cell, xy = cell centres in metres\n"
        "n, xbar, s = len(x), x.mean(), x.std()          # population std\n"
        "tree = BallTree(xy)\n"
        "z = np.zeros(n)\n"
        "for i, idx in enumerate(tree.query_radius(xy, r=radius_m)):\n"
        "    w = len(idx)                                 # binary weights, i included\n"
        "    z[i] = (x[idx].sum() - xbar * w) / (s * np.sqrt((n * w - w * w) / (n - 1)))\n\n"
        "hot_99 = z >= 2.576; hot_95 = z >= 1.960; hot_90 = z >= 1.645"
    ),
)

if not places.has_geo():
    ui.locked(T("ch2.locked", "This step needs a text column and longitude/latitude columns."),
              "p1_data", T("ch2.locked_link", "Go to Data"))

p = places.params()
if places.active_located() is None:
    ui.info(T("ch2.no_places", "No comments could be assigned to a place."))
    ui.page_done(PAGE)
    ui.track_footer(PAGE)
    st.stop()

cat = viz.categorical(ui.palette(), 2)
cold_hex, hot_hex = cat[0], cat[1]


def _nearest_place(lon: float, lat: float) -> str:
    gz = places.load_gazetteer()
    gz = gz[gz["kind"].isin(["province", "city"])]
    d = places.haversine_km(lon, lat, gz["lon"].to_numpy(), gz["lat"].to_numpy())
    return str(gz["name"].iloc[int(np.argmin(d))])


@st.fragment
def _hotspots():
    c1, c2, c3 = st.columns(3)
    cell_km = c1.slider(T("p8_hotspots.cell", "Grid cell size (km)"), 5, 50, 20, 5, key="p8_cell")
    radius_km = c2.slider(T("p8_hotspots.radius", "Neighbourhood radius (km)"), 10, 150, 50, 5, key="p8_rad")
    min_n = c3.slider(T("p8_hotspots.min_n", "Minimum comments per cell"), 3, 50, 10, 1, key="p8_min")
    value = st.selectbox(
        T("p8_hotspots.value", "What to map"), [""] + ASPECTS, key="p8_value",
        format_func=lambda a: (T("p8_hotspots.all", "All comments: share negative") if a == ""
                               else T("p8_hotspots.aspect_neg", "{aspect}: share negative",
                                      aspect=T(f"asp.{a}", ASPECT_DEFAULT[a]))))
    st.session_state[SS_PARAMS] = (cell_km, radius_km, min_n, value)
    if radius_km < 1.5 * cell_km:
        ui.info(T("p8_hotspots.small_radius",
                  "The radius is about one cell, so each cell is barely compared with neighbours. Try a radius of at least 2 cells."))

    key = (p["source_key"], p["text_col"], p["lon_col"], p["lat_col"], p["km"], p["mode"],
           float(cell_km), float(radius_km), int(min_n), value)
    with audio.result(tracks.SIGNATURE[PAGE], key):
        res = salita.hotspots_for(*key)
    cells = res["cells"]
    if cells is None or len(cells) < 2:
        ui.info(T("p8_hotspots.none", "Not enough cells have {n} comments. Lower the minimum or enlarge the cells.",
                  n=min_n))
        return

    cls = cells["hot_class"]
    hot = cls.str.startswith("hot").sum()
    cold = cls.str.startswith("cold").sum()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(T("p8_hotspots.m_cells", "Cells tested"), f"{len(cells):,}")
    m2.metric(T("p8_hotspots.m_hot", "Hot cells"), int(hot))
    m3.metric(T("p8_hotspots.m_hot99", "Hot at 99%"), int((cls == "hot_99").sum()))
    m4.metric(T("p8_hotspots.m_cold", "Cold cells"), int(cold))

    show = cells.copy()
    lab = {"ns": T("p8_hotspots.ns", "not significant")}
    tips = []
    for r in show.itertuples():
        kind = lab["ns"] if r.hot_class == "ns" else (
            f"{T('p8_hotspots.hot', 'hot') if r.hot_class.startswith('hot') else T('p8_hotspots.cold', 'cold')} "
            f"{r.hot_class.split('_')[1]}%")
        tips.append(f"<b>{html.escape(kind)}</b> (z = {r.z:.2f})<br>"
                    f"{100 * r.share_neg:.0f}% {T('p8_hotspots.negative', 'negative')}, n = {int(r.n_points):,}")
    show["tip"] = tips
    show = show.drop(columns=["cx", "cy"])
    cen = show.geometry.centroid
    centres = __import__("pandas").DataFrame({"lon": cen.x.to_numpy(), "lat": cen.y.to_numpy()})
    layers = [maps.hotspot_layer(show, hot_hex, cold_hex)]
    st.pydeck_chart(maps.deck(layers, maps.view_for(centres), "{properties.tip}"),
                    height=520, width="stretch")
    st.markdown(maps.hotspot_legend_html(hot_hex, cold_hex, {
        "hot": T("p8_hotspots.leg_hot", "Hot (more negative than chance)"),
        "cold": T("p8_hotspots.leg_cold", "Cold (less negative)"),
        "ns": T("p8_hotspots.leg_ns", "Not significant"),
        "level": T("p8_hotspots.leg_level", "{level}% confidence", level="{level}")}), unsafe_allow_html=True)
    st.caption(T("p8_hotspots.safe99",
                 "Many cells are tested at once, so a few 90% cells are expected by luck. Trust the 99% cells most."))

    top = cells.loc[cells["z"].idxmax()]
    if top["z"] >= 1.645:
        c = top.geometry.centroid
        st.caption(T("p8_hotspots.strongest",
                     "Strongest hotspot: near {place} (z = {z:.1f}, {share}% negative in {n} comments).",
                     place=_nearest_place(c.x, c.y), z=float(top["z"]),
                     share=f"{100 * top['share_neg']:.0f}", n=f"{int(top['n_points']):,}"))


_hotspots()
ui.page_done(PAGE)
ui.track_footer(PAGE)
