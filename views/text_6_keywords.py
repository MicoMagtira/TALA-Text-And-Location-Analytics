import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import i18n, nlp, preprocess, ui, viz

PAGE = "text_6_keywords"

ui.page_header(PAGE, "text")
ui.learn_page(
    PAGE,
    code=(
        "from rake_nltk import Rake\n"
        "import nltk\n\n"
        "r = Rake()\n"
        "r.extract_keywords_from_text(' . '.join(texts))\n"
        "ranked = r.get_ranked_phrases_with_scores()[:25]\n\n"
        "tags = nltk.pos_tag(nltk.tokenize.TreebankWordTokenizer().tokenize(sent))\n"
        "nouns = [w for w, t in tags if t.startswith('NN')]"
    ),
)

texts = dl.text_series().tolist()
sw = ui.stopwords()

tab_rake, tab_nouns, tab_co = st.tabs([
    i18n.t("text_6_keywords.tab_rake"),
    i18n.t("text_6_keywords.tab_nouns"),
    i18n.t("text_6_keywords.tab_co"),
])

with tab_rake:
    top_n = st.slider(i18n.t("text_6_keywords.kw_n"), 10, 40, 25, 5, key="rake_n")
    rk = nlp.rake_keywords(tuple(texts[:5000]), top_n)
    if rk.empty:
        st.info(i18n.t("text_6_keywords.rake_missing"))
    else:
        fig = px.bar(rk.sort_values("score"), x="score", y="keyword",
                     orientation="h", color_discrete_sequence=[viz.NU_NAVY])
        fig.update_layout(**viz.plotly_template(ui.palette())["layout"],
                          height=26 * len(rk) + 80, yaxis_title="",
                          xaxis_title=i18n.t("text_6_keywords.axis_rake"),
                          showlegend=False)
        st.plotly_chart(fig, width="stretch")
        st.download_button(i18n.t("text_6_keywords.dl"), rk.to_csv(index=False),
                           "tala_keywords.csv", "text/csv")

with tab_nouns:
    if not nlp.pos_available():
        st.info(i18n.t("text_6_keywords.nltk_missing"))
    else:
        nouns, proper = nlp.extract_nouns(tuple(texts))
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(i18n.t("text_6_keywords.common_nouns"))
            fig = px.bar(nouns.sort_values("count"), x="count", y="noun",
                         orientation="h", color_discrete_sequence=[viz.NU_NAVY])
            fig.update_layout(**viz.plotly_template(ui.palette())["layout"],
                              height=26 * len(nouns) + 80, yaxis_title="",
                              showlegend=False)
            st.plotly_chart(fig, width="stretch")
        with c2:
            st.markdown(i18n.t("text_6_keywords.proper_nouns"))
            fig = px.bar(proper.sort_values("count"), x="count", y="proper_noun",
                         orientation="h", color_discrete_sequence=[viz.NU_GOLD_DEEP])
            fig.update_layout(**viz.plotly_template(ui.palette())["layout"],
                              height=26 * len(proper) + 80, yaxis_title="",
                              showlegend=False)
            st.plotly_chart(fig, width="stretch")
        st.caption(i18n.t("text_6_keywords.sample_caption"))

with tab_co:
    corpus = tuple(preprocess.clean_corpus(texts, sw))
    n_terms = st.slider(i18n.t("text_6_keywords.terms"), 8, 25, 15, key="co_n")
    co = nlp.cooccurrence(corpus, n_terms)
    if co.empty:
        st.info(i18n.t("text_6_keywords.co_none"))
    else:
        fig = px.imshow(co, color_continuous_scale="Blues", aspect="auto",
                        labels=dict(color=i18n.t("text_6_keywords.co_legend")))
        fig.update_layout(height=560, paper_bgcolor=viz.SURFACE,
                          font=dict(color=viz.INK_SECONDARY),
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, width="stretch")
