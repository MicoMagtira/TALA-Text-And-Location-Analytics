import pandas as pd
import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import nlp, preprocess, ui, viz

ui.page_title("Text Analytics", "Themes (TF-IDF K-Means)",
              "Group comments into themes with TF-IDF + K-Means, view them in 2-D "
              "(PCA), read the top terms per theme, and cross-tab against sentiment.")

ui.learn(
    "TF-IDF + K-Means themes (from NLP.ipynb)",
    "**TF-IDF** gives more weight to terms that distinguish one comment from the rest; "
    "**K-Means** then groups comments that are similar in that weighted space. The top "
    "terms are clues for naming each cluster, while the PCA map is only a two-dimensional "
    "projection for exploration—not proof that themes are cleanly separated.\n\n"
    "Try several values of K. A useful solution has readable top terms, enough examples "
    "to inspect, and a purpose that fits the research question. Name themes after reading "
    "sample comments, not from keywords alone. The sentiment cross-tab is descriptive: it "
    "can guide follow-up questions but cannot establish why a theme has a given tone.",
    code=(
        "from sklearn.feature_extraction.text import TfidfVectorizer\n"
        "from sklearn.cluster import KMeans\n\n"
        "X = TfidfVectorizer(ngram_range=(1,2), max_df=0.9, min_df=3,\n"
        "                    max_features=1200).fit_transform(cleaned_docs)\n"
        "km = KMeans(n_clusters=4, n_init=10, random_state=42).fit(X)\n"
        "order = km.cluster_centers_.argsort()[:, ::-1]  # top terms per cluster"
    ),
)

texts = dl.text_series().tolist()
sw = ui.stopwords()
corpus = tuple(preprocess.clean_corpus(texts, sw))

k = st.slider("Number of themes (K)", 2, 10, 4)
res = nlp.tfidf_kmeans(corpus, k)
if res is None:
    st.info("Not enough documents to cluster at this setting.")
    st.stop()

colors = viz.categorical(ui.palette(), k)
labels = res["labels"]

c1, c2 = st.columns([1.2, 1])
with c1:
    st.markdown("#### Theme map (PCA projection)")
    coords = res["coords"]
    sdf = pd.DataFrame({"x": coords[:, 0], "y": coords[:, 1],
                        "theme": [f"Theme {l + 1}" for l in labels]})
    fig = px.scatter(sdf.sample(min(len(sdf), 3000), random_state=1),
                     x="x", y="y", color="theme",
                     color_discrete_sequence=colors, opacity=0.6,
                     category_orders={"theme": [f"Theme {i + 1}" for i in range(k)]})
    fig.update_traces(marker=dict(size=6, line=dict(width=0.5, color="white")))
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=500,
                      xaxis_title="PC 1", yaxis_title="PC 2")
    st.plotly_chart(fig, width="stretch")
with c2:
    st.markdown("#### Theme sizes")
    sizes = res["sizes"]
    sz = pd.DataFrame({"theme": [f"Theme {i + 1}" for i in sizes.index],
                       "count": sizes.values})
    fig = px.bar(sz, x="count", y="theme", orientation="h", text="count",
                 color="theme", color_discrete_sequence=colors)
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=500,
                      showlegend=False, yaxis_title="", xaxis_title="comments")
    st.plotly_chart(fig, width="stretch")

st.markdown("#### Top terms per theme")
for c in range(k):
    st.markdown(f"**Theme {c + 1}** — {', '.join(res['top_terms'][c])}")

st.markdown("---")
st.markdown("#### Theme × sentiment")
sent = nlp.vader_sentiment(tuple(texts))
# align lengths (kmeans docs dropped empties): use min length
m = min(len(labels), len(sent))
cross = pd.crosstab(
    pd.Series([f"Theme {l + 1}" for l in labels[:m]], name="theme"),
    sent["label"].iloc[:m])
for col in ["positive", "neutral", "negative"]:
    if col not in cross.columns:
        cross[col] = 0
cross = cross[["positive", "neutral", "negative"]]
fig = px.bar(cross.reset_index().melt(id_vars="theme", var_name="sentiment",
                                      value_name="count"),
             x="count", y="theme", color="sentiment", orientation="h",
             color_discrete_map={"positive": "#008300", "neutral": viz.INK_MUTED,
                                 "negative": "#e34948"})
fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=90 + 55 * k,
                  barmode="stack", yaxis_title="", xaxis_title="comments")
st.plotly_chart(fig, width="stretch")
