"""Stub for How TALA works. A later task fills in the essay, About and attributions."""
import streamlit as st

from core import ui

PAGE = "learn"

ui.page_header(PAGE, "learn")
st.info(ui._t("stub.placeholder", "This step is being built."))
