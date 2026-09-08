import io

import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import i18n, nlp, preprocess, ui, viz

PAGE = "text_2_wordcloud"

ui.page_header(PAGE, "text")
ui.learn_page(
    PAGE,
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

top_n = st.slider(i18n.t("text_2_wordcloud.top_n"), 10, 50, 20, step=5)
freqs = dict(nlp.word_frequencies(tokens, top_n=200).set_index("word")["count"])

c1, c2 = st.columns([1.3, 1])
with c1:
    st.markdown(i18n.t("text_2_wordcloud.wc_head"))
    wc = nlp.make_wordcloud(freqs, ui.seq_palette())
    if wc is not None:
        fig, ax = viz.figure(figsize=(9, 4.5))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig, width="stretch")
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
        st.download_button(i18n.t("text_2_wordcloud.dl_wc"), buf.getvalue(),
                           "tala_wordcloud.png", "image/png")
    else:
        st.info(i18n.t("text_2_wordcloud.no_tokens"))

with c2:
    st.markdown(i18n.t("text_2_wordcloud.top_head"))
    tdf = nlp.word_frequencies(tokens, top_n=top_n)
    fig = px.bar(tdf.sort_values("count"), x="count", y="word", orientation="h",
                 text="count", color_discrete_sequence=[viz.NU_NAVY])
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=520,
                      yaxis_title="",
                      xaxis_title=i18n.t("text_2_wordcloud.axis_freq"),
                      showlegend=False)
    st.plotly_chart(fig, width="stretch")
    st.download_button(i18n.t("text_2_wordcloud.dl_counts"), tdf.to_csv(index=False),
                       "tala_word_counts.csv", "text/csv")

st.markdown("---")
st.markdown(i18n.t("text_2_wordcloud.polarity_head"))
pos, neg = nlp.polarity_word_frequencies(tuple(tokens))
if not pos and not neg:
    st.info(i18n.t("text_2_wordcloud.nrc_missing"))
else:
    pc, nc = st.columns(2)
    for col, data, title, cmap in [
            (pc, pos, i18n.t("text_2_wordcloud.positive"), "NU Navy"),
            (nc, neg, i18n.t("text_2_wordcloud.negative"), "NU Gold")]:
        with col:
            st.markdown(f"**{title}**")
            wcx = nlp.make_wordcloud(data, cmap, height=350)
            if wcx is not None:
                fig, ax = viz.figure(figsize=(6, 3.2))
                ax.imshow(wcx, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig, width="stretch")
            else:
                st.caption(i18n.t("text_2_wordcloud.no_words",
                                  polarity=title.lower()))
