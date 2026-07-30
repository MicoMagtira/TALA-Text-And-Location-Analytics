import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import nlp, preprocess, ui, viz

ui.page_title("Text Analytics", "Keywords & Nouns",
              "RAKE keyword extraction, noun / proper-noun ranking (spaCy POS), and "
              "a term co-occurrence heatmap.")

texts = dl.text_series().tolist()
sw = ui.stopwords()

tab_rake, tab_nouns, tab_co = st.tabs(["🔑 RAKE keywords", "🏷️ Nouns & proper nouns",
                                       "🔥 Co-occurrence heatmap"])

with tab_rake:
    top_n = st.slider("Keywords", 10, 40, 25, 5, key="rake_n")
    rk = nlp.rake_keywords(tuple(texts[:5000]), top_n)
    if rk.empty:
        st.info("RAKE requires `rake-nltk` (and NLTK data). Install it to enable this.")
    else:
        fig = px.bar(rk.sort_values("score"), x="score", y="keyword",
                     orientation="h", color_discrete_sequence=[viz.NU_NAVY])
        fig.update_layout(**viz.plotly_template(ui.palette())["layout"],
                          height=26 * len(rk) + 80, yaxis_title="",
                          xaxis_title="RAKE score", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("⬇️ Keywords (CSV)", rk.to_csv(index=False),
                           "tala_keywords.csv", "text/csv")

with tab_nouns:
    if not nlp.spacy_available():
        st.info("Noun extraction needs the spaCy model `en_core_web_sm`. Install it "
                "with `python -m spacy download en_core_web_sm`.")
    else:
        nouns, proper = nlp.extract_nouns(tuple(texts))
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Common nouns**")
            fig = px.bar(nouns.sort_values("count"), x="count", y="noun",
                         orientation="h", color_discrete_sequence=[viz.NU_NAVY])
            fig.update_layout(**viz.plotly_template(ui.palette())["layout"],
                              height=26 * len(nouns) + 80, yaxis_title="",
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown("**Proper nouns**")
            fig = px.bar(proper.sort_values("count"), x="count", y="proper_noun",
                         orientation="h", color_discrete_sequence=[viz.NU_GOLD_DEEP])
            fig.update_layout(**viz.plotly_template(ui.palette())["layout"],
                              height=26 * len(proper) + 80, yaxis_title="",
                              showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        st.caption("Computed on a sample of up to 4,000 comments for responsiveness.")

with tab_co:
    corpus = tuple(preprocess.clean_corpus(texts, sw))
    n_terms = st.slider("Terms in matrix", 8, 25, 15, key="co_n")
    co = nlp.cooccurrence(corpus, n_terms)
    if co.empty:
        st.info("Not enough shared terms to build a co-occurrence matrix.")
    else:
        fig = px.imshow(co, color_continuous_scale="Blues", aspect="auto",
                        labels=dict(color="co-occurrences"))
        fig.update_layout(height=560, paper_bgcolor=viz.SURFACE,
                          font=dict(color=viz.INK_SECONDARY),
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

ui.learn(
    "RAKE, POS tagging & co-occurrence",
    "**RAKE** (Rapid Automatic Keyword Extraction) scores candidate phrases by word "
    "frequency and degree of co-occurrence, favoring multi-word terms. **spaCy** POS "
    "tagging labels each token so we can rank `NOUN` (common) and `PROPN` (proper) "
    "words separately. The **co-occurrence** matrix counts how often two terms appear "
    "in the same comment (binary per document), revealing associated concepts.",
    code=(
        "from rake_nltk import Rake\n"
        "r = Rake(); r.extract_keywords_from_text(corpus_text)\n"
        "ranked = r.get_ranked_phrases_with_scores()\n\n"
        "import spacy\n"
        "nlp = spacy.load('en_core_web_sm')\n"
        "nouns = [t.lemma_ for d in nlp.pipe(texts) for t in d if t.pos_ == 'NOUN']"
    ),
)
