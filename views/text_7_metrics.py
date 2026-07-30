import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import nlp, ui, viz

ui.page_title("Text Analytics", "Linguistic Metrics",
              "Corpus-level readability and lexical-diversity measures, plus the "
              "part-of-speech makeup of the text.")

ui.learn(
    "Readability formulas & lexical diversity",
    "Every number on this page is a *proxy*. Readability formulas do not read; they count "
    "syllables, words and sentences, then run the totals through a regression fitted "
    "decades ago on English schoolbook prose. Knowing what each one actually measures is "
    "the difference between using them and being used by them.\n\n"
    "**The readability family.** Flesch Reading Ease scores 0–100, higher = easier; this "
    "corpus lands at 54.0, which the scale calls \"fairly difficult\" — plausible for "
    "clinical vocabulary in casual sentences. Flesch-Kincaid (8.2), Gunning Fog (10.6) "
    "and SMOG (10.8) all convert to US school grades and *disagree by more than two "
    "grades on identical text.* That spread is the most useful thing here: it shows the "
    "formulas are opinions, not measurements. Report the direction of a difference "
    "between subsets, never the absolute grade.\n\n"
    "**Why two diversity measures.** Type-Token Ratio is unique words ÷ total words. On "
    "this corpus that is 1,687 ÷ 292,674 = **0.0058**, a number that looks alarming and "
    "means nothing — TTR falls mechanically as text lengthens, because vocabulary "
    "saturates while token count keeps climbing. Any long corpus scores near zero. "
    "**Herdan's C** takes the ratio in log space (log types ÷ log tokens) and lands at "
    "**0.59**, stable enough to compare corpora of different sizes. When someone reports "
    "a bare TTR across unequal samples, that is the error to catch.\n\n"
    "**Where this breaks on this data.** Syllable counters are English pronunciation "
    "rules, so Filipino and Taglish words get miscounted and every derived grade drifts. "
    "Sentence-splitting depends on punctuation these comments use loosely. And short "
    "survey replies sit far outside the prose these formulas were fitted on.\n\n"
    "**One firm boundary.** These are properties of *text*, never of people. A low "
    "readability score describes writing that is dense, not a writer who is limited — "
    "and applying them to individuals rather than corpora is the standard misuse.",
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
