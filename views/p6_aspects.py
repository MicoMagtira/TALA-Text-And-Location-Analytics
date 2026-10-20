"""Step 6 (p6_aspects): what they praise or fault.

Aspect sentiment: only the sentences that mention an aspect (waiting, staff, cost,
medicine, facilities, access; English and Filipino terms from ``data/aspects.json``) are
scored with VADER, then summed per place. A heatmap of % negative, and a map for one
chosen aspect. This is a lexicon method: it is transparent and fast, and it misses
paraphrase and sarcasm (see Learn).
"""
import html

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from core import audio, i18n, maps, places, salita, tracks, ui, viz
from core import data_loader as dl

PAGE = "p6_aspects"
T = ui._t
ASPECTS = ["waiting", "staff", "cost", "medicine", "facilities", "access"]
DEFAULT_ASPECT_NAMES = {"waiting": "Waiting", "staff": "Staff", "cost": "Cost",
                        "medicine": "Medicine", "facilities": "Facilities", "access": "Access"}


def aspect_name(a: str) -> str:
    return T(f"asp.{a}", DEFAULT_ASPECT_NAMES.get(a, a.title()))


dl.ensure_loaded()
ui.page_header(PAGE, "what")
if i18n.t(f"{PAGE}.blurb") == f"{PAGE}.blurb":
    st.markdown(T(f"{PAGE}.blurb", "What do people in each place praise or fault: waiting, staff, cost, medicine?"))
ui.auto_ran(PAGE)
ui.learn_page(
    PAGE,
    code=(
        "import re\n\n"
        "aspects = {'waiting': ['wait', 'queue', 'delay', 'hintay', 'pila'],\n"
        "           'staff':   ['nurse', 'doctor', 'rude', 'mabait']}\n"
        "rx = {a: re.compile(r'\\b(?:' + '|'.join(w) + r')\\w*', re.I)\n"
        "      for a, w in aspects.items()}\n\n"
        "rows = []\n"
        "for place, text in zip(df.place, df.text):\n"
        "    for sent in re.split(r'(?<=[.!?])\\s+', text):\n"
        "        for a, pattern in rx.items():\n"
        "            if pattern.search(sent):\n"
        "                c = sia.polarity_scores(sent)['compound']\n"
        "                rows.append((place, a, c <= -0.05))\n"
        "out = pd.DataFrame(rows, columns=['place', 'aspect', 'neg'])\n"
        "out.groupby(['place', 'aspect']).neg.agg(['mean', 'size'])"
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

seq = viz.sequential_hexes(ui.seq_palette(), 6)
key = (p["source_key"], p["text_col"], p["km"], p["mode"], p["unit"], p["eps_m"], p["min_samples"])


@st.fragment
def _aspects():
    min_n = st.slider(T("p6_aspects.min_n", "Minimum sentences per cell"), 5, 100, 20, 5, key="p6_min")
    with audio.result(tracks.SIGNATURE[PAGE], key + (min_n,)):
        rows = salita.aspect_rows_for(p["source_key"], p["text_col"])
        tab = salita.aspect_by_place(rows, labels.to_numpy(object))
    if tab.empty:
        ui.info(T("p6_aspects.none", "No sentences mention an aspect."))
        return

    n_p = tab.pivot(index="place", columns="aspect", values="n").reindex(columns=ASPECTS)
    v_p = tab.pivot(index="place", columns="aspect", values="pct_neg").reindex(columns=ASPECTS)
    v_p = v_p.where(n_p >= min_n)
    order = n_p.sum(axis=1).sort_values().tail(25).index          # largest places last = top row
    n_p, v_p = n_p.loc[order], v_p.loc[order]
    text = [[("" if np.isnan(v) else f"<b>{v:.0f}%</b> n={int(n)}")
             for v, n in zip(vr, nr)] for vr, nr in zip(v_p.to_numpy(), n_p.fillna(0).to_numpy())]
    zmax = float(np.nanmax(v_p.to_numpy())) if np.isfinite(v_p.to_numpy()).any() else 100.0
    zmin = float(np.nanmin(v_p.to_numpy())) if np.isfinite(v_p.to_numpy()).any() else 0.0
    stops = [[i / (len(seq) - 1), c] for i, c in enumerate(seq)]
    fig = go.Figure(go.Heatmap(
        z=v_p.to_numpy(), x=[aspect_name(a) for a in ASPECTS], y=list(v_p.index),
        text=text, texttemplate="%{text}", colorscale=stops, zmin=zmin, zmax=zmax,
        hoverongaps=False, colorbar=dict(title=T("p6_aspects.cbar", "% negative"), thickness=12),
        hovertemplate="%{y} / %{x}<br>%{z:.1f}% negative<extra></extra>", xgap=2, ygap=2))
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"],
                      height=140 + 34 * len(v_p), margin=dict(l=10, r=10, t=10, b=10))
    fig.update_xaxes(side="top", showgrid=False)
    fig.update_yaxes(showgrid=False)
    st.plotly_chart(fig, width="stretch")
    st.caption(T("p6_aspects.caption",
                 "Each cell is the % of sentences about that aspect that read negative. n = matching sentences; blank = fewer than the minimum."))

    # --- one aspect on the map --------------------------------------------
    st.markdown(f"##### {T('p6_aspects.map_head', 'One aspect on the map')}")
    pick = st.segmented_control(T("p6_aspects.pick", "Aspect"), ASPECTS, default=ASPECTS[0],
                                format_func=aspect_name, key="p6_pick",
                                label_visibility="collapsed")
    pick = pick or ASPECTS[0]
    sub = tab[tab["aspect"] == pick].rename(columns={"n": "n_sent"})
    pts = places.place_points(located, labels, p["unit"])[["place", "lon", "lat"]].merge(sub, on="place")
    pts["n"] = pts["n_sent"]
    pts["ok"] = pts["n"] >= min_n
    word = T("p6_aspects.sentences", "sentences")
    neg_word = T("p6_aspects.negative", "negative")
    pts["tip"] = [f"<b>{html.escape(r.place)}</b><br>{aspect_name(pick)}: {r.pct_neg:.0f}% {neg_word}"
                  f"<br>n = {int(r.n):,} {word}" for r in pts.itertuples()]
    if pts.empty:
        ui.info(T("p6_aspects.none", "No sentences mention an aspect."))
        return
    ok_vals = pts.loc[pts["ok"], "pct_neg"]
    lo_v, hi_v = (float(ok_vals.min()), float(ok_vals.max())) if len(ok_vals) else (0.0, 100.0)
    frame = maps.bubble_frame(pts, "pct_neg", seq, lo_v, hi_v)
    st.pydeck_chart(maps.deck([maps.bubble_layer(frame)], maps.view_for(frame), "{tip}"),
                    height=440, width="stretch")
    st.markdown(maps.gradient_legend_html(
        seq, f"{lo_v:.0f}%", f"{hi_v:.0f}%",
        T("p6_aspects.legend", "Colour = % negative about this aspect. Size = sentences. Grey = too few.")),
        unsafe_allow_html=True)


_aspects()
ui.page_done(PAGE)
ui.track_footer(PAGE)
