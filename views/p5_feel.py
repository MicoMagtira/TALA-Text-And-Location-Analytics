"""Step 5 (p5_feel): how each place feels.

VADER sentiment per place: a bubble map (size = comments, colour = % negative) and a
ranked dot plot with Wilson intervals. Places with too few comments are greyed out and
say why, because a percentage from a handful of comments is mostly noise.
"""
import html

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from core import audio, compare, i18n, maps, places, salita, tracks, ui, viz
from core import data_loader as dl

PAGE = "p5_feel"
T = ui._t
MAX_ROWS = 30

dl.ensure_loaded()
ui.page_header(PAGE, "what")
if i18n.t(f"{PAGE}.blurb") == f"{PAGE}.blurb":
    st.markdown(T(f"{PAGE}.blurb", "Which places sound most unhappy, and how sure can we be?"))
ui.auto_ran(PAGE)
ui.learn_page(
    PAGE,
    code=(
        "from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer\n"
        "import numpy as np\n\n"
        "sia = SentimentIntensityAnalyzer()\n"
        "df['compound'] = [sia.polarity_scores(t)['compound'] for t in df.text]\n"
        "df['neg'] = df.compound <= -0.05\n\n"
        "def wilson(k, n, z=1.96):\n"
        "    p = k / n\n"
        "    centre = (p + z*z/(2*n)) / (1 + z*z/n)\n"
        "    half = z * np.sqrt(p*(1-p)/n + z*z/(4*n*n)) / (1 + z*z/n)\n"
        "    return centre - half, centre + half\n\n"
        "g = df.groupby('place').neg.agg(['sum', 'size'])\n"
        "g['lo'], g['hi'] = wilson(g['sum'], g['size'])"
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
key = (p["source_key"], p["text_col"], p["km"], p["mode"], p["unit"], p["eps_m"], p["min_samples"])


@st.fragment
def _feel():
    min_n = st.slider(T("p5_feel.min_n", "Minimum comments per place"), 5, 300, 30, 5, key="p5_min")
    with audio.result(tracks.SIGNATURE[PAGE], key + (min_n,)):
        comp = salita.sentiment_for(p["source_key"], p["text_col"])
        table = compare.place_sentiment(comp, labels.to_numpy(object), min_n=min_n)
    if table.empty:
        ui.info(T("ch2.no_places", "No comments could be assigned to a place."))
        return

    overall = 100 * float((comp <= -0.05).mean())
    small = table[~table["ok"]]
    m1, m2, m3 = st.columns(3)
    m1.metric(T("p5_feel.m_places", "Places shown"), int(table["ok"].sum()))
    m2.metric(T("p5_feel.m_overall", "Negative overall"), f"{overall:.0f}%")
    m3.metric(T("p5_feel.m_greyed", "Greyed out (too few)"), len(small))

    # --- bubble map -------------------------------------------------------
    pts = places.place_points(located, labels, p["unit"]).drop(columns="n").merge(table, on="place")
    reason = T("p5_feel.reason", "fewer than {min_n} comments", min_n=min_n)
    neg_word = T("p5_feel.negative", "negative")
    tips = []
    for r in pts.itertuples():
        t = (f"<b>{html.escape(r.place)}</b><br>n = {r.n:,}<br>"
             f"{r.pct_neg:.0f}% {neg_word} ({r.lo:.0f}–{r.hi:.0f}%)")
        tips.append(t if r.ok else t + f"<br><i>{html.escape(reason)}</i>")
    pts["tip"] = tips
    ok_vals = pts.loc[pts["ok"], "pct_neg"]
    lo_v, hi_v = (float(ok_vals.min()), float(ok_vals.max())) if len(ok_vals) else (0.0, 100.0)
    frame = maps.bubble_frame(pts, "pct_neg", seq, lo_v, hi_v)
    st.pydeck_chart(maps.deck([maps.bubble_layer(frame)], maps.view_for(frame), "{tip}"),
                    height=480, width="stretch")
    st.markdown(maps.gradient_legend_html(
        seq, f"{lo_v:.0f}%", f"{hi_v:.0f}%",
        T("p5_feel.legend", "Colour = % negative. Bubble size = number of comments. Grey = too few comments.")),
        unsafe_allow_html=True)

    # --- ranked dot plot --------------------------------------------------
    st.markdown(f"##### {T('p5_feel.rank_head', '% negative by place, with 95% interval')}")
    show = table.sort_values("n", ascending=False).head(MAX_ROWS).sort_values("pct_neg")
    fig = go.Figure()
    for ok, color, name in ((True, cat[1], T("p5_feel.enough", "Enough comments")),
                            (False, viz.INK_MUTED, reason)):
        d = show[show["ok"] == ok]
        if d.empty:
            continue
        fig.add_trace(go.Scatter(
            x=d["pct_neg"], y=d["place"], mode="markers", name=name,
            marker=dict(color=color, size=10),
            error_x=dict(type="data", symmetric=False, array=d["hi"] - d["pct_neg"],
                         arrayminus=d["pct_neg"] - d["lo"], color=color, thickness=1.5),
            customdata=np.column_stack([d["n"], d["lo"], d["hi"]]),
            hovertemplate=("%{y}<br>%{x:.1f}% " + neg_word +
                           " (%{customdata[1]:.0f}–%{customdata[2]:.0f}%)<br>n = %{customdata[0]:,}"
                           "<extra></extra>")))
    fig.add_vline(x=overall, line_dash="dot", line_color=viz.INK_MUTED)
    layout = viz.plotly_template(ui.palette())["layout"]
    layout["legend"] = {**layout["legend"], "orientation": "h", "y": -0.2}
    fig.update_layout(**layout, height=120 + 26 * len(show), margin=dict(l=10, r=10, t=10, b=40),
                      yaxis_title="", xaxis_title=T("p5_feel.axis", "% of comments negative"))
    fig.update_xaxes(range=[0, min(100, float(show["hi"].max()) + 5)])
    st.plotly_chart(fig, width="stretch")
    if len(table) > MAX_ROWS:
        st.caption(T("p5_feel.capped", "Showing the {n} largest places.", n=MAX_ROWS))


_feel()
ui.page_done(PAGE)
ui.track_footer(PAGE)
