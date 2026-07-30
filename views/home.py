import streamlit as st

from core import data_loader as dl
from core import ui

ui.page_title("Overview", "Welcome to TALA")

st.markdown(
    """
**TALA — Text And Location Analytics** is a hands-on training app that pairs
classic **Natural Language Processing** with a full **geospatial** workflow, so
participants can move from raw comments to *what people are saying* **and**
*where they are saying it*.

*Tala* is Filipino for **star** and for a **record / note** — fitting for a tool
that turns notes into insight.
    """
)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("#### 🧠 Text Analytics")
    st.markdown(
        "- Cleaning & Filipino/Taglish stopwords\n"
        "- Word clouds & frequencies\n"
        "- VADER sentiment + NRC emotions\n"
        "- N-grams & co-occurrence networks\n"
        "- LDA topics + stability\n"
        "- RAKE keywords, nouns/POS\n"
        "- Readability metrics & TF-IDF themes"
    )
with c2:
    st.markdown("#### 🗺️ Geospatial Analytics")
    st.markdown(
        "- Ingest + **CRS/bounds validation**\n"
        "- DBSCAN clustering (+ k-distance)\n"
        "- Grid / centroid generalization\n"
        "- Philippines land clipping\n"
        "- Interactive & publication maps\n"
        "- **NLP per cluster** (privacy-safe)\n"
        "- GeoJSON / PNG / CSV exports"
    )
with c3:
    st.markdown("#### 🎓 For Training")
    st.markdown(
        "- **Learn** panels with source code\n"
        "- Adjustable parameters (live)\n"
        "- Reset-to-lab-defaults buttons\n"
        "- NU-Manila branding\n"
        "- Responsive on any screen\n"
        "- Bundled example dataset"
    )

st.markdown("---")
st.markdown("### 📦 Active dataset")
df = dl.active_df()
m1, m2, m3, m4 = st.columns(4)
m1.metric("Rows", f"{len(df):,}")
m2.metric("Columns", len(df.columns))
m3.metric("Text column", st.session_state.get(dl.SS_TEXT_COL, "—"))
m4.metric("Has coordinates", "Yes" if dl.has_geo() else "No")
st.caption(f"Source: {st.session_state.get(dl.SS_SOURCE, 'n/a')}")
st.dataframe(df.head(15), use_container_width=True)

st.info(
    "Go to **Text Analytics → Data & Preprocessing** to upload your own data or "
    "adjust the text column, then explore the Text and Geospatial sections in the "
    "sidebar. Use the sidebar toggles to change the palette, add Filipino "
    "stopwords, or hide the Learn panels during assessments.",
    icon="👉",
)

ui.learn(
    "How the two tracks connect",
    "The same dataset drives both tracks. In the geospatial track the pages "
    "**chain** just like the original Colab labs — each step reads the previous "
    "step's output from the session:\n\n"
    "`CSV → Ingest (points) → DBSCAN (clusters) → Generalization / NLP-per-cluster → Map & Exports`\n\n"
    "The **NLP per Cluster** page is the integration point: it profiles each "
    "spatial cluster with TF-IDF keywords + VADER sentiment, but only ever shows "
    "**aggregated** results — never raw comments — which is the privacy-safe "
    "principle from Lab 5.",
)
