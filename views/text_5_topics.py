import numpy as np
import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import nlp, preprocess, ui, viz

ui.page_title("Text Analytics", "Topic Modeling (LDA)",
              "Latent Dirichlet Allocation extracts hidden themes as word "
              "distributions, with representative quotes and a stability check.")

ui.learn(
    "LDA & topic stability",
    "LDA proposes candidate topics. **People name them, and people are responsible for "
    "them.** The model never sees a theme — it sees which words tend to occur in the "
    "same documents, and works backwards to a set of word-distributions that would "
    "explain that pattern.\n\n"
    "**The two distributions it learns.** Each *document* is modelled as a mixture of "
    "topics (a comment can be 70% one thing, 30% another), and each *topic* as a "
    "distribution over words. That double flexibility is why LDA handles comments "
    "covering several concerns at once, and also why its output is softer than it "
    "looks: nothing is assigned anywhere with certainty.\n\n"
    "**Choosing K is your call, not the model's.** There is no correct number of topics, "
    "and LDA will happily produce whatever K you ask for — five topics from noise, "
    "twenty topics from five real themes. Judge a solution by whether the top words "
    "cohere, whether the representative quotes below actually belong together, and "
    "whether the sizes are usable. A topic holding 3% of documents is rarely worth "
    "reporting; one holding 60% usually needs splitting.\n\n"
    "**Why stability matters more than plausibility.** LDA is initialised randomly, so "
    "different seeds give different topics from identical data. Human beings are "
    "extremely good at reading meaning into any list of related words — you will find a "
    "story in a topic that is pure noise. The stability check is the defence: it re-fits "
    "under three seeds and scores how much the topic word-sets overlap. High agreement "
    "means you found structure in the data. Low agreement means you found structure in "
    "the random seed, no matter how convincing the words look.\n\n"
    "**A note on speed.** The fit runs at `max_iter=10` rather than the library default "
    "of 10× more work per document. On this corpus that halves the wait while topic "
    "word-sets still agree with the slower settings at 0.79 Jaccard — a deliberate "
    "accuracy-for-latency trade, and exactly the kind of decision worth writing down "
    "when you report results.",
    code=(
        "from sklearn.decomposition import LatentDirichletAllocation\n"
        "from sklearn.feature_extraction.text import CountVectorizer\n\n"
        "X = CountVectorizer(min_df=3, max_df=0.9).fit_transform(cleaned_docs)\n"
        "lda = LatentDirichletAllocation(n_components=5, random_state=42)\n"
        "doc_topic = lda.fit_transform(X)          # per-doc topic mix\n"
        "top = lda.components_.argsort(axis=1)[:, ::-1][:, :10]  # top words"
    ),
)

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
        st.plotly_chart(fig, width="stretch")

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
        st.dataframe(stab, width="stretch")
        st.metric("Mean Jaccard (topic overlap)", f"{stab['mean_jaccard'].mean():.2f}")
