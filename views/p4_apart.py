"""Stub for step 4 (p4_apart). A later task replaces the body; the header,
auto-ran line, done mark and footer below are the skeleton every journey page keeps."""
import streamlit as st

from core import ui

PAGE = "p4_apart"

ui.page_header(PAGE, "what")
ui.auto_ran(PAGE)
st.info(ui._t("stub.placeholder", "This step is being built."))
ui.page_done(PAGE)
ui.track_footer(PAGE)
