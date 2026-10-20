"""Step 4 (p4_apart): what sets a place apart.

Weighted log-odds (Monroe, Colaresi & Quinn 2008) of one place against every other
place, or against a second place. Shows aggregated terms only, never comments.
"""
import plotly.graph_objects as go
import streamlit as st

from core import audio, i18n, places, salita, tracks, ui, viz
from core import data_loader as dl

PAGE = "p4_apart"
T = ui._t

dl.ensure_loaded()
ui.page_header(PAGE, "what")
if i18n.t(f"{PAGE}.blurb") == f"{PAGE}.blurb":
    st.markdown(T(f"{PAGE}.blurb", "Which words make one place sound different from the rest?"))
ui.auto_ran(PAGE)
ui.learn_page(
    PAGE,
    code=(
        "from sklearn.feature_extraction.text import CountVectorizer\n"
        "import numpy as np\n\n"
        "vec = CountVectorizer(ngram_range=(1, 2)).fit(all_docs)\n"
        "ya = np.asarray(vec.transform(docs_a).sum(0)).ravel()   # counts in place A\n"
        "yb = np.asarray(vec.transform(docs_b).sum(0)).ravel()   # counts in the rest\n"
        "yp = np.asarray(vec.transform(all_docs).sum(0)).ravel() # background\n"
        "alpha = yp * 500 / yp.sum()                             # informative prior\n"
        "a0, na, nb = alpha.sum(), ya.sum(), yb.sum()\n"
        "pa, pb = ya + alpha, yb + alpha\n"
        "delta = np.log(pa / (na + a0 - pa)) - np.log(pb / (nb + a0 - pb))\n"
        "z = delta / np.sqrt(1 / pa + 1 / pb)    # z > 0: more typical of A"
    ),
)

if not places.has_geo():
    ui.locked(T("ch2.locked", "This step needs a text column and longitude/latitude columns."),
              "p1_data", T("ch2.locked_link", "Go to Data"))

p = places.params()
labels = places.active_places()
counts = labels[labels != ""].value_counts() if labels is not None else None
if counts is None or len(counts) < 2:
    ui.info(T("ch2.few_places", "Fewer than two places were found, so there is nothing to compare."))
    ui.page_done(PAGE)
    ui.track_footer(PAGE)
    st.stop()

PLACES = counts.index.tolist()           # largest first
REST = ""                                 # sentinel: "all other places"
cat = viz.categorical(ui.palette(), 2)
sw_custom, sw_tl = salita.stopword_key()


@st.fragment
def _compare():
    c1, c2 = st.columns(2)
    a = c1.selectbox(T("p4_apart.place_a", "Place A"), PLACES, index=0,
                     format_func=lambda x: f"{x} ({counts[x]:,})", key="p4_a")
    others = [REST] + [x for x in PLACES if x != a]
    b = c2.selectbox(T("p4_apart.place_b", "Compare with"), others, index=0, key="p4_b",
                     format_func=lambda x: (T("p4_apart.rest", "All other places") if x == REST
                                            else f"{x} ({counts[x]:,})"))
    c3, c4 = st.columns(2)
    # A floor of 5 keeps a term from describing one or two people.
    min_count = c3.slider(T("p4_apart.min_count", "Minimum times a term must appear"),
                          5, 100, 10, 5, key="p4_min")
    hide = c4.checkbox(T("p4_apart.hide_places", "Hide place names"), value=True, key="p4_hide",
                       help=T("p4_apart.hide_help",
                              "Place names separate places trivially. Hide them to see what people say."))

    key = (p["source_key"], p["text_col"], sw_custom, sw_tl, p["lon_col"], p["lat_col"],
           p["km"], p["mode"], p["unit"], p["eps_m"], p["min_samples"], a, b)
    with audio.result(tracks.SIGNATURE[PAGE], key + (min_count, hide)):
        table = salita.logodds_for(*key)
    table = table[(table["count_a"] + table["count_b"]) >= min_count]
    if hide:
        table = salita.drop_place_terms(table, p["source_key"], p["text_col"])
    if table.empty:
        ui.info(T("p4_apart.none", "No terms pass the minimum count. Lower it to see more."))
        return

    top_a = table[table["z"] > 0].head(15)                      # largest positive z: typical of A
    top_b = table[table["z"] < 0].tail(15)                      # most negative z: typical of B
    rows = sorted(list(top_a.itertuples()) + list(top_b.itertuples()), key=lambda r: r.z)
    name_b = T("p4_apart.rest", "All other places") if b == REST else b
    fig = go.Figure(go.Bar(
        x=[r.z for r in rows], y=[r.term for r in rows], orientation="h",
        marker_color=[cat[1] if r.z > 0 else cat[0] for r in rows],
        customdata=[[r.count_a, r.count_b] for r in rows],
        hovertemplate="%{y}<br>z = %{x:.1f}<br>A: %{customdata[0]}, B: %{customdata[1]}<extra></extra>"))
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"],
                      height=140 + 22 * len(rows), margin=dict(l=10, r=10, t=30, b=40),
                      showlegend=False, yaxis_title="",
                      xaxis_title=T("p4_apart.axis", "z-score (distinctiveness)"))
    fig.add_annotation(x=0.0, y=1.07, xref="paper", yref="paper", showarrow=False, xanchor="left",
                       text=f"<b style='color:{cat[0]}'>◀ {T('p4_apart.more_typical', 'more typical of')} {name_b}</b>")
    fig.add_annotation(x=1.0, y=1.07, xref="paper", yref="paper", showarrow=False, xanchor="right",
                       text=f"<b style='color:{cat[1]}'>{T('p4_apart.more_typical', 'more typical of')} {a} ▶</b>")
    st.plotly_chart(fig, width="stretch")
    st.caption(T("p4_apart.caption", "Terms are single words and two-word phrases; counts are across all comments."))


_compare()
ui.page_done(PAGE)
ui.track_footer(PAGE)
