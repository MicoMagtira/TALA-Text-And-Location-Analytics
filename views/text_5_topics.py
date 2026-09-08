import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import i18n, nlp, preprocess, ui, viz

PAGE = "text_5_topics"

ui.page_header(PAGE, "text")
ui.learn_page(
    PAGE,
    code=(
        "from sklearn.decomposition import LatentDirichletAllocation\n"
        "from sklearn.feature_extraction.text import CountVectorizer\n\n"
        "vec = CountVectorizer(min_df=3, max_df=0.9)\n"
        "X = vec.fit_transform(cleaned_docs)\n"
        "lda = LatentDirichletAllocation(n_components=5, random_state=42,\n"
        "                                learning_method='batch')\n"
        "doc_topic = lda.fit_transform(X)"
    ),
)

texts = dl.text_series().tolist()
sw = ui.stopwords()
corpus = tuple(preprocess.clean_corpus(texts, sw))

c1, c2, c3 = st.columns(3)
k = c1.slider(i18n.t("text_5_topics.k"), 2, 12, 5)
n_words = c2.slider(i18n.t("text_5_topics.n_words"), 5, 15, 10)
seed = c3.number_input(i18n.t("text_5_topics.seed"), 0, 9999, 42)

res = nlp.lda_topics(corpus, k, n_words, int(seed))
if res is None:
    st.info(i18n.t("text_5_topics.not_enough"))
    st.stop()

colors = viz.categorical(ui.palette(), k)
cols = st.columns(2)
for t in res["topics"]:
    with cols[t["topic"] % 2]:
        st.markdown(i18n.t("text_5_topics.topic_bold", n=t["topic"] + 1))
        df = {"word": t["words"][::-1], "weight": t["weights"][::-1]}
        fig = px.bar(df, x="weight", y="word", orientation="h",
                     color_discrete_sequence=[colors[t["topic"]]])
        fig.update_layout(**viz.plotly_template(ui.palette())["layout"],
                          height=30 * n_words + 60, yaxis_title="",
                          xaxis_title="", showlegend=False,
                          margin=dict(l=10, r=10, t=10, b=20))
        st.plotly_chart(fig, width="stretch")

st.markdown(i18n.t("text_5_topics.quotes_head"))
options = [i18n.t("text_5_topics.topic_opt", n=i + 1) for i in range(k)]
sel = st.selectbox(i18n.t("text_5_topics.show_quotes"), options)
ti = options.index(sel)
doc_topic = res["doc_topic"]
order = doc_topic[:, ti].argsort()[::-1][:5]
for rank, di in enumerate(order, 1):
    st.markdown(f"> **{rank}.** ({doc_topic[di, ti]:.2f}) {texts[di]}")

st.markdown("---")
st.markdown(i18n.t("text_5_topics.stab_head"))
st.caption(i18n.t("text_5_topics.stab_caption"))
if st.button(i18n.t("text_5_topics.stab_btn")):
    with st.spinner(i18n.t("text_5_topics.stab_spinner")):
        stab = nlp.topic_stability(corpus, k, (0, 1, 2))
    if stab.empty:
        st.info(i18n.t("text_5_topics.stab_none"))
    else:
        st.dataframe(stab, width="stretch")
        st.metric(i18n.t("text_5_topics.stab_metric"),
                  f"{stab['mean_jaccard'].mean():.2f}")
