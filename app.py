"""TALA — Text And Location Analytics.

An interactive NLP + geospatial analytics explorer for data-science training,
by Mico C. Magtira (DOST-NICER). National University Manila branding.

Run:  streamlit run app.py

Boot order matters here. The app targets Streamlit Community Cloud (~1 GB RAM,
shared CPU), so the module graph is kept deliberately shallow: only streamlit and
pandas load before the first page renders. sklearn, matplotlib, geopandas, pydeck
and NLTK are imported inside the functions that use them, which means a visitor
who only opens the Home page never pays for the geospatial or modelling stacks.

A new session starts behind a language gate (English, Filipino, Cebuano,
Ilocano, Hiligaynon), then the boot splash, then START. The intro order is
language, splash, START: the first tap unlocks audio, the splash is already
localized and audible, and a trainee never watches the interface change language
mid-load. Returning visitors skip it via the saved prefs cookie (core/persist.py). See core/i18n.py for the translation model.
"""
from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="TALA — Text And Location Analytics",
    page_icon=":material/star:",
    layout="wide",
    initial_sidebar_state="expanded",
)

from core import i18n  # noqa: E402  (after set_page_config, per Streamlit rules)
from core import persist  # noqa: E402

# Saved prefs load before the gate check: a restored language means returning
# visitors skip the gate and land on the page named by the URL.
persist.restore()

# Nothing else renders until a language is chosen. language_gate() never
# returns — it calls st.stop(), and the run that follows START finds is_set().
if not i18n.is_set():
    from core import gate  # noqa: E402

    gate.language_gate()

# The splash goes up before anything heavy so the browser has something to paint
# while the rest of this module and the first dataset read complete.
from core import splash  # noqa: E402

boot = splash.boot()
if boot:
    boot.update(6, i18n.t("boot.core"))

from core import audio, data_loader as dl  # noqa: E402
from core import tracks, ui  # noqa: E402

if boot:
    boot.update(18, i18n.t("boot.theme"))

ui.inject_css()

# Pull the dataset in explicitly rather than letting the first page trigger it,
# so the read happens while the splash is still up and reports honest progress.
if boot:
    boot.update(32, i18n.t("boot.dataset"))
dl.ensure_loaded()

if boot:
    boot.update(44, i18n.t("boot.indexing"))

# --- Navigation ---------------------------------------------------------------
# Streamlit's own page list is hidden; ui.sidebar_nav draws the constellation
# (Home, How TALA works, two chapters, nine steps). The pages are still
# registered here so routing, URLs and st.page_link work. Titles come from the
# catalog with English fallbacks (ui.nav_title). See core/i18n.py.
home = st.Page("views/home.py", title=i18n.t("home.nav"), icon=":material/home:", default=True)
learn = st.Page("views/learn.py", title=ui._t("learn.nav", "How TALA works"),
                icon=":material/menu_book:")
journey = [
    st.Page(tracks.path_of(p), title=ui.nav_title(p))
    for p in tracks.ALL_PAGES
]
nav = st.navigation([home, learn, *journey], position="hidden")

# The nav slot sits above Settings. It is drawn now (so it is there while a slow
# page computes) and redrawn after the page runs if a step was just completed.
nav_slot = st.sidebar.empty()
with nav_slot.container():
    ui.sidebar_nav(nav.url_path or "")
done_before = tracks.done_pages()
ui.sidebar_controls()

# The music follows the page about to run. url_path is "" for Home.
area = tracks.area_for(nav.url_path or "")
audio.mount(area)

if boot:
    boot.update(55, i18n.t("boot.render"))

# Only Home keeps the big banner; journey pages carry a compact header instead.
if area == "home":
    ui.header()

# The splash must come down even if a page raises, otherwise the overlay would
# sit on top of the traceback.
try:
    nav.run()
finally:
    if tracks.done_pages() != done_before:
        with nav_slot.container():
            ui.sidebar_nav(nav.url_path or "", redraw=True)
    if boot:
        boot.finish(i18n.t("boot.ready"))
    persist.save()

ui.footer()
