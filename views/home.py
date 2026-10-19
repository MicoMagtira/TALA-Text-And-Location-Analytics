import streamlit as st

from core import data_loader as dl
from core import i18n, tracks, ui

PAGE = "home"

ui.page_header(PAGE, "home")
st.markdown(i18n.t("home.greeting"))

# --- Continue card ------------------------------------------------------------
# Resume where the trainee left off; the page name is all session state keeps.
last = st.session_state.get(tracks.SS_LAST_PAGE)
pos = tracks.position(last) if last else None
if pos:
    with st.container(border=True, key="tala-continue"):
        track, index, total = pos
        st.markdown(f"**{i18n.t('home.continue', title=i18n.t(f'{last}.title'), track=i18n.t(f'home.track_{track}'), index=index, total=total)}**")
        st.page_link(tracks.path_of(last), label=i18n.t("home.continue_btn"),
                     icon=":material/arrow_forward:", icon_position="right")

# --- Your path ----------------------------------------------------------------
st.markdown(i18n.t("home.path_head"))
done = tracks.done_pages()
for col, track in zip(st.columns(2), ("text", "geo")):
    pages = tracks.TRACKS[track]
    n_done = sum(p in done for p in pages)
    with col, st.container(border=True, key=f"tala-card-{track}"):
        st.markdown(i18n.t(f"home.{track}_head"))
        st.markdown(ui.strip_html(track), unsafe_allow_html=True)
        st.caption(i18n.t("home.steps", done=n_done, total=len(pages)))
        st.markdown(i18n.t(f"home.{track}_list"))
        verb = "start" if n_done == 0 else ("review" if n_done == len(pages) else "resume")
        st.page_link(tracks.path_of(tracks.first_todo(track)),
                     label=i18n.t(f"home.{verb}"),
                     icon=":material/arrow_forward:", icon_position="right")

# --- Dataset ------------------------------------------------------------------
st.markdown(i18n.t("home.dataset_head"))
df = dl.active_df()
st.caption(i18n.t("home.source", source=ui.source_label()))
with st.expander(i18n.t("home.preview"), expanded=False):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(i18n.t("home.m_rows"), f"{len(df):,}")
    m2.metric(i18n.t("home.m_cols"), len(df.columns))
    m3.metric(i18n.t("home.m_textcol"), st.session_state.get(dl.SS_TEXT_COL, "—"))
    m4.metric(i18n.t("home.m_hasgeo"),
              i18n.t("home.yes") if dl.has_geo() else i18n.t("home.no"))
    st.dataframe(df.head(15), width="stretch")

with st.expander(i18n.t("home.about"), expanded=False):
    st.markdown(i18n.t("home.intro"))

ui.learn_page(PAGE)
