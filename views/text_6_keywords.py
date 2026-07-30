import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import nlp, preprocess, ui, viz

ui.page_title("Text Analytics", "Keywords & Nouns",
              "RAKE keyword extraction, noun / proper-noun ranking (NLTK POS), and "
              "a term co-occurrence heatmap.")

ui.learn(
    "RAKE, POS tagging & co-occurrence",
    "Three tabs, three genuinely different questions — worth keeping straight, because "
    "they fail in different ways.\n\n"
    "**RAKE: which phrases stand out?** Rapid Automatic Keyword Extraction splits text at "
    "stopwords and punctuation, treats each surviving run as a candidate phrase, and "
    "scores it by word *degree* divided by word *frequency*. That ratio rewards words "
    "appearing in longer phrases rather than words appearing often — which is why RAKE "
    "surfaces specific multi-word terms that raw counting buries. The side effect: a "
    "phrase said once, if distinctive, can outrank one said five hundred times. RAKE "
    "ranks distinctiveness, never importance.\n\n"
    "**POS tagging: which words are things?** The tagger labels every token, letting us "
    "split common nouns (what people discuss) from proper nouns (where and who). The top "
    "common nouns here are `health` (975), `hospital` (736), `process` (702) and "
    "`update` (684) — note that filtering to nouns did *not* rescue us from the "
    "template wording the frequency page flagged, since `process` and `update` are "
    "perfectly good nouns. Grammar is not relevance. Proper nouns fare better, recovering "
    "the geography the coordinates also encode — `Brgy`, `Davao`, `Norte`, `Sur`, "
    "`Zamboanga` — a useful cross-check that the text and the map describe the same "
    "country.\n\n"
    "**Why proper nouns are hard.** Capitalisation is the tagger's strongest clue, and "
    "the first word of every sentence is capitalised too. Raw output ranked `Tried` and "
    "`Felt` among the top \"names\" in this corpus. The page filters them out by keeping "
    "only capitalised words that *also* appear mid-sentence somewhere — worth knowing, "
    "because the same trap catches anyone tagging survey text. And the tagger is trained "
    "on English newswire, so Filipino and Taglish tokens get unreliable tags.\n\n"
    "**Co-occurrence: which terms travel together?** The heatmap counts how often two "
    "terms appear in the same comment, binary per document, so one comment saying "
    "`staff` twenty times contributes once. Bright cells mark concepts discussed "
    "together. They do not mark cause: `waited` and `staff` co-occurring tells you people "
    "raised both, not that staffing caused the wait. Use all three tabs to generate "
    "questions, then answer them by reading comments.",
    code=(
        "from rake_nltk import Rake\n"
        "r = Rake(); r.extract_keywords_from_text(corpus_text)\n"
        "ranked = r.get_ranked_phrases_with_scores()\n\n"
        "import nltk\n"
        "from nltk.tokenize.treebank import TreebankWordTokenizer\n"
        "tokens = TreebankWordTokenizer().tokenize(text)\n"
        "nouns = [w for w, tag in nltk.pos_tag(tokens) if tag.startswith('NN')]"
    ),
)

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
        st.plotly_chart(fig, width="stretch")
        st.download_button("⬇️ Keywords (CSV)", rk.to_csv(index=False),
                           "tala_keywords.csv", "text/csv")

with tab_nouns:
    if not nlp.pos_available():
        st.info("Noun extraction needs the NLTK tagger data, which is downloaded "
                "on first use. Check this container's network access and reload.")
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
            st.plotly_chart(fig, width="stretch")
        with c2:
            st.markdown("**Proper nouns**")
            fig = px.bar(proper.sort_values("count"), x="count", y="proper_noun",
                         orientation="h", color_discrete_sequence=[viz.NU_GOLD_DEEP])
            fig.update_layout(**viz.plotly_template(ui.palette())["layout"],
                              height=26 * len(proper) + 80, yaxis_title="",
                              showlegend=False)
            st.plotly_chart(fig, width="stretch")
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
        st.plotly_chart(fig, width="stretch")
