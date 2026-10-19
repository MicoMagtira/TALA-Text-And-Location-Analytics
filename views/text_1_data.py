import streamlit as st

from core import audio, data_loader as dl
from core import i18n, preprocess, ui

PAGE = "text_1_data"

ui.page_header(PAGE, "text")
ui.learn_page(
    PAGE,
    code=(
        'from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS\n'
        'import re\n\n'
        'def clean_text(t):\n'
        '    t = t.lower()\n'
        '    t = re.sub(r"http\\S+|www\\.\\S+", " ", t)\n'
        '    t = re.sub(r"[@#]\\w+", " ", t)\n'
        '    t = re.sub(r"[^\\w\\s]", " ", t)   # punctuation (Unicode)\n'
        '    t = re.sub(r"\\d+", " ", t)\n'
        '    return re.sub(r"\\s+", " ", t).strip()\n\n'
        'stopwords = set(ENGLISH_STOP_WORDS) | tagalog_stopwords | custom\n'
        'tokens = [w for w in clean_text(t).split() if len(w) > 2 and w not in stopwords]'
    ),
)

# --- Data source --------------------------------------------------------------
# Changes apply instantly: there is no "Use this dataset" button. The radio is
# seeded from the dataset that is *currently* active, so it never lies about it.
SRC_KEY, UP_KEY = "t1_source", "_t1_upload_key"
BUNDLED, UPLOAD = "bundled", "upload"
st.session_state.setdefault(
    SRC_KEY, BUNDLED if dl.source_key() == dl.BUNDLED_KEY else UPLOAD)

st.markdown(i18n.t("text_1_data.step1"))
labels = {BUNDLED: i18n.t("text_1_data.src_bundled"), UPLOAD: i18n.t("text_1_data.src_upload")}
src = st.radio(i18n.t("text_1_data.source"), [BUNDLED, UPLOAD], key=SRC_KEY,
               format_func=labels.get, horizontal=True, label_visibility="collapsed")

if src == UPLOAD:
    up = st.file_uploader(i18n.t("text_1_data.uploader"), type=["csv", "xlsx", "xls"])
    if up is not None:
        # Registering returns a content-addressed key; the parsed frame lives in
        # the shared cache, so two trainees uploading the same file share it and
        # nothing large lands in this session's state.
        new_key = dl.register_upload(up.getvalue(), up.name)
        # Activate only a *new* upload, not on every rerun, so the trainee's own
        # column choices below are not overwritten.
        if st.session_state.get(UP_KEY) != new_key:
            st.session_state[UP_KEY] = new_key
            g_text, g_lon, g_lat = dl.guess_columns(dl.dataset(new_key))
            dl.set_active(new_key, g_text, g_lon, g_lat,
                          i18n.t("text_1_data.upload_name", name=up.name))
            st.toast(i18n.t("text_1_data.toast_upload", name=up.name), icon="📥")
            audio.cue("upload")
    elif dl.source_key() == dl.BUNDLED_KEY:
        st.caption(i18n.t("text_1_data.upload_hint"))
elif dl.source_key() != dl.BUNDLED_KEY:
    st.session_state.pop(UP_KEY, None)
    g_text, g_lon, g_lat = dl.guess_columns(dl.dataset(dl.BUNDLED_KEY))
    # Stored untranslated: ui.source_label() localizes it for display, so the
    # label survives a mid-session language switch.
    dl.set_active(dl.BUNDLED_KEY, g_text, g_lon, g_lat, dl.BUNDLED_LABEL)
    st.toast(i18n.t("text_1_data.toast_bundled"), icon="📦")

source_key = dl.source_key()
df = dl.active_df()   # shared, read-only
st.caption(i18n.t("text_1_data.active", source=ui.source_label()))

# --- Column mapping -----------------------------------------------------------
st.markdown(i18n.t("text_1_data.step2"))
none = i18n.t("text_1_data.none")
cols = list(df.columns)
# Widget keys carry the source key, so a new dataset gets fresh widgets seeded
# from the columns that were just guessed for it.
K_TEXT, K_LON, K_LAT = (f"t1_{n}_{source_key}" for n in ("text", "lon", "lat"))


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
c1.selectbox(i18n.t("text_1_data.text_col"), cols, key=K_TEXT, on_change=_apply_columns,
             index=_index(st.session_state.get(dl.SS_TEXT_COL)))
c2.selectbox(i18n.t("text_1_data.lon_col"), [none] + cols, key=K_LON, on_change=_apply_columns,
             index=_index(st.session_state.get(dl.SS_LON_COL), 1))
c3.selectbox(i18n.t("text_1_data.lat_col"), [none] + cols, key=K_LAT, on_change=_apply_columns,
             index=_index(st.session_state.get(dl.SS_LAT_COL), 1))
text_col = st.session_state[K_TEXT]

st.markdown(i18n.t("text_1_data.preview"))
st.dataframe(df.head(20), width="stretch")
m1, m2, m3 = st.columns(3)
m1.metric(i18n.t("text_1_data.m_rows"), f"{len(df):,}")
m2.metric(i18n.t("text_1_data.m_cols"), len(df.columns))
m3.metric(i18n.t("text_1_data.m_coords"),
          i18n.t("text_1_data.coords_present") if dl.has_geo()
          else i18n.t("text_1_data.coords_none"))

# --- Cleaning preview ---------------------------------------------------------
st.markdown("---")
st.markdown(i18n.t("text_1_data.step3"))


@st.fragment
def _cleaning_preview() -> None:
    """The slider only affects this block, so moving it reruns just this block."""
    sw = ui.stopwords()
    st.caption(i18n.t(
        "text_1_data.sw_caption", count=f"{len(sw):,}",
        tagalog=i18n.t("text_1_data.sw_tagalog")
        if st.session_state.get(ui.SS_USE_TL) else ""))

    sample = df[text_col].dropna().astype(str).head(400).tolist()
    idx = st.slider(i18n.t("text_1_data.inspect"), 0, max(0, len(sample) - 1), 0)
    raw = sample[idx] if sample else ""
    st.markdown(i18n.t("text_1_data.raw"))
    st.write(raw)
    st.markdown(i18n.t("text_1_data.cleaned"))
    st.code(preprocess.clean_text(raw) or i18n.t("text_1_data.empty_clean"))
    st.markdown(i18n.t("text_1_data.tokens"))
    st.write(preprocess.tokenize(raw, sw) or i18n.t("text_1_data.no_tokens"))


_cleaning_preview()

ui.page_done(PAGE)
ui.track_footer(PAGE)
