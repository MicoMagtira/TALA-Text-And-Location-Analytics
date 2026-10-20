"""Step 2 (Lugar): read the place a comment names, check it against its GPS.

The km slider and the location-source radio write ``places.SS_KM`` /
``places.SS_MODE``, which Chapter 2 reads. Their widgets use local keys and the
value is copied to the journey keys on every run: a widget that is not drawn on
another page loses its state, the journey parameters must not."""
import numpy as np
import pandas as pd
import streamlit as st

from core import audio, places, tracks, ui, viz
from core import data_loader as dl

PAGE = "p2_textgps"
_t = ui._t

ui.page_header(PAGE, "where")
ui.auto_ran(PAGE)
ui.learn_page(
    PAGE,
    code=(
        "from core import places\n\n"
        "parsed = places.geoparse(df['text'])        # longest title-case match\n"
        "check = places.text_vs_gps(parsed, df['lon'], df['lat'], km=50)\n"
        "check['status'].value_counts()              # agree / disagree / gps_invalid ...\n\n"
        "# the distance behind 'agree': great-circle km between GPS and named place\n"
        "def haversine_km(lon1, lat1, lon2, lat2):\n"
        "    lon1, lat1, lon2, lat2 = map(np.radians, (lon1, lat1, lon2, lat2))\n"
        "    a = (np.sin((lat2 - lat1) / 2) ** 2\n"
        "         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)\n"
        "    return 6371.0088 * 2 * np.arcsin(np.sqrt(a))\n\n"
        "located = places.locate(parsed, check, df['lon'], df['lat'], mode='repaired')"
    ),
)

if not places.has_geo():
    ui.locked(_t("p2_textgps.no_geo", "This dataset has no coordinates yet."),
              "p1_data", _t("p2_textgps.pick_coords", "Pick the longitude and latitude columns"))

MAX_LINES = 400
K_KM, K_MODE, K_INVALID = "p2_km", "p2_mode", "p2_show_invalid"


def _mode_label(mode: str) -> str:
    return {
        "repaired": _t("p2_textgps.mode_repaired", "Repair from the text (recommended)"),
        "gps": _t("p2_textgps.mode_gps", "Trust the GPS only"),
        "agree": _t("p2_textgps.mode_agree", "Only where both agree"),
    }[mode]


def _metric(col, label: str, n: int, total: int) -> None:
    """Count as the value, share as a quiet note (a combined string truncates)."""
    col.metric(label, f"{n:,}", f"{100 * n / max(total, 1):.0f}%",
               delta_color="off", delta_arrow="off")


def _numeric(col) -> np.ndarray:
    return pd.to_numeric(col, errors="coerce").to_numpy(float)


def _lines_layer(df: pd.DataFrame, rgba):
    """GPS point -> named place, for a deterministic sample of disagreements.

    Built here (not in core/maps.py) because only this page draws such lines."""
    import pydeck as pdk

    return pdk.Layer(
        "LineLayer", id="gps-to-place", data=df,
        get_source_position="[lon, lat]", get_target_position="[lon_t, lat_t]",
        get_color=list(rgba), get_width=1.2, width_units="'pixels'",
        pickable=True, auto_highlight=True)


def _dots(df: pd.DataFrame, rgba, radius_px: int, layer_id: str, lon="lon", lat="lat"):
    import pydeck as pdk

    return pdk.Layer(
        "ScatterplotLayer", id=layer_id, data=df, get_position=f"[{lon}, {lat}]",
        get_fill_color=list(rgba), get_radius=radius_px, radius_units="'pixels'",
        radius_min_pixels=1, pickable=False)


