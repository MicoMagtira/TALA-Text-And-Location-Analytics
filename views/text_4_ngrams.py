import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import i18n, nlp, preprocess, ui, viz

PAGE = "text_4_ngrams"

ui.page_header(PAGE, "text")
ui.learn_page(
    PAGE,
    code=(
        "from sklearn.feature_extraction.text import CountVectorizer\n\n"
        "vec = CountVectorizer(ngram_range=(2, 2), min_df=2)\n"
        "X = vec.fit_transform(cleaned_docs)\n"
        "counts = X.sum(axis=0).A1\n"
        "terms = vec.get_feature_names_out()\n"
        "top = sorted(zip(terms, counts), key=lambda kv: -kv[1])[:20]"
    ),
)

texts = dl.text_series().tolist()
sw = ui.stopwords()
corpus = tuple(preprocess.clean_corpus(texts, sw))

c0, c1, c2 = st.columns(3)
n = c0.selectbox(i18n.t("text_4_ngrams.size"), [2, 3],
                 format_func=lambda x: i18n.t("text_4_ngrams.size_fmt", n=x))
top_n = c1.slider(i18n.t("text_4_ngrams.top_n"), 10, 40, 20, 5)
min_df = c2.slider(i18n.t("text_4_ngrams.min_df"), 1, 10, 2)

ng = nlp.top_ngrams(corpus, (n, n), top_n, min_df)
if ng.empty:
    st.info(i18n.t("text_4_ngrams.none"))
else:
    fig = px.bar(ng.sort_values("count"), x="count", y="ngram", orientation="h",
                 text="count", color_discrete_sequence=[viz.NU_NAVY])
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"],
                      height=26 * len(ng) + 80, yaxis_title="",
                      xaxis_title=i18n.t("text_4_ngrams.axis_freq"),
                      showlegend=False)
    st.plotly_chart(fig, width="stretch")
    st.download_button(i18n.t("text_4_ngrams.dl"), ng.to_csv(index=False),
                       f"tala_{n}grams.csv", "text/csv")

st.markdown("---")
st.markdown(i18n.t("text_4_ngrams.net_head"))
edges = nlp.top_ngrams(corpus, (2, 2), 40, min_df)
if edges.empty:
    st.info(i18n.t("text_4_ngrams.no_bigrams"))
else:
    G = nx.Graph()
    for _, row in edges.iterrows():
        parts = row["ngram"].split()
        if len(parts) == 2:
            G.add_edge(parts[0], parts[1], weight=int(row["count"]))
    if G.number_of_edges() == 0:
        st.info(i18n.t("text_4_ngrams.no_connected"))
    else:
        pos = nx.spring_layout(G, seed=42, k=0.6)
        ex, ey = [], []
        for a, b in G.edges():
            ex += [pos[a][0], pos[b][0], None]
            ey += [pos[a][1], pos[b][1], None]
        edge_trace = go.Scatter(x=ex, y=ey, mode="lines",
                                line=dict(width=1, color="#c9cee8"), hoverinfo="none")
        deg = dict(G.degree())
        node_trace = go.Scatter(
            x=[pos[n_][0] for n_ in G.nodes()],
            y=[pos[n_][1] for n_ in G.nodes()],
            mode="markers+text", text=list(G.nodes()), textposition="top center",
            textfont=dict(size=11, color=viz.INK_SECONDARY),
            marker=dict(size=[8 + 3 * deg[n_] for n_ in G.nodes()],
                        color=viz.NU_NAVY, line=dict(width=1, color="white")),
            hovertext=[i18n.t("text_4_ngrams.degree", word=n_, n=deg[n_])
                       for n_ in G.nodes()],
            hoverinfo="text")
        fig = go.Figure([edge_trace, node_trace])
        fig.update_layout(height=560, showlegend=False,
                          paper_bgcolor=viz.SURFACE, plot_bgcolor=viz.SURFACE,
                          margin=dict(l=10, r=10, t=10, b=10),
                          xaxis=dict(visible=False), yaxis=dict(visible=False))
        st.plotly_chart(fig, width="stretch")
