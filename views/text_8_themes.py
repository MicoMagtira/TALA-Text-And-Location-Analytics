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
    "This page runs the notebook's clustering workflow end to end, and the result "
    "contains a mistake worth more than the method itself. Look at the themes before "
    "reading on.\n\n"
    "**How the two pieces fit.** TF-IDF weights each term by how often it appears in a "
    "comment (TF) against how rare it is across all comments (IDF), so words everywhere "
    "get crushed and words that distinguish a comment get amplified. K-Means then groups "
    "comments that are near each other in that weighted space. TF-IDF decides what "
    "\"similar\" means; K-Means only obeys it.\n\n"
    "**What K=4 finds here.** Themes of 2,719 / 1,131 / 1,316 / 6,834 comments. Three "
    "are recognisable service concerns — waiting times, staff conduct, general "
    "experience. One is not. Its top terms are `del`, `del norte`, `del sur`, `norte`, "
    "`sur`, `surigao`.\n\n"
    "**That cluster is geography, not a theme.** Nothing malfunctioned. Province names "
    "are rare across the corpus, so IDF scored them as highly distinctive, and K-Means "
    "faithfully grouped every comment mentioning a `del`-province together. The "
    "algorithm did exactly what it was asked. The question it answered was simply not "
    "the question anyone wanted asked. This is the most common failure in applied "
    "clustering and it never raises an error — a cluster is always returned, and it "
    "always looks like a finding.\n\n"
    "**What to do about it.** Add place names to the sidebar's custom stopwords and "
    "re-run: the geographic cluster dissolves and a real theme usually takes its place. "
    "Then note that you did it. \"We excluded toponyms because they clustered on "
    "location rather than content\" is a legitimate, reportable analytical decision.\n\n"
    "**Reading the scatter.** The map is a 2-D projection of a 1,200-dimension space, so "
    "most of the separation is not on your screen. Points that look adjacent may be far "
    "apart. Use it to spot a cluster that is obviously smeared or split — never as "
    "evidence that themes are cleanly separated. And name every theme from the sample "
    "comments, not the keyword list, precisely because the keyword list is what fooled "
    "us above.",
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
