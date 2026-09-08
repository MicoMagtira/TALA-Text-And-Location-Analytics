import streamlit as st

from core import data_loader as dl
from core import i18n, ui

PAGE = "home"

ui.page_header(PAGE, "home")
ui.learn_page(PAGE)

st.markdown(i18n.t("home.intro"))

c1, c2 = st.columns(2)
with c1:
    st.markdown(i18n.t("home.text_head"))
    st.markdown(i18n.t("home.text_list"))
with c2:
    st.markdown(i18n.t("home.geo_head"))
    st.markdown(i18n.t("home.geo_list"))

st.markdown("---")
st.markdown(i18n.t("home.dataset_head"))
df = dl.active_df()
m1, m2, m3, m4 = st.columns(4)
m1.metric(i18n.t("home.m_rows"), f"{len(df):,}")
m2.metric(i18n.t("home.m_cols"), len(df.columns))
m3.metric(i18n.t("home.m_textcol"), st.session_state.get(dl.SS_TEXT_COL, "—"))
m4.metric(i18n.t("home.m_hasgeo"),
          i18n.t("home.yes") if dl.has_geo() else i18n.t("home.no"))
st.caption(i18n.t("home.source", source=ui.source_label()))
st.dataframe(df.head(15), width="stretch")

st.info(i18n.t("home.tip"), icon="👉")
