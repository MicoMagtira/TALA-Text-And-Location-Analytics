import streamlit as st

from core import data_loader as dl
from core import preprocess, ui

ui.page_title("Text Analytics", "Data & Preprocessing",
              "Load a dataset, pick the text/coordinate columns, and preview the "
              "cleaning pipeline that every text page uses.")

ui.learn(
    "The preprocessing pipeline (from NLP.ipynb)",
    "Preprocessing is where you decide what the computer is allowed to notice. Raw text "
    "carries punctuation, capitalization, filler words, emoji, numbers, typos and mixed "
    "languages. Some of that is signal and some is noise, and *which is which depends "
    "entirely on your research question.* Preprocessing is not a cleansing ritual — it "
    "is a research decision you have to be able to defend.\n\n"
    "**What this pipeline does, in order.** Lowercase → strip URLs → strip `@mentions` "
    "and `#hashtags` → strip punctuation (Unicode-aware, so it handles curly quotes) → "
    "strip digits → collapse whitespace → split on spaces → drop tokens shorter than 3 "
    "characters → drop stopwords.\n\n"
    "**What it costs on this corpus.** 292,674 raw words become 174,562 tokens — you "
    "are discarding 40% of the text. The surviving vocabulary is 551 distinct words. "
    "That is a big reduction, and it is the whole point: what remains should be the "
    "part worth counting.\n\n"
    "**The stopword decision.** 318 English stopwords come from scikit-learn's standard "
    "list; 147 Filipino stopwords (`ang`, `sa`, `mga`, `naman`) are bundled separately "
    "and toggled in the sidebar. Turn the Filipino list off and re-run any later page — "
    "Tagalog function words flood the top of every frequency chart, which is exactly "
    "what happens when you apply English-only tooling to Taglish data.\n\n"
    "**Where the defaults will hurt you.** The digit-stripping rule deletes `24/7`, "
    "`3 hours` and `P500`. The punctuation rule deletes the `!` in \"three hours "
    "again!\" — if you are studying anger, you just removed the anger. The 3-character "
    "minimum deletes `ER`, `OB` and `IV`. None of this is wrong in general and all of "
    "it might be wrong for you.\n\n"
    "**Do this before moving on.** Read the raw-vs-cleaned pairs below. If a comment "
    "you understand becomes a comment you do not, add the lost words to the sidebar's "
    "custom stopword box in reverse — that is, reconsider the rule, not the example.",
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
st.markdown("### 1 · Choose a data source")
src = st.radio("Source", ["Bundled example (PH Health Services)", "Upload a file"],
               horizontal=True, label_visibility="collapsed")

if src == "Upload a file":
    up = st.file_uploader("Upload CSV or Excel (.xlsx). Needs a text column; "
                          "optional `lon`/`lat` for the geospatial pages.",
                          type=["csv", "xlsx", "xls"])
    if up is not None:
        # Registering returns a content-addressed key; the parsed frame lives in
        # the shared cache, so two trainees uploading the same file share it and
        # nothing large lands in this session's state.
        source_key = dl.register_upload(up.getvalue(), up.name)
        source_name = f"Upload: {up.name}"
    else:
        st.stop()
else:
    source_key = dl.BUNDLED_KEY
    source_name = dl.BUNDLED_LABEL

df = dl.dataset(source_key)   # shared, read-only

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
    dl.set_active(source_key, text_col, lon_col, lat_col, source_name)
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
