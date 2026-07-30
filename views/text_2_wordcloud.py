import io

import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import nlp, preprocess, ui, viz

ui.page_title("Text Analytics", "Word Frequency & Clouds",
              "The most frequent words after cleaning, shown as a word cloud and a "
              "ranked bar chart, plus NRC positive/negative word clouds.")
viz.apply_matplotlib_theme()

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
        fig, ax = plt.subplots(figsize=(9, 4.5))
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
                fig, ax = plt.subplots(figsize=(6, 3.2))
                ax.imshow(wcx, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig, width="stretch")
            else:
                st.caption(f"No {title.lower()} words found.")

ui.learn(
    "Frequencies & word clouds",
    "After cleaning and stopword removal, we count tokens with `collections.Counter`. "
    "A **word cloud** sizes each word by frequency; the bar chart shows exact counts "
    "(direct-labeled, since some palette colors sit below the 3:1 contrast floor and "
    "must not rely on color alone). The positive/negative clouds classify each unique "
    "word with the **NRC emotion lexicon**.",
    code=(
        "from collections import Counter\n"
        "from wordcloud import WordCloud\n\n"
        "counts = Counter(tokens)\n"
        "wc = WordCloud(width=900, height=450, background_color='white',\n"
        "               colormap='viridis').generate_from_frequencies(dict(counts))"
    ),
)
