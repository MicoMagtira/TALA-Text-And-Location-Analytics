import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import nlp, ui, viz

ui.page_title("Text Analytics", "Linguistic Metrics",
              "Corpus-level readability and lexical-diversity measures, plus the "
              "part-of-speech makeup of the text.")

texts = dl.text_series().tolist()
metrics = nlp.readability(tuple(texts))

st.markdown("#### Readability & lexical diversity")
keys = list(metrics.items())
cols = st.columns(4)
for i, (k, v) in enumerate(keys):
    cols[i % 4].metric(k, f"{v:,}" if isinstance(v, int) else v)

with st.expander("What do these mean?"):
    st.markdown(
        "- **Flesch Reading Ease** — higher (up to ~100) is easier to read.\n"
        "- **Flesch-Kincaid / Gunning Fog / SMOG** — approximate US school grade "
        "level needed to understand the text; lower is simpler.\n"
        "- **Type-Token Ratio** and **Herdan's C** — lexical diversity "
        "(vocabulary richness); higher means more varied wording.")

st.markdown("---")
st.markdown("#### Part-of-speech proportions")
if not nlp.pos_available():
    st.info("POS proportions need the NLTK tagger data, which is downloaded on "
            "first use. Check this container's network access and reload.")
else:
    pos = nlp.pos_proportions(tuple(texts))
    if pos.empty:
        st.info("No POS data available.")
    else:
        fig = px.bar(pos, x="pos", y="percent", text="percent",
                     color_discrete_sequence=[viz.NU_NAVY])
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                          cliponaxis=False)
        fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=420,
                          xaxis_title="part of speech", yaxis_title="% of tokens",
                          showlegend=False)
        st.plotly_chart(fig, width="stretch")
        st.caption("Computed on a sample of up to 4,000 comments.")

ui.learn(
    "Readability formulas & lexical diversity",
    "Readability indices estimate how hard text is to read from sentence and word "
    "lengths (and syllable counts). We use the `textstat` library for Flesch Reading "
    "Ease, Flesch-Kincaid grade, Gunning Fog and SMOG. **Lexical diversity** is the "
    "ratio of unique words (types) to total words (tokens); **Herdan's C** = "
    "log(types)/log(tokens) corrects TTR's sensitivity to text length.",
    code=(
        "import textstat\n"
        "textstat.flesch_reading_ease(text)\n"
        "textstat.flesch_kincaid_grade(text)\n"
        "textstat.gunning_fog(text); textstat.smog_index(text)\n\n"
        "types, tokens = len(set(words)), len(words)\n"
        "ttr = types / tokens\n"
        "herdan_c = math.log(types) / math.log(tokens)"
    ),
)
