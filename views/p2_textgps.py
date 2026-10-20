"""Stub for step 2 (p2_textgps). A later task replaces the body; the header,
auto-ran line, done mark and footer below are the skeleton every journey page keeps."""
import streamlit as st

from core import ui

PAGE = "p2_textgps"

ui.page_header(PAGE, "where")
ui.auto_ran(PAGE)
st.info(ui._t("stub.placeholder", "This step is being built."))
ui.page_done(PAGE)
ui.track_footer(PAGE)
