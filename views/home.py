"""Home: a short visual landing (hero is drawn by ``ui.header`` from app.py).

Continue card, two chapter cards, the tour video and a collapsed data peek. The
theory lives on How TALA works, one link away (docs/PLAN_PANEL.md, section 3).
"""
from pathlib import Path

import streamlit as st

from core import data_loader as dl
from core import i18n, tracks, ui

PAGE = "home"
VIDEO_DIR = Path(__file__).resolve().parent.parent / "assets" / "video"

# --- Continue card ------------------------------------------------------------
# Resume where the trainee left off; the page name is all session state keeps.
last = st.session_state.get(tracks.SS_LAST_PAGE)
if last and tracks.position(last):
    with st.container(border=True, key="tala-continue"):
        st.markdown("**" + ui._t(
            "home.continue_step", "Continue: {title} (step {n} of {total})",
            title=ui.nav_title(last), n=tracks.step_number(last),
            total=len(tracks.ALL_PAGES)) + "**")
        st.page_link(tracks.path_of(last), label=i18n.t("home.continue_btn"),
                     icon=":material/arrow_forward:", icon_position="right")

# --- Two chapter cards --------------------------------------------------------
_QUESTION = {"where": "Where are people?", "what": "What is each place saying?"}
_LINE = {
    "where": "Check where each comment says it is from against its GPS, then group the comments into places.",
    "what": "Compare places by their words, feelings, themes and hotspots.",
}
for col, chapter in zip(st.columns(2), tracks.CHAPTERS):
    n_done, total = tracks.chapter_done_count(chapter)
    hint = (ui._t("nav.hint_ordered", "in order") if tracks.ORDERED[chapter]
            else ui._t("nav.hint_any", "any order"))
    verb = "start" if n_done == 0 else ("review" if n_done == total else "resume")
    with col, st.container(border=True, key=f"tala-card-{chapter}"):
        st.markdown(f'<div class="tala-chap-label">{tracks.NAMES[chapter]}</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="tala-chap-q">'
                    f'{ui._t(f"nav.q_{chapter}", _QUESTION[chapter])}</div>',
                    unsafe_allow_html=True)
        st.markdown(ui.strip_html(chapter), unsafe_allow_html=True)
        st.caption(f"{n_done}/{total} · {hint}")
        st.write(ui._t(f"home.{chapter}_line", _LINE[chapter]))
        st.page_link(tracks.path_of(tracks.first_todo(chapter)),
                     label=i18n.t(f"home.{verb}"),
                     icon=":material/arrow_forward:", icon_position="right")

# --- Tour video ---------------------------------------------------------------
# One captioned tour per UI language, recorded later (tools/record_tour.cjs). If
# there is none for this language, English; if there is no file at all, nothing
# is drawn: no empty player and no placeholder.
tour = next((p for p in (VIDEO_DIR / f"tour_{i18n.current()}.webm",
                         VIDEO_DIR / "tour_en.webm") if p.exists()), None)
if tour is not None:
    st.markdown(f"#### :material/play_circle: {ui._t('home.tour', 'Watch the 1-minute tour')}")
    # The tours are VP9 WebM; st.video labels files video/mp4 by default, which
    # Safari and Firefox refuse to play when the bytes are actually WebM.
    st.video(str(tour), format="video/webm")

# --- Data peek + pointer to the essay -----------------------------------------
df = dl.active_df()
with st.expander(ui._t("home.peek", "Peek at the data"), expanded=False):
    st.caption(i18n.t("home.source", source=ui.source_label()))
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(i18n.t("home.m_rows"), f"{len(df):,}")
    m2.metric(i18n.t("home.m_cols"), len(df.columns))
    m3.metric(i18n.t("home.m_textcol"), st.session_state.get(dl.SS_TEXT_COL, "—"))
    m4.metric(i18n.t("home.m_hasgeo"),
              i18n.t("home.yes") if dl.has_geo() else i18n.t("home.no"))
    st.dataframe(df.head(15), width="stretch")

st.page_link(tracks.path_of("learn"),
             label=ui._t("home.how_link", "New here? How TALA works"),
             icon=":material/arrow_forward:", icon_position="right")
