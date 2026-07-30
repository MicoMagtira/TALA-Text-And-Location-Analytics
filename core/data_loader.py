"""Data loading + shared session state for TALA.

A single 4-column dataset (id, text, lon, lat) feeds both the text-analytics and
geospatial tracks. The bundled example is PH_Health_Services_Sentiments.csv
(12,000 PH health-service comments with deliberately dirty coordinates, used to
teach CRS/bounds validation).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# Parquet is the shipped format (~0.5 MB vs 2.5 MB, and no text parsing on load);
# the CSV is kept alongside it as the human-readable teaching copy and as a
# fallback if pyarrow is unavailable.
DEFAULT_PARQUET = DATA_DIR / "PH_Health_Services_Sentiments.parquet"
DEFAULT_CSV = DATA_DIR / "PH_Health_Services_Sentiments.csv"
TAGALOG_STOPWORDS = DATA_DIR / "tagalog_stop_words.txt"
ENGLISH_STOPWORDS = DATA_DIR / "english_stop_words.txt"

# Session-state keys shared across pages (the geo pages chain through these,
# mirroring the notebooks' outputs/*.geojson pipeline).
SS_DF = "active_df"
SS_TEXT_COL = "text_col"
SS_LON_COL = "lon_col"
SS_LAT_COL = "lat_col"
SS_SOURCE = "data_source"
SS_POINTS = "geo_points"          # cleaned GeoDataFrame (Lab 1)
SS_CLUSTERS = "geo_clusters"      # DBSCAN result (Lab 2)
SS_GENERALIZED = "geo_generalized"  # grid / centroids (Lab 3)
SS_CLUSTER_TEXT = "geo_cluster_text"  # per-cluster NLP (Lab 5)


@st.cache_data(show_spinner=False)
def load_default() -> pd.DataFrame:
    """Load the bundled dataset, preferring Parquet over CSV."""
    if DEFAULT_PARQUET.exists():
        try:
            return pd.read_parquet(DEFAULT_PARQUET)
        except Exception:
            pass  # fall through to the CSV copy
    return _downcast(pd.read_csv(DEFAULT_CSV))


def _downcast(df: pd.DataFrame) -> pd.DataFrame:
    """Halve the footprint of coordinate columns.

    float32 holds ~7 significant digits — far more than the ~1 cm of positional
    precision that matters here, and DBSCAN/plotting are unaffected."""
    for col in df.columns:
        if str(df[col].dtype) == "float64":
            df[col] = df[col].astype("float32")
    return df


@st.cache_data(show_spinner=False)
def load_upload(file_bytes: bytes, name: str) -> pd.DataFrame:
    from io import BytesIO

    buf = BytesIO(file_bytes)
    lower = name.lower()
    if lower.endswith((".xlsx", ".xls")):
        return _downcast(pd.read_excel(buf))
    if lower.endswith(".parquet"):
        return pd.read_parquet(buf)
    return _downcast(pd.read_csv(buf))


def _read_wordlist(path: Path) -> list[str]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return [w.strip() for w in fh if w.strip()]


@st.cache_data(show_spinner=False)
def load_tagalog_stopwords() -> list[str]:
    return _read_wordlist(TAGALOG_STOPWORDS)


@st.cache_data(show_spinner=False)
def load_english_stopwords() -> list[str]:
    """The 318-word sklearn ENGLISH_STOP_WORDS list, vendored as plain text.

    It is a static frozenset in sklearn, so shipping it as data lets the text
    pipeline drop its sklearn import — worth ~1s and a large chunk of RSS on
    every page load, since preprocess is on the base import path."""
    return _read_wordlist(ENGLISH_STOPWORDS)


def guess_columns(df: pd.DataFrame) -> tuple[str, str | None, str | None]:
    """Best-effort guess of (text, lon, lat) columns."""
    cols = {c.lower(): c for c in df.columns}
    text = cols.get("text") or cols.get("response") or cols.get("comment")
    if text is None:
        # first object/string column with the longest average length
        obj = [c for c in df.columns if df[c].dtype == object]
        text = max(obj, key=lambda c: df[c].astype(str).str.len().mean(), default=df.columns[0])
    lon = cols.get("lon") or cols.get("longitude") or cols.get("lng") or cols.get("x")
    lat = cols.get("lat") or cols.get("latitude") or cols.get("y")
    return text, lon, lat


def set_active(df: pd.DataFrame, text_col: str, lon_col: str | None,
               lat_col: str | None, source: str) -> None:
    st.session_state[SS_DF] = df
    st.session_state[SS_TEXT_COL] = text_col
    st.session_state[SS_LON_COL] = lon_col
    st.session_state[SS_LAT_COL] = lat_col
    st.session_state[SS_SOURCE] = source
    # Any new dataset invalidates the geo pipeline chain.
    for key in (SS_POINTS, SS_CLUSTERS, SS_GENERALIZED, SS_CLUSTER_TEXT):
        st.session_state.pop(key, None)


def ensure_loaded() -> None:
    """Auto-load the bundled dataset the first time any page runs, so the app is
    useful out of the box during a live training session."""
    if SS_DF not in st.session_state:
        df = load_default()
        text, lon, lat = guess_columns(df)
        set_active(df, text, lon, lat, "Bundled example: PH Health Services Sentiments")


def active_df() -> pd.DataFrame:
    ensure_loaded()
    return st.session_state[SS_DF]


def text_series() -> pd.Series:
    ensure_loaded()
    col = st.session_state[SS_TEXT_COL]
    return st.session_state[SS_DF][col].dropna().astype(str)


def has_geo() -> bool:
    ensure_loaded()
    return bool(st.session_state.get(SS_LON_COL) and st.session_state.get(SS_LAT_COL))
