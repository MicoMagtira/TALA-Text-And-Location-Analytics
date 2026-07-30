import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import nlp, preprocess, ui, viz

ui.page_title("Text Analytics", "N-grams & Networks",
              "Frequent two- and three-word phrases, and a co-occurrence network "
              "that shows which words travel together.")

texts = dl.text_series().tolist()
sw = ui.stopwords()
corpus = tuple(preprocess.clean_corpus(texts, sw))

c0, c1, c2 = st.columns(3)
n = c0.selectbox("N-gram size", [2, 3], format_func=lambda x: f"{x}-gram")
top_n = c1.slider("Top phrases", 10, 40, 20, 5)
min_df = c2.slider("Min. document frequency", 1, 10, 2)

ng = nlp.top_ngrams(corpus, (n, n), top_n, min_df)
if ng.empty:
    st.info("No n-grams at this setting — try lowering the minimum document frequency.")
else:
    fig = px.bar(ng.sort_values("count"), x="count", y="ngram", orientation="h",
                 text="count", color_discrete_sequence=[viz.NU_NAVY])
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"],
                      height=26 * len(ng) + 80, yaxis_title="",
                      xaxis_title="frequency", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    st.download_button("⬇️ Download n-grams (CSV)", ng.to_csv(index=False),
                       f"tala_{n}grams.csv", "text/csv")

st.markdown("---")
st.markdown("#### Bigram co-occurrence network")
edges = nlp.top_ngrams(corpus, (2, 2), 40, min_df)
if edges.empty:
    st.info("Not enough bigrams to draw a network.")
else:
    G = nx.Graph()
    for _, row in edges.iterrows():
        parts = row["ngram"].split()
        if len(parts) == 2:
            G.add_edge(parts[0], parts[1], weight=int(row["count"]))
    if G.number_of_edges() == 0:
        st.info("No connected bigrams to display.")
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
            hovertext=[f"{n_} · degree {deg[n_]}" for n_ in G.nodes()],
            hoverinfo="text")
        fig = go.Figure([edge_trace, node_trace])
        fig.update_layout(height=560, showlegend=False,
                          paper_bgcolor=viz.SURFACE, plot_bgcolor=viz.SURFACE,
                          margin=dict(l=10, r=10, t=10, b=10),
                          xaxis=dict(visible=False), yaxis=dict(visible=False))
        st.plotly_chart(fig, use_container_width=True)

ui.learn(
    "N-grams & co-occurrence",
    "An **n-gram** is a contiguous run of *n* words; `CountVectorizer` with "
    "`ngram_range=(n, n)` counts them across the corpus. The **network** turns the "
    "top bigrams into a graph — each word is a node, each bigram an edge weighted by "
    "how often the pair appears — so recurring phrase structures become visible.",
    code=(
        "from sklearn.feature_extraction.text import CountVectorizer\n"
        "vec = CountVectorizer(ngram_range=(2, 2), min_df=2)\n"
        "X = vec.fit_transform(cleaned_docs)\n"
        "counts = X.sum(axis=0).A1  # per-bigram totals\n\n"
        "import networkx as nx\n"
        "G = nx.Graph()\n"
        "for bigram, c in zip(vec.get_feature_names_out(), counts):\n"
        "    w1, w2 = bigram.split()\n"
        "    G.add_edge(w1, w2, weight=c)"
    ),
)
