import streamlit as st

from core import data_loader as dl
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
st.markdown(i18n.t("text_1_data.step1"))
bundled = i18n.t("text_1_data.src_bundled")
upload = i18n.t("text_1_data.src_upload")
src = st.radio(i18n.t("text_1_data.source"), [bundled, upload],
               horizontal=True, label_visibility="collapsed")

if src == upload:
    up = st.file_uploader(i18n.t("text_1_data.uploader"), type=["csv", "xlsx", "xls"])
    if up is not None:
        # Registering returns a content-addressed key; the parsed frame lives in
        # the shared cache, so two trainees uploading the same file share it and
        # nothing large lands in this session's state.
        source_key = dl.register_upload(up.getvalue(), up.name)
        source_name = i18n.t("text_1_data.upload_name", name=up.name)
    else:
        st.stop()
else:
    source_key = dl.BUNDLED_KEY
    # Stored untranslated: ui.source_label() localizes it for display, so the
    # label survives a mid-session language switch.
    source_name = dl.BUNDLED_LABEL

df = dl.dataset(source_key)   # shared, read-only

# --- Column mapping -----------------------------------------------------------
st.markdown(i18n.t("text_1_data.step2"))
g_text, g_lon, g_lat = dl.guess_columns(df)
cols = list(df.columns)
c1, c2, c3 = st.columns(3)
text_col = c1.selectbox(i18n.t("text_1_data.text_col"), cols,
                        index=cols.index(g_text) if g_text in cols else 0)
none = i18n.t("text_1_data.none")
lon_col = c2.selectbox(i18n.t("text_1_data.lon_col"), [none] + cols,
                       index=(cols.index(g_lon) + 1) if g_lon in cols else 0)
lat_col = c3.selectbox(i18n.t("text_1_data.lat_col"), [none] + cols,
                       index=(cols.index(g_lat) + 1) if g_lat in cols else 0)
lon_col = None if lon_col == none else lon_col
lat_col = None if lat_col == none else lat_col

if st.button(i18n.t("text_1_data.use_btn"), type="primary"):
    dl.set_active(source_key, text_col, lon_col, lat_col, source_name)
    st.success(i18n.t("text_1_data.activated"))

st.markdown(i18n.t("text_1_data.preview"))
st.dataframe(df.head(20), width="stretch")
m1, m2, m3 = st.columns(3)
m1.metric(i18n.t("text_1_data.m_rows"), f"{len(df):,}")
m2.metric(i18n.t("text_1_data.m_cols"), len(df.columns))
m3.metric(i18n.t("text_1_data.m_coords"),
          i18n.t("text_1_data.coords_present") if (lon_col and lat_col)
          else i18n.t("text_1_data.coords_none"))

# --- Cleaning preview ---------------------------------------------------------
st.markdown("---")
st.markdown(i18n.t("text_1_data.step3"))
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