@st.fragment
def _check_and_map() -> None:
    from core import maps

    p = places.params()
    st.session_state.setdefault(K_KM, int(p["km"]))
    st.session_state.setdefault(K_MODE, p["mode"])
    c1, c2 = st.columns(2)
    km = c1.slider(_t("p2_textgps.km", "Agree if within (km)"), 10, 200, key=K_KM, step=5,
                   help=_t("p2_textgps.km_help",
                           "How far the GPS point may sit from the place the comment names."))
    mode = c2.radio(_t("p2_textgps.mode", "Which locations should the next steps use?"),
                    list(places.MODES), key=K_MODE, format_func=_mode_label)
    # The journey keys are what Chapter 2 reads; write them before any lookup.
    st.session_state[places.SS_KM] = float(km)
    st.session_state[places.SS_MODE] = mode

    p = places.params()
    df = dl.active_df()
    with audio.result(tracks.SIGNATURE[PAGE], (p["source_key"], p["km"], p["mode"])):
        parsed = places.active_parsed()
        check = places.active_check()
        located = places.active_located()
    if parsed is None or check is None or located is None:
        ui.locked(_t("p2_textgps.gone", "The dataset changed. Pick the columns again."),
                  "p1_data", _t("p2_textgps.pick_coords", "Pick the longitude and latitude columns"))

    total = len(check)
    status = check["status"]
    n_named = int((parsed["status"] != "no_place").sum())
    n_agree = int((status == "agree").sum())
    n_dis = int((status == "disagree").sum())
    n_bad = int((status == "gps_invalid").sum())

    m1, m2, m3, m4 = st.columns(4)
    _metric(m1, _t("p2_textgps.m_named", "Name a place"), n_named, total)
    _metric(m2, _t("p2_textgps.m_agree", "GPS agrees"), n_agree, total)
    _metric(m3, _t("p2_textgps.m_disagree", "GPS disagrees"), n_dis, total)
    _metric(m4, _t("p2_textgps.m_invalid", "GPS invalid"), n_bad, total)

    wrong = 100 * (n_dis + n_bad) / max(total, 1)
    st.markdown(_t(
        "p2_textgps.lesson",
        "**About {pct}% of these coordinates are wrong.** The text tells us where they belong.",
        pct=f"{wrong:.0f}"))

    # ---- map ---------------------------------------------------------------
    cat = viz.categorical(ui.palette())
    col_agree, col_dis, col_bad = (viz.hex_to_rgba(c, 190) for c in cat[:3])
    col_other = (150, 150, 150, 110)

    lon = _numeric(df[p["lon_col"]])
    lat = _numeric(df[p["lat_col"]])
    base = pd.DataFrame({"lon": lon, "lat": lat, "status": status.to_numpy()})
    base["lon_t"] = parsed["lon_t"].to_numpy(float)
    base["lat_t"] = parsed["lat_t"].to_numpy(float)

    show_bad = st.toggle(_t("p2_textgps.show_invalid", "Show GPS points that fall outside the Philippines"),
                         key=K_INVALID, value=False)

    layers = [maps.land_layer()]
    valid = base[(base["status"] != "gps_invalid") & base["lon"].notna()]
    layers.append(_dots(valid[valid["status"].isin(["no_place", "ambiguous"])],
                        col_other, 2, "pts-other"))
    layers.append(_dots(valid[valid["status"] == "agree"], col_agree, 3, "pts-agree"))
    dis = base[base["status"] == "disagree"]
    layers.append(_dots(dis, col_dis, 3, "pts-disagree"))
    if show_bad:
        bad = base[(base["status"] == "gps_invalid") & base["lon"].notna()
                   & (base["lon"].abs() <= 180) & (base["lat"].abs() <= 90)]
        layers.append(_dots(bad, col_bad, 3, "pts-invalid"))

    sample = dis.dropna(subset=["lon_t", "lat_t"])
    if len(sample) > MAX_LINES:
        sample = sample.sample(MAX_LINES, random_state=0)        # deterministic
    sample = sample.copy()
    sample["tip"] = [f"{d:,.0f} km" for d in
                     places.haversine_km(sample["lon"], sample["lat"],
                                         sample["lon_t"], sample["lat_t"])]
    layers.append(_lines_layer(sample, (*col_dis[:3], 150)))

    view_df = valid if len(valid) else base
    st.pydeck_chart(maps.deck(layers, maps.view_for(view_df), "{tip}"),
                    height=480, width="stretch")

    # Legend as plain text: colour name next to what it means.
    def dot(c):
        return f'<span style="color:{c};font-size:1.1em">&#9679;</span>'

    st.markdown(
        f"{dot(cat[0])} {_t('p2_textgps.lg_agree', 'agree')} &nbsp; "
        f"{dot(cat[1])} {_t('p2_textgps.lg_disagree', 'disagree (line points to the named place)')} &nbsp; "
        f"{dot(cat[2])} {_t('p2_textgps.lg_invalid', 'invalid GPS')} &nbsp; "
        f"{dot('#969696')} {_t('p2_textgps.lg_other', 'no clear place')}",
        unsafe_allow_html=True)
    if len(dis) > len(sample):
        st.caption(_t("p2_textgps.lines_sampled", "Lines are drawn for {shown} of {total} disagreements.",
                      shown=f"{len(sample):,}", total=f"{len(dis):,}"))

    # ---- what the next steps will use --------------------------------------
    src = located["source"]
    st.caption(_t(
        "p2_textgps.use_caption",
        "Next steps will use {gps} GPS points and {fixed} locations repaired from the text; {none} comments have no usable location.",
        gps=f"{int((src == 'gps').sum()):,}", fixed=f"{int((src == 'place').sum()):,}",
        none=f"{int((src == '').sum()):,}"))

    # ---- sample table: ids and places only, never the comment --------------
    ids = df[next((c for c in df.columns if str(c).lower() == "id"), None)] \
        if any(str(c).lower() == "id" for c in df.columns) else None
    rows = pd.DataFrame({
        _t("p2_textgps.t_id", "id"): (ids.astype(str).to_numpy() if ids is not None
                                      else np.arange(total).astype(str)),
        _t("p2_textgps.t_place", "Named place"): parsed["place"].to_numpy(),
        _t("p2_textgps.t_province", "Province"): parsed["province"].to_numpy(),
        _t("p2_textgps.t_dist", "Distance (km)"): check["dist_km"].round(0).to_numpy(),
    })[(status == "disagree").to_numpy()]
    if len(rows):
        with st.expander(_t("p2_textgps.table_head", "Largest disagreements"), expanded=False):
            st.dataframe(rows.sort_values(_t("p2_textgps.t_dist", "Distance (km)"),
                                          ascending=False).head(15),
                         hide_index=True, width="stretch")


_check_and_map()

ui.page_done(PAGE)
ui.track_footer(PAGE)
