import plotly.express as px
import streamlit as st

from core import data_loader as dl
from core import i18n, nlp, ui, viz

PAGE = "text_7_metrics"

ui.page_header(PAGE, "text")
ui.learn_page(
    PAGE,
    code=(
        "import textstat\n\n"
        "joined = ' '.join(texts)\n"
        "words = joined.split()\n"
        "ttr = len({w.lower() for w in words}) / len(words)   # type-token ratio\n"
        "ease = textstat.flesch_reading_ease(joined)\n"
        "grade = textstat.flesch_kincaid_grade(joined)"
    ),
)

texts = dl.text_series().tolist()
metrics = nlp.readability(tuple(texts))

st.markdown(i18n.t("text_7_metrics.read_head"))
cols = st.columns(4)
for i, (k, v) in enumerate(metrics.items()):
    # Metric names come back from nlp.readability() in English; the catalog maps
    # each to its display name so the numbers keep their untranslated keys.
    cols[i % 4].metric(i18n.t(f"metric.{k}"), f"{v:,}" if isinstance(v, int) else v)

with st.expander(i18n.t("text_7_metrics.what")):
    st.markdown(i18n.t("text_7_metrics.what_body"))

st.markdown("---")
st.markdown(i18n.t("text_7_metrics.pos_head"))
if not nlp.pos_available():
    st.info(i18n.t("text_7_metrics.nltk_missing"))
else:
    pos = nlp.pos_proportions(tuple(texts))
    if pos.empty:
        st.info(i18n.t("text_7_metrics.no_pos"))
    else:
        fig = px.bar(pos, x="pos", y="percent", text="percent",
                     color_discrete_sequence=[viz.NU_NAVY])
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside",
                          cliponaxis=False)
        fig.update_layout(**viz.plotly_template(ui.palette())["layout"], height=420,
                          xaxis_title=i18n.t("text_7_metrics.axis_pos"),
                          yaxis_title=i18n.t("text_7_metrics.axis_pct"),
                          showlegend=False)
        st.plotly_chart(fig, width="stretch")
        st.caption(i18n.t("text_7_metrics.sample_caption"))
