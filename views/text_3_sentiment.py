import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import nlp, ui, viz

ui.page_title("Text Analytics", "Sentiment & Emotion",
              "VADER polarity per comment (positive / neutral / negative) and the "
              "NRC emotion profile of the corpus.")

texts = dl.text_series().tolist()
thr = st.slider("VADER neutral threshold (±)", 0.0, 0.2, 0.05, 0.01)

sent = nlp.vader_sentiment(tuple(texts), thr)
cats = ["positive", "neutral", "negative"]
cmap = {"positive": "#008300", "neutral": viz.INK_MUTED, "negative": "#e34948"}

c1, c2 = st.columns(2)
with c1:
    st.markdown("#### Sentiment distribution")
    counts = sent["label"].value_counts().reindex(cats).fillna(0).reset_index()
    counts.columns = ["label", "count"]
    fig = px.bar(counts, x="label", y="count", color="label", text="count",
                 color_discrete_map=cmap, category_orders={"label": cats})
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=380,
                      showlegend=False, xaxis_title="", yaxis_title="comments")
    st.plotly_chart(fig, width="stretch")
with c2:
    st.markdown("#### Compound score distribution")
    fig = px.histogram(sent, x="compound", nbins=40,
                       color_discrete_sequence=[viz.NU_NAVY])
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=380,
                      xaxis_title="VADER compound", yaxis_title="comments")
    st.plotly_chart(fig, width="stretch")

m1, m2, m3 = st.columns(3)
m1.metric("Positive", f"{(sent['label'] == 'positive').mean() * 100:.1f}%")
m2.metric("Neutral", f"{(sent['label'] == 'neutral').mean() * 100:.1f}%")
m3.metric("Negative", f"{(sent['label'] == 'negative').mean() * 100:.1f}%")

with st.expander("See most positive / negative examples"):
    st.markdown("**Most positive**")
    st.write(sent.nlargest(5, "compound")[["compound", "text"]])
    st.markdown("**Most negative**")
    st.write(sent.nsmallest(5, "compound")[["compound", "text"]])

st.download_button("⬇️ Download per-comment sentiment (CSV)",
                   sent.to_csv(index=False), "tala_sentiment.csv", "text/csv")

st.markdown("---")
st.markdown("#### Emotion profile (NRC lexicon)")
n_sample = min(len(texts), 4000)
emo = nlp.nrc_emotions(tuple(texts[:n_sample]))
if emo.empty:
    st.info("NRC emotions require `nrclex`. Install it to enable this chart.")
else:
    st.caption(f"Aggregated over {n_sample:,} comments.")
    fig = px.bar(emo, x="emotion", y="count", color="emotion",
                 color_discrete_sequence=viz.categorical(ui.palette()))
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=400,
                      showlegend=False, xaxis_title="", yaxis_title="term hits")
    st.plotly_chart(fig, width="stretch")

st.warning("**Teaching note:** VADER and the NRC lexicon are English-tuned. On "
           "Filipino/Taglish text they still give a useful signal but will miss "
           "or misread native-language emotion — a great point to discuss with "
           "participants and to motivate multilingual models.", icon="⚠️")

ui.learn(
    "How VADER scores sentiment",
    "VADER (Valence Aware Dictionary and sEntiment Reasoner) is a rule + lexicon "
    "model. Its **compound** score is normalized to [-1, 1]; the common convention "
    "labels ≥ +0.05 positive, ≤ -0.05 negative, and the band between as neutral. "
    "Unlike the bag-of-words steps, VADER runs on the **raw** text so punctuation, "
    "capitalization and emojis contribute.",
    code=(
        "from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer\n"
        "sia = SentimentIntensityAnalyzer()\n"
        "c = sia.polarity_scores(text)['compound']\n"
        "label = 'positive' if c >= 0.05 else 'negative' if c <= -0.05 else 'neutral'"
    ),
)
