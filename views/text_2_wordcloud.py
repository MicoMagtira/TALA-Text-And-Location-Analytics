import io

import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import nlp, preprocess, ui, viz

ui.page_title("Text Analytics", "Word Frequency & Clouds",
              "The most frequent words after cleaning, shown as a word cloud and a "
              "ranked bar chart, plus NRC positive/negative word clouds.")

ui.learn(
    "Frequencies & word clouds",
    "Counting words is the simplest thing you can do to a corpus, which makes it the "
    "easiest place to fool yourself. This page gives you the same counts twice, on "
    "purpose.\n\n"
    "**Read the bar chart, look at the cloud.** A word cloud encodes frequency as area, "
    "and human eyes are unreliable at comparing areas — a word twice as frequent does "
    "not look twice as big, and long words look more important than short ones simply "
    "because they occupy more pixels. `hospital` will always out-loom `staff` at equal "
    "counts. Use the cloud to notice *what is present*; use the bar chart whenever you "
    "need to say *how much*.\n\n"
    "**What the top of this corpus looks like.** `staff` (3,467), `felt` (2,765), "
    "`health` (2,612), `hospital` (2,586), `update` (2,493). Two of those five should "
    "make you suspicious. `update` and `felt` are not health-service concepts — they "
    "are artefacts of how these comments were phrased (\"Manila visit update:…\", "
    "\"Felt smooth…\"). Frequency found the template, not the topic.\n\n"
    "**That is the real lesson.** A word can be common because many people independently "
    "said it, or because one survey prompt put it in their mouths. Frequency cannot tell "
    "those apart. Only reading examples can, which is why the sample comments sit next "
    "to the chart. If a term is boilerplate, add it to the sidebar's custom stopwords "
    "and recount — a legitimate, documentable analytical move.\n\n"
    "**On the emotion clouds.** The positive/negative split uses the NRC lexicon, an "
    "English word-emotion dictionary. It matches word-by-word with no notion of context "
    "or negation, so \"not kind\" contributes `kind` to the positive cloud. Filipino "
    "terms are largely invisible to it. Treat the split as a rough sorting of English "
    "vocabulary, not as a measurement of how people felt — the Sentiment page handles "
    "that question with better tools, and still imperfectly.",
    code=(
        "from collections import Counter\n"
        "from wordcloud import WordCloud\n\n"
        "counts = Counter(tokens)\n"
        "wc = WordCloud(width=900, height=450, background_color='white',\n"
        "               colormap='viridis').generate_from_frequencies(dict(counts))"
    ),
)

texts = dl.text_series().tolist()
sw = ui.stopwords()
tokens = preprocess.all_tokens(texts, sw)

top_n = st.slider("Number of top words", 10, 50, 20, step=5)
freqs = dict(nlp.word_frequencies(tokens, top_n=200).set_index("word")["count"])

c1, c2 = st.columns([1.3, 1])
with c1:
    st.markdown("#### Word cloud")
    wc = nlp.make_wordcloud(freqs, ui.seq_palette())
    if wc is not None:
        fig, ax = viz.figure(figsize=(9, 4.5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig, width="stretch")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
        st.download_button("⬇️ Download word cloud (PNG)", buf.getvalue(),
                           "tala_wordcloud.png", "image/png")
    else:
        st.info("No tokens to display for the current data / stopwords.")

with c2:
    st.markdown("#### Top words")
    tdf = nlp.word_frequencies(tokens, top_n=top_n)
    fig = px.bar(tdf.sort_values("count"), x="count", y="word", orientation="h",
                 text="count", color_discrete_sequence=[viz.NU_NAVY])
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=520,
                      yaxis_title="", xaxis_title="frequency", showlegend=False)
    st.plotly_chart(fig, width="stretch")
    st.download_button("⬇️ Download counts (CSV)", tdf.to_csv(index=False),
                       "tala_word_counts.csv", "text/csv")

st.markdown("---")
st.markdown("#### Positive / negative word clouds (NRC lexicon)")
pos, neg = nlp.polarity_word_frequencies(tuple(tokens))
if not pos and not neg:
    st.info("The NRC lexicon (nrclex) is unavailable, so polarity word clouds are "
            "skipped. Install `nrclex` to enable them.")
else:
    pc, nc = st.columns(2)
    for col, data, title, cmap in [(pc, pos, "Positive", "NU Navy"),
                                    (nc, neg, "Negative", "NU Gold")]:
        with col:
            st.markdown(f"**{title}**")
            wcx = nlp.make_wordcloud(data, cmap, height=350)
            if wcx is not None:
                fig, ax = viz.figure(figsize=(6, 3.2))
                ax.imshow(wcx, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig, width="stretch")
            else:
                st.caption(f"No {title.lower()} words found.")
