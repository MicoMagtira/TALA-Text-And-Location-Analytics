"""Step 1 (Lugar): load a dataset, map its columns, preview the cleaning.

The custom-stopword box and the Filipino toggle live here (they used to sit in
Settings). Their widgets use *local* keys and copy into ``ui.SS_CUSTOM_SW`` /
``ui.SS_USE_TL`` on change: a widget that is not drawn on a page loses its
state in Streamlit, and the stopword set must survive visits to other pages."""
import streamlit as st

from core import audio, data_loader as dl
from core import i18n, preprocess, ui

PAGE = "p1_data"
_t = ui._t

# Re-assert the stopword keys: Streamlit drops state for keys whose widget is not
# drawn on the current page, and these must survive navigating away and back.
st.session_state[ui.SS_CUSTOM_SW] = st.session_state.get(ui.SS_CUSTOM_SW, "")
st.session_state[ui.SS_USE_TL] = st.session_state.get(ui.SS_USE_TL, True)

ui.page_header(PAGE, "where")
ui.learn_page(
    PAGE,
    code=(
        'import re\n'
        'from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS\n\n'
        'def clean_text(t):\n'
        '    t = t.lower()\n'
        '    t = re.sub(r"http\\S+|www\\.\\S+", " ", t)\n'
        '    t = re.sub(r"[@#]\\w+", " ", t)\n'
        '    t = re.sub(r"[^\\w\\s]", " ", t)   # punctuation (Unicode)\n'
        '    t = re.sub(r"\\d+", " ", t)\n'
        '    return re.sub(r"\\s+", " ", t).strip()\n\n'
        'stopwords = set(ENGLISH_STOP_WORDS) | tagalog_stopwords | custom\n'
        'tokens = [w for w in clean_text(text).split()\n'
        '          if len(w) > 2 and w not in stopwords]'
    ),
)

# --- Data source --------------------------------------------------------------
# Changes apply instantly: there is no "Use this dataset" button. The radio is
# seeded from the dataset that is *currently* active, so it never lies about it.
SRC_KEY, UP_KEY = "p1_source", "_p1_upload_key"
BUNDLED, UPLOAD = "bundled", "upload"
st.session_state.setdefault(
    SRC_KEY, BUNDLED if dl.source_key() == dl.BUNDLED_KEY else UPLOAD)

st.markdown(_t("p1_data.step1", "### Choose a data source"))
labels = {BUNDLED: _t("p1_data.src_bundled", "Bundled example (PH Health Services)"),
          UPLOAD: _t("p1_data.src_upload", "Upload a file")}
src = st.radio(_t("p1_data.source", "Source"), [BUNDLED, UPLOAD], key=SRC_KEY,
               format_func=labels.get, horizontal=True, label_visibility="collapsed")

if src == UPLOAD:
    up = st.file_uploader(
        _t("p1_data.uploader",
           "Upload CSV or Excel (.xlsx). Needs a text column; add `lon`/`lat` columns for the maps."),
        type=["csv", "xlsx", "xls"])
    if up is not None:
        # Registering returns a content-addressed key; the parsed frame lives in
        # the shared cache, so nothing large lands in this session's state.
        new_key = dl.register_upload(up.getvalue(), up.name)
        # Activate only a *new* upload so the trainee's own column choices stay.
        if st.session_state.get(UP_KEY) != new_key:
            st.session_state[UP_KEY] = new_key
            g_text, g_lon, g_lat = dl.guess_columns(dl.dataset(new_key))
            dl.set_active(new_key, g_text, g_lon, g_lat,
                          _t("p1_data.upload_name", "Upload: {name}", name=up.name))
            st.toast(_t("p1_data.toast_upload",
                        "Loaded {name}. Columns were guessed; change them below if needed.",
                        name=up.name), icon=":material/upload_file:")
            audio.cue("upload")
    elif dl.source_key() == dl.BUNDLED_KEY:
        st.caption(_t("p1_data.upload_hint",
                      "Upload a file to switch to it. Until then the current dataset stays active."))
elif dl.source_key() != dl.BUNDLED_KEY:
    st.session_state.pop(UP_KEY, None)
    g_text, g_lon, g_lat = dl.guess_columns(dl.dataset(dl.BUNDLED_KEY))
    # Stored untranslated: ui.source_label() localizes it for display.
    dl.set_active(dl.BUNDLED_KEY, g_text, g_lon, g_lat, dl.BUNDLED_LABEL)
    st.toast(_t("p1_data.toast_bundled", "Switched to the bundled example."),
             icon=":material/dataset:")

source_key = dl.source_key()
df = dl.active_df()   # shared, read-only
st.caption(_t("p1_data.active", "Active dataset: **{source}**.", source=ui.source_label()))

