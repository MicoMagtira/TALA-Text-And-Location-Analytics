"""Step 7 (p7_themes): what they talk about.

TF-IDF + K-Means themes over the cleaned comments, then how much of each place's
conversation each theme takes up. Place names are hidden by default: left in, one
"theme" is just province names (the lesson of the original themes page).
"""
import plotly.graph_objects as go
import streamlit as st

from core import audio, compare, i18n, maps, places, tracks, ui, viz
from core import data_loader as dl

PAGE = "p7_themes"
T = ui._t
TOP_PLACES = 10
ASPECT_DEFAULT = {"waiting": "Waiting", "staff": "Staff", "cost": "Cost",
                  "medicine": "Medicine", "facilities": "Facilities", "access": "Access"}

dl.ensure_loaded()
ui.page_header(PAGE, "what")
if i18n.t(f"{PAGE}.blurb") == f"{PAGE}.blurb":
    st.markdown(T(f"{PAGE}.blurb", "What topics come up in the comments, and which places talk about which?"))
ui.auto_ran(PAGE)
ui.learn_page(
    PAGE,
    code=(
        "from sklearn.cluster import KMeans\n"
        "from sklearn.feature_extraction.text import TfidfVectorizer\n"
        "from sklearn.metrics import silhouette_score\n\n"
        "X = TfidfVectorizer(ngram_range=(1, 2), max_df=0.9, min_df=3,\n"
        "                    max_features=1200).fit_transform(cleaned_docs)\n"
        "labels = KMeans(n_clusters=4, n_init=10, random_state=42).fit_predict(X)\n"
        "print(silhouette_score(X, labels, metric='cosine', sample_size=2000))\n\n"
        "# share of each theme inside each place (rows sum to 100%)\n"
        "pd.crosstab(df.place, labels, normalize='index')"
    ),
)

if not places.has_geo():
    ui.locked(T("ch2.locked", "This step needs a text column and longitude/latitude columns."),
              "p1_data", T("ch2.locked_link", "Go to Data"))

p = places.params()
labels = places.active_places()
if labels is None or not (labels != "").any():
    ui.info(T("ch2.no_places", "No comments could be assigned to a place."))
    ui.page_done(PAGE)
    ui.track_footer(PAGE)
    st.stop()

sw_custom, sw_tl = maps.stopword_key()
cat = viz.categorical(ui.palette())
asp_names = {a: T(f"asp.{a}", n) for a, n in ASPECT_DEFAULT.items()}


@st.fragment
def _themes():
    c1, c2 = st.columns([2, 1])
    k = c1.slider(T("p7_themes.k", "Number of themes (k)"), 3, 8, 4, key="p7_k")
    drop = c2.checkbox(T("p7_themes.drop_places", "Hide place names"), value=True, key="p7_drop",
                       help=T("p7_themes.drop_help",
                              "Left in, province names form a theme of their own."))
    with audio.result(tracks.SIGNATURE[PAGE], (p["source_key"], p["text_col"], sw_custom, sw_tl, drop, k)):
        res = maps.themes_for(p["source_key"], p["text_col"], sw_custom, sw_tl, drop, k)
    if res is None:
        ui.info(T("p7_themes.not_enough", "Not enough text to find themes."))
        return

    sil = res["silhouette"]
    sizes = res["sizes"]
    total = int(sizes.sum())
    names = maps.theme_names(res["top_terms"], asp_names)
    colors = [cat[i % len(cat)] for i in range(k)]

    sil_txt = f"{sil:.2f}" if sil == sil else "n/a"
    st.metric(T("p7_themes.silhouette", "Silhouette (cluster separation)"), sil_txt,
              help=T("p7_themes.sil_help",
                     "From -1 to 1. Above 0.5 is clearly separated; below 0.25 means themes overlap a lot. Short comments usually score low."))

    # --- theme cards --------------------------------------------------------
    for start in range(0, k, 4):
        cols = st.columns(min(4, k - start))
        for col, i in zip(cols, range(start, k)):
            with col, st.container(border=True):
                st.markdown(f"<span style='color:{colors[i]};font-weight:700'>●</span> **{names[i]}**",
                            unsafe_allow_html=True)
                st.caption(T("p7_themes.card_n", "{n} comments ({pct}%)",
                             n=f"{int(sizes.get(i, 0)):,}", pct=f"{100 * sizes.get(i, 0) / max(total, 1):.0f}"))
                st.write(", ".join(res["top_terms"][i][:6]))

    # --- theme share per place ----------------------------------------------
    st.markdown(f"##### {T('p7_themes.share_head', 'Theme share per place')}")
    share = compare.theme_share(res["labels"], labels.to_numpy(object)) * 100
    top = labels[labels != ""].value_counts().head(TOP_PLACES).index
    share = share.loc[[x for x in top if x in share.index]].iloc[::-1]       # largest place on top
    fig = go.Figure()
    for i in range(k):
        if i in share.columns:
            fig.add_trace(go.Bar(
                y=share.index, x=share[i], name=names[i], orientation="h",
                marker_color=colors[i],
                hovertemplate="%{y}<br>" + names[i] + ": %{x:.0f}%<extra></extra>"))
    layout = viz.plotly_template(ui.palette())["layout"]
    layout["legend"] = {**layout["legend"], "orientation": "h", "y": -0.25}
    fig.update_layout(**layout, barmode="stack",
                      height=150 + 32 * len(share), margin=dict(l=10, r=10, t=10, b=40),
                      yaxis_title="", xaxis_title=T("p7_themes.axis", "% of the place's comments"))
    fig.update_xaxes(range=[0, 100])
    st.plotly_chart(fig, width="stretch")


_themes()
ui.page_done(PAGE)
ui.track_footer(PAGE)
