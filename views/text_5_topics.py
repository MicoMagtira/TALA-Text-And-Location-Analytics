import numpy as np
import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import nlp, preprocess, ui, viz

ui.page_title("Text Analytics", "Topic Modeling (LDA)",
              "Latent Dirichlet Allocation extracts hidden themes as word "
              "distributions, with representative quotes and a stability check.")

texts = dl.text_series().tolist()
sw = ui.stopwords()
corpus = tuple(preprocess.clean_corpus(texts, sw))

c1, c2, c3 = st.columns(3)
k = c1.slider("Number of topics", 2, 12, 5)
n_words = c2.slider("Words per topic", 5, 15, 10)
seed = c3.number_input("Random seed", 0, 9999, 42)

res = nlp.lda_topics(corpus, k, n_words, int(seed))
if res is None:
    st.info("Not enough documents to fit LDA at this setting.")
    st.stop()

colors = viz.categorical(ui.palette(), k)
cols = st.columns(2)
for t in res["topics"]:
    with cols[t["topic"] % 2]:
        st.markdown(f"**Topic {t['topic'] + 1}**")
        df = {"word": t["words"][::-1], "weight": t["weights"][::-1]}
        fig = px.bar(df, x="weight", y="word", orientation="h",
                     color_discrete_sequence=[colors[t["topic"]]])
        fig.update_layout(**viz.plotly_template(ui.palette())["layout"],
                          height=30 * n_words + 60, yaxis_title="",
                          xaxis_title="", showlegend=False,
                          margin=dict(l=10, r=10, t=10, b=20))
        st.plotly_chart(fig, use_container_width=True)

st.markdown("#### Representative quotes")
sel = st.selectbox("Show top quotes for", [f"Topic {i + 1}" for i in range(k)])
ti = int(sel.split()[-1]) - 1
doc_topic = res["doc_topic"]
order = doc_topic[:, ti].argsort()[::-1][:5]
for rank, di in enumerate(order, 1):
    st.markdown(f"> **{rank}.** ({doc_topic[di, ti]:.2f}) {texts[di]}")

st.markdown("---")
st.markdown("#### Topic stability")
st.caption("LDA is stochastic. We re-fit under different random seeds and measure "
           "how consistently the same topics reappear (higher = more stable).")
if st.button("Run stability check (3 seeds)"):
    with st.spinner("Re-fitting LDA under multiple seeds…"):
        stab = nlp.topic_stability(corpus, k, (0, 1, 2))
    if stab.empty:
        st.info("Could not compute stability for this corpus.")
    else:
        st.dataframe(stab, use_container_width=True)
        st.metric("Mean Jaccard (topic overlap)", f"{stab['mean_jaccard'].mean():.2f}")

ui.learn(
    "LDA & topic stability",
    "**LDA** treats each document as a mixture of topics and each topic as a "
    "distribution over words. We fit it on a `CountVectorizer` bag-of-words and read "
    "the top-weighted words per topic. Because LDA is initialized randomly, we assess "
    "**stability** by re-fitting with different seeds and comparing topic word-sets "
    "with **Jaccard** and **cosine** similarity — unstable topics shift between runs.",
    code=(
        "from sklearn.decomposition import LatentDirichletAllocation\n"
        "from sklearn.feature_extraction.text import CountVectorizer\n\n"
        "X = CountVectorizer(min_df=3, max_df=0.9).fit_transform(cleaned_docs)\n"
        "lda = LatentDirichletAllocation(n_components=5, random_state=42)\n"
        "doc_topic = lda.fit_transform(X)          # per-doc topic mix\n"
        "top = lda.components_.argsort(axis=1)[:, ::-1][:, :10]  # top words"
    ),
)