# --- Column mapping -----------------------------------------------------------
st.markdown(_t("p1_data.step2", "### Map the columns"))
none = _t("p1_data.none", "— none —")
cols = list(df.columns)
# Widget keys carry the source key, so a new dataset gets fresh widgets seeded
# from the columns that were just guessed for it.
K_TEXT, K_LON, K_LAT = (f"p1_{n}_{source_key}" for n in ("text", "lon", "lat"))


def _apply_columns() -> None:
    """Selecting a column is the commit: write it straight to the active dataset."""
    lon = st.session_state[K_LON]
    lat = st.session_state[K_LAT]
    dl.set_active(source_key, st.session_state[K_TEXT],
                  None if lon == none else lon, None if lat == none else lat,
                  st.session_state.get(dl.SS_SOURCE, dl.BUNDLED_LABEL))


def _index(col, extra: int = 0) -> int:
    return cols.index(col) + extra if col in cols else 0


c1, c2, c3 = st.columns(3)
c1.selectbox(_t("p1_data.text_col", "Text column"), cols, key=K_TEXT,
             on_change=_apply_columns, index=_index(st.session_state.get(dl.SS_TEXT_COL)))
c2.selectbox(_t("p1_data.lon_col", "Longitude column"), [none] + cols, key=K_LON,
             on_change=_apply_columns, index=_index(st.session_state.get(dl.SS_LON_COL), 1))
c3.selectbox(_t("p1_data.lat_col", "Latitude column"), [none] + cols, key=K_LAT,
             on_change=_apply_columns, index=_index(st.session_state.get(dl.SS_LAT_COL), 1))
text_col = st.session_state[K_TEXT]

st.dataframe(df.head(20), width="stretch")
m1, m2, m3 = st.columns(3)
m1.metric(_t("p1_data.m_rows", "Rows"), f"{len(df):,}")
m2.metric(_t("p1_data.m_cols", "Columns"), len(df.columns))
m3.metric(_t("p1_data.m_coords", "Coordinates"),
          _t("p1_data.coords_present", "Present") if dl.has_geo()
          else _t("p1_data.coords_none", "None"))
if not dl.has_geo():
    ui.warn(_t("p1_data.need_coords",
               "Pick a longitude and a latitude column to unlock the next steps."))

# --- Cleaning preview + stopwords ---------------------------------------------
st.markdown("---")
st.markdown(_t("p1_data.step3", "### Clean the text"))

W_TL, W_SW = "p1_use_tagalog", "p1_custom_sw"
# Seed the local widgets from the session values that persist across pages.
st.session_state.setdefault(W_TL, st.session_state.get(ui.SS_USE_TL, True))
st.session_state.setdefault(W_SW, st.session_state.get(ui.SS_CUSTOM_SW, ""))
st.session_state.setdefault(ui.SS_USE_TL, st.session_state[W_TL])
st.session_state.setdefault(ui.SS_CUSTOM_SW, st.session_state[W_SW])


def _save_stopwords() -> None:
    st.session_state[ui.SS_USE_TL] = st.session_state[W_TL]
    st.session_state[ui.SS_CUSTOM_SW] = st.session_state[W_SW]


s1, s2 = st.columns([1, 2])
s1.checkbox(i18n.t("side.use_tagalog"),
            key=W_TL, on_change=_save_stopwords)
s2.text_area(i18n.t("side.custom_stopwords"),
             key=W_SW, height=90, on_change=_save_stopwords,
             placeholder=i18n.t("side.custom_placeholder"))


@st.fragment
def _cleaning_preview() -> None:
    """The slider only affects this block, so moving it reruns just this block."""
    sw = ui.stopwords()
    st.caption(_t("p1_data.sw_caption", "Ignoring **{count}** common words.",
                  count=f"{len(sw):,}"))
    sample = df[text_col].dropna().astype(str).head(400).tolist()
    idx = st.slider(_t("p1_data.inspect", "Inspect a sample row"), 0,
                    max(0, len(sample) - 1), 0)
    raw = sample[idx] if sample else ""
    st.markdown(_t("p1_data.raw", "**Raw**"))
    st.write(raw)
    st.markdown(_t("p1_data.cleaned", "**Cleaned**"))
    st.code(preprocess.clean_text(raw) or _t("p1_data.empty_clean", "(empty after cleaning)"))
    st.markdown(_t("p1_data.tokens", "**Tokens (stopwords removed)**"))
    st.write(preprocess.tokenize(raw, sw) or _t("p1_data.no_tokens", "(no tokens)"))


_cleaning_preview()

ui.page_done(PAGE)
ui.track_footer(PAGE)
