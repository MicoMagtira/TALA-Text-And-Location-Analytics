import streamlit as st

from core import data_loader as dl
from core import preprocess, ui

ui.page_title("Text Analytics", "Data & Preprocessing",
              "Load a dataset, pick the text/coordinate columns, and preview the "
              "cleaning pipeline that every text page uses.")

# --- Data source --------------------------------------------------------------
st.markdown("### 1 · Choose a data source")
src = st.radio("Source", ["Bundled example (PH Health Services)", "Upload a file"],
               horizontal=True, label_visibility="collapsed")

if src == "Upload a file":
    up = st.file_uploader("Upload CSV or Excel (.xlsx). Needs a text column; "
                          "optional `lon`/`lat` for the geospatial pages.",
                          type=["csv", "xlsx", "xls"])
    if up is not None:
        df = dl.load_upload(up.getvalue(), up.name)
        source_name = f"Upload: {up.name}"
    else:
        st.stop()
else:
    df = dl.load_default()
    source_name = "Bundled example: PH Health Services Sentiments"

# --- Column mapping -----------------------------------------------------------
st.markdown("### 2 · Map the columns")
g_text, g_lon, g_lat = dl.guess_columns(df)
cols = list(df.columns)
c1, c2, c3 = st.columns(3)
text_col = c1.selectbox("Text column", cols, index=cols.index(g_text) if g_text in cols else 0)
none = "— none —"
lon_col = c2.selectbox("Longitude column", [none] + cols,
                       index=(cols.index(g_lon) + 1) if g_lon in cols else 0)
lat_col = c3.selectbox("Latitude column", [none] + cols,
                       index=(cols.index(g_lat) + 1) if g_lat in cols else 0)
lon_col = None if lon_col == none else lon_col
lat_col = None if lat_col == none else lat_col

if st.button("✅ Use this dataset", type="primary"):
    dl.set_active(df, text_col, lon_col, lat_col, source_name)
    st.success("Dataset activated. It now drives every Text and Geospatial page.")

st.markdown("#### Preview")
st.dataframe(df.head(20), width="stretch")
m1, m2, m3 = st.columns(3)
m1.metric("Rows", f"{len(df):,}")
m2.metric("Columns", len(df.columns))
m3.metric("Coordinates", "Present" if (lon_col and lat_col) else "None")

# --- Cleaning preview ---------------------------------------------------------
st.markdown("---")
st.markdown("### 3 · Preprocessing preview")
sw = ui.stopwords()
st.caption(f"Active stopword set: **{len(sw):,}** words "
           f"(English + {'Filipino + ' if st.session_state.get(ui.SS_USE_TL) else ''}custom). "
           "Adjust in the sidebar.")

sample = df[text_col].dropna().astype(str).head(400).tolist()
idx = st.slider("Inspect a sample row", 0, max(0, len(sample) - 1), 0)
raw = sample[idx] if sample else ""
st.markdown("**Raw**")
st.write(raw)
st.markdown("**Cleaned**")
st.code(preprocess.clean_text(raw) or "(empty after cleaning)")
st.markdown("**Tokens (stopwords removed)**")
st.write(preprocess.tokenize(raw, sw) or "(no tokens)")

ui.learn(
    "The preprocessing pipeline (from NLP.ipynb)",
    "Text is lowercased, then URLs, @mentions/#hashtags, digits, punctuation "
    "(Unicode-aware), underscores and extra whitespace are stripped. Tokens are "
    "split on whitespace, kept only if longer than 2 characters, and filtered "
    "against **English (scikit-learn) ∪ Filipino ∪ custom** stopwords — the union "
    "is what makes Taglish text work.",
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
