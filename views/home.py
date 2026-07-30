import streamlit as st

from core import data_loader as dl
from core import ui

ui.page_title("Overview", "Welcome to TALA")

ui.learn(
    "How the two tracks connect",
    "Most analytics tools answer either *what are people saying* or *where is this "
    "happening*. TALA is built to show why those two questions are weaker apart than "
    "together. One dataset of 12,000 health-service comments carries both a `text` "
    "column and a `lon`/`lat` pair, and every page is a different way of reading the "
    "same 12,000 rows.\n\n"
    "**Why the pairing matters.** Text alone tells you that 1,448 comments mention "
    "waiting hours, but not whether that is one overwhelmed facility or a nationwide "
    "pattern. Location alone shows you a dense cluster of 1,750 points, but not that "
    "the people inside it are talking about staff conduct rather than medicine supply. "
    "The final geospatial page joins the two: keywords and sentiment computed *per "
    "cluster*, which is a claim neither track could make by itself.\n\n"
    "**Two different shapes of work.** The eight text pages are independent lenses — "
    "open them in any order. The five geospatial pages are a *pipeline*, where each "
    "step consumes the last:\n\n"
    "`Ingest → DBSCAN → Generalization → NLP per cluster → Map & exports`\n\n"
    "That ordering is not a UI convenience. Distances cannot be measured until "
    "coordinates are validated and projected; clusters cannot be found without "
    "distances; per-cluster text needs clusters to group by. Skipping ahead produces "
    "a number, just not a defensible one.\n\n"
    "**A deliberate trap.** The bundled coordinates are dirty on purpose — some land in "
    "London and California. Nothing removes them until the land-clip on the last page, "
    "which drops 3,467 of 11,715 points. Roughly a third of this dataset is wrong in a "
    "way no error message will announce, and every intermediate map still looks "
    "plausible. Noticing that is the point.\n\n"
    "**Sidebar controls apply everywhere.** Palettes, the Filipino-stopword toggle and "
    "your custom stopwords are global, so a change on one page silently changes results "
    "on the others. Set them deliberately before comparing outputs.",
)

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

c1, c2 = st.columns(2)
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
st.markdown("---")
st.markdown("### 📦 Active dataset")
df = dl.active_df()
m1, m2, m3, m4 = st.columns(4)
m1.metric("Rows", f"{len(df):,}")
m2.metric("Columns", len(df.columns))
m3.metric("Text column", st.session_state.get(dl.SS_TEXT_COL, "—"))
m4.metric("Has coordinates", "Yes" if dl.has_geo() else "No")
st.caption(f"Source: {st.session_state.get(dl.SS_SOURCE, 'n/a')}")
st.dataframe(df.head(15), width="stretch")

st.info(
    "Go to **Text Analytics → Data & Preprocessing** to upload your own data or "
    "adjust the text column, then explore the Text and Geospatial sections in the "
    "sidebar. Use the sidebar toggles to change the palette, add Filipino "
    "stopwords, or hide the Learn panels during assessments.",
    icon="👉",
)
