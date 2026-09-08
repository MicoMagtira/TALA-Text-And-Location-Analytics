import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import i18n, nlp, ui, viz

PAGE = "text_3_sentiment"

ui.page_header(PAGE, "text")
ui.learn_page(
    PAGE,
    code=(
        "from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer\n"
        "sia = SentimentIntensityAnalyzer()\n"
        "c = sia.polarity_scores(text)['compound']\n"
        "label = 'positive' if c >= 0.05 else 'negative' if c <= -0.05 else 'neutral'"
    ),
)

texts = dl.text_series().tolist()
thr = st.slider(i18n.t("text_3_sentiment.threshold"), 0.0, 0.2, 0.05, 0.01)

sent = nlp.vader_sentiment(tuple(texts), thr)
cats = ["positive", "neutral", "negative"]
cmap = {"positive": "#008300", "neutral": viz.INK_MUTED, "negative": "#e34948"}
# The label column stays English so the CSV export contract is unchanged; only
# what the chart prints is localized.
shown = {c: i18n.t(f"sent.{c}") for c in cats}

c1, c2 = st.columns(2)
with c1:
    st.markdown(i18n.t("text_3_sentiment.dist_head"))
    counts = sent["label"].value_counts().reindex(cats).fillna(0).reset_index()
    counts.columns = ["label", "count"]
    counts["shown"] = counts["label"].map(shown)
    fig = px.bar(counts, x="shown", y="count", color="label", text="count",
                 color_discrete_map=cmap,
                 category_orders={"shown": [shown[c] for c in cats]})
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=380,
                      showlegend=False, xaxis_title="",
                      yaxis_title=i18n.t("text_3_sentiment.axis_comments"))
    st.plotly_chart(fig, width="stretch")
with c2:
    st.markdown(i18n.t("text_3_sentiment.compound_head"))
    fig = px.histogram(sent, x="compound", nbins=40,
                       color_discrete_sequence=[viz.NU_NAVY])
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=380,
                      xaxis_title=i18n.t("text_3_sentiment.axis_compound"),
                      yaxis_title=i18n.t("text_3_sentiment.axis_comments"))
    st.plotly_chart(fig, width="stretch")

m1, m2, m3 = st.columns(3)
m1.metric(i18n.t("text_3_sentiment.m_positive"),
          f"{(sent['label'] == 'positive').mean() * 100:.1f}%")
m2.metric(i18n.t("text_3_sentiment.m_neutral"),
          f"{(sent['label'] == 'neutral').mean() * 100:.1f}%")
m3.metric(i18n.t("text_3_sentiment.m_negative"),
          f"{(sent['label'] == 'negative').mean() * 100:.1f}%")

with st.expander(i18n.t("text_3_sentiment.examples")):
    st.markdown(i18n.t("text_3_sentiment.most_pos"))
    st.write(sent.nlargest(5, "compound")[["compound", "text"]])
    st.markdown(i18n.t("text_3_sentiment.most_neg"))
    st.write(sent.nsmallest(5, "compound")[["compound", "text"]])

st.download_button(i18n.t("text_3_sentiment.dl"),
                   sent.to_csv(index=False), "tala_sentiment.csv", "text/csv")

st.markdown("---")
st.markdown(i18n.t("text_3_sentiment.emo_head"))
n_sample = min(len(texts), 4000)
emo = nlp.nrc_emotions(tuple(texts[:n_sample]))
if emo.empty:
    st.info(i18n.t("text_3_sentiment.nrc_missing"))
else:
    st.caption(i18n.t("text_3_sentiment.emo_caption", n=f"{n_sample:,}"))
    fig = px.bar(emo, x="emotion", y="count", color="emotion",
                 color_discrete_sequence=viz.categorical(ui.palette()))
    fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=400,
                      showlegend=False, xaxis_title="",
                      yaxis_title=i18n.t("text_3_sentiment.axis_hits"))
    st.plotly_chart(fig, width="stretch")

st.warning(i18n.t("text_3_sentiment.teaching_note"), icon="⚠️")
