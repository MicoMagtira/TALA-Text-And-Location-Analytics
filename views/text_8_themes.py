import pandas as pd
import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import i18n, nlp, preprocess, ui, viz

PAGE = "text_8_themes"

ui.page_header(PAGE, "text")
ui.learn_page(
    PAGE,
    code=(
        "from sklearn.cluster import KMeans\n"
        "from sklearn.decomposition import TruncatedSVD\n"
        "from sklearn.feature_extraction.text import TfidfVectorizer\n\n"
        "X = TfidfVectorizer(ngram_range=(1, 2), min_df=3,\n"
        "                    max_features=1200).fit_transform(cleaned_docs)\n"
        "labels = KMeans(n_clusters=4, n_init=10, random_state=42).fit_predict(X)\n"
        "coords = TruncatedSVD(n_components=2, random_state=42).fit_transform(X)"
    ),
)

texts = dl.text_series().tolist()
sw = ui.stopwords()
corpus = tuple(preprocess.clean_corpus(texts, sw))

k = st.slider(i18n.t("text_8_themes.k"), 2, 10, 4)
res = nlp.tfidf_kmeans(corpus, k)
if res is None:
    st.info(i18n.t("text_8_themes.not_enough"))
    st.stop()

colors = viz.categorical(ui.palette(), k)
labels = res["labels"]
theme_name = lambda i: i18n.t("text_8_themes.theme", n=i + 1)

c1, c2 = st.columns([1.2, 1])
with c1:
    st.markdown(i18n.t("text_8_themes.map_head"))
    coords = res["coords"]
    sdf = pd.DataFrame({"x": coords[:, 0], "y": coords[:, 1],
                        "theme": [theme_name(l) for l in labels]})
    fig = px.scatter(sdf.sample(min(len(sdf), 3000), random_state=1),
                     x="x", y="y", color="theme",
                     color_discrete_sequence=colors, opacity=0.6,
                     category_orders={"theme": [theme_name(i) for i in range(k)]})
    fig.update_traces(marker=dict(size=6, line=dict(width=0.5, color="white")))
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=500,
                      xaxis_title="PC 1", yaxis_title="PC 2")
    st.plotly_chart(fig, width="stretch")
with c2:
    st.markdown(i18n.t("text_8_themes.sizes_head"))
    sizes = res["sizes"]
    sz = pd.DataFrame({"theme": [theme_name(i) for i in sizes.index],
                       "count": sizes.values})
    fig = px.bar(sz, x="count", y="theme", orientation="h", text="count",
                 color="theme", color_discrete_sequence=colors)
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=500,
                      showlegend=False, yaxis_title="",
                      xaxis_title=i18n.t("text_8_themes.axis_comments"))
    st.plotly_chart(fig, width="stretch")

st.markdown(i18n.t("text_8_themes.terms_head"))
for c in range(k):
    st.markdown(i18n.t("text_8_themes.theme_terms", n=c + 1,
                       terms=", ".join(res["top_terms"][c])))

st.markdown("---")
st.markdown(i18n.t("text_8_themes.cross_head"))
sent = nlp.vader_sentiment(tuple(texts))
# align lengths (kmeans docs dropped empties): use min length
m = min(len(labels), len(sent))
cross = pd.crosstab(
    pd.Series([theme_name(l) for l in labels[:m]], name="theme"),
    sent["label"].iloc[:m])
for col in ["positive", "neutral", "negative"]:
    if col not in cross.columns:
        cross[col] = 0
cross = cross[["positive", "neutral", "negative"]]
melted = cross.reset_index().melt(id_vars="theme", var_name="sentiment",
                                  value_name="count")
melted["shown"] = melted["sentiment"].map(lambda s: i18n.t(f"sent.{s}"))
fig = px.bar(melted, x="count", y="theme", color="shown", orientation="h",
             color_discrete_map={i18n.t("sent.positive"): "#008300",
                                 i18n.t("sent.neutral"): viz.INK_MUTED,
                                 i18n.t("sent.negative"): "#e34948"})
fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=90 + 55 * k,
                  barmode="stack", yaxis_title="",
                  xaxis_title=i18n.t("text_8_themes.axis_comments"))
st.plotly_chart(fig, width="stretch")
