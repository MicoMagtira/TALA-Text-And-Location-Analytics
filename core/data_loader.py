"""Data loading + shared session state for TALA.

A single 4-column dataset (id, text, lon, lat) feeds both the text-analytics and
geospatial tracks. The bundled example is PH_Health_Services_Sentiments.parquet
(12,000 PH health-service comments with deliberately dirty coordinates, used to
teach CRS/bounds validation).

Concurrency model
-----------------
This app is deployed for a whole workshop cohort on one ~1 GB container, so the
rule is: **session state holds keys and parameters, never DataFrames.**

``st.cache_data`` deep-copies its return value on every call, so the old design —
``st.session_state[SS_DF] = load_default()`` — gave each visitor a private ~6.4 MB
copy of the same immutable file. Thirty trainees meant thirty copies for no
benefit. The dataset is read-only, so it now lives behind ``st.cache_resource``,
which hands every session *the same object*.

That sharing is only safe because nothing mutates it. The contract is:

* Callers treat everything returned by :func:`active_df` / :func:`text_series`
  as **read-only**.
* Any transformation copies first. ``geo.build_points``, ``geo.run_dbscan`` and
  ``geo.clip_to_ph`` already do (``work = df.copy()``, ``out = gdf.copy()``), and
  ``tests/test_concurrency.py`` asserts it stays that way.
"""
from __future__ import annotations

import hashlib
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

BUNDLED_KEY = "bundled"
BUNDLED_LABEL = "Bundled example: PH Health Services Sentiments"

# --- session-state keys (small values only) ----------------------------------
SS_SOURCE_KEY = "data_source_key"   # -> resolves to a *shared* frame via dataset()
SS_TEXT_COL = "text_col"
SS_LON_COL = "lon_col"
SS_LAT_COL = "lat_col"
SS_SOURCE = "data_source"           # human-readable label

# Geo pipeline: session state records only *what was asked for*. The heavy
# GeoDataFrames are derived on demand and shared through core.geo's caches.
SS_POINTS_READY = "geo_points_ready"      # bool — has the user run Lab 1?
SS_CLUSTER_PARAMS = "geo_cluster_params"  # (eps_m, min_samples)
SS_GEN_PARAMS = "geo_gen_params"          # ("grid", cell_m) | ("centroids", bool)

# Upload cache sizing: a workshop cohort works mostly from the bundled file, so a
# handful of distinct uploads at a time is plenty. Bounded so an unexpected burst
# of uploads cannot grow the container without limit.
_UPLOAD_MAX = 6
_UPLOAD_TTL = 3600  # seconds


# ---------------------------------------------------------------------------
# Shared, read-only datasets
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _bundled() -> pd.DataFrame:
    """The bundled dataset — ONE object shared by every session.

    ``cache_resource`` (not ``cache_data``) is deliberate: it returns the same
    object rather than a per-caller copy, which is the whole point. Treat the
    result as immutable."""
    if DEFAULT_PARQUET.exists():
        try:
            return pd.read_parquet(DEFAULT_PARQUET)
        except Exception:
            pass  # fall through to the CSV copy
    return _downcast(pd.read_csv(DEFAULT_CSV))


@st.cache_resource(show_spinner=False, max_entries=_UPLOAD_MAX, ttl=_UPLOAD_TTL)
def _uploaded(key: str, _file_bytes: bytes, _name: str) -> pd.DataFrame:
    """Parse an uploaded file once, keyed on its content digest.

    Streamlit excludes underscore-prefixed arguments from the cache key, so the
    entry is identified by ``key`` alone. That is what lets :func:`dataset`
    look an upload back up later without still holding its bytes. Two trainees
    who upload the same file therefore share one frame, and a single trainee's
    reruns never re-parse."""
    from io import BytesIO

    buf = BytesIO(_file_bytes)
    lower = _name.lower()
    if lower.endswith((".xlsx", ".xls")):
        return _downcast(pd.read_excel(buf))
    if lower.endswith(".parquet"):
        return pd.read_parquet(buf)
    return _downcast(pd.read_csv(buf))


def _downcast(df: pd.DataFrame) -> pd.DataFrame:
    """Halve the footprint of coordinate columns.

    float32 holds ~7 significant digits — far more than the ~1 cm of positional
    precision that matters here, and DBSCAN/plotting are unaffected."""
    for col in df.columns:
        if str(df[col].dtype) == "float64":
            df[col] = df[col].astype("float32")
    return df


def register_upload(file_bytes: bytes, name: str) -> str:
    """Parse + cache an upload, returning the source key that identifies it."""
    digest = hashlib.sha256(file_bytes).hexdigest()[:16]
    key = f"upload:{digest}:{name}"
    _uploaded(key, file_bytes, name)   # populate the cache under this exact key
    return key


def dataset(source_key: str) -> pd.DataFrame | None:
    """Resolve a session's source key to the shared, read-only frame.

    Returns ``None`` if an upload has been evicted (TTL or ``max_entries``), which
    the caller turns into a graceful fall back to the bundled dataset. The dummy
    arguments below are ignored by the cache key; on a hit they are never used,
    and on a miss the empty payload fails to parse, which is exactly the signal
    that the entry is gone."""
    if source_key == BUNDLED_KEY or not source_key:
        return _bundled()
    try:
        return _uploaded(source_key, b"", "")
    except Exception:
        _uploaded.clear()
        return None


# ---------------------------------------------------------------------------
# Word lists (small; cache_data copies are negligible)
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Column inference + active selection
# ---------------------------------------------------------------------------
def guess_columns(df: pd.DataFrame) -> tuple[str, str | None, str | None]:
    """Best-effort guess of (text, lon, lat) columns."""
    cols = {c.lower(): c for c in df.columns}
    text = cols.get("text") or cols.get("response") or cols.get("comment")
    if text is None:
        # first object/string column with the longest average length
        obj = [c for c in df.columns
               if df[c].dtype == object or str(df[c].dtype) == "string"]
        text = max(obj, key=lambda c: df[c].astype(str).str.len().mean(),
                   default=df.columns[0])
    lon = cols.get("lon") or cols.get("longitude") or cols.get("lng") or cols.get("x")
    lat = cols.get("lat") or cols.get("latitude") or cols.get("y")
    return text, lon, lat


def set_active(source_key: str, text_col: str, lon_col: str | None,
               lat_col: str | None, source: str) -> None:
    """Point this session at a dataset. Stores the *key*, never the frame."""
    st.session_state[SS_SOURCE_KEY] = source_key
    st.session_state[SS_TEXT_COL] = text_col
    st.session_state[SS_LON_COL] = lon_col
    st.session_state[SS_LAT_COL] = lat_col
    st.session_state[SS_SOURCE] = source
    reset_geo_chain()


def reset_geo_chain() -> None:
    """A new dataset invalidates the geo pipeline the user has walked."""
    for key in (SS_POINTS_READY, SS_CLUSTER_PARAMS, SS_GEN_PARAMS):
        st.session_state.pop(key, None)


def ensure_loaded() -> None:
    """Point a fresh session at the bundled dataset, so the app is useful out of
    the box during a live training session."""
    if SS_SOURCE_KEY not in st.session_state:
        text, lon, lat = guess_columns(_bundled())
        set_active(BUNDLED_KEY, text, lon, lat, BUNDLED_LABEL)


def source_key() -> str:
    ensure_loaded()
    return st.session_state[SS_SOURCE_KEY]


def active_df() -> pd.DataFrame:
    """The session's dataset. **Read-only** — copy before modifying."""
    ensure_loaded()
    df = dataset(st.session_state[SS_SOURCE_KEY])
    if df is None:
        # The upload aged out of the shared cache; fall back rather than crash.
        st.warning("Your uploaded dataset expired from the shared cache. "
                   "Falling back to the bundled example — re-upload to continue "
                   "with your own file.", icon="⚠️")
        text, lon, lat = guess_columns(_bundled())
        set_active(BUNDLED_KEY, text, lon, lat, BUNDLED_LABEL)
        df = _bundled()
    return df


def text_series() -> pd.Series:
    """The active text column, cleaned of nulls. Read-only."""
    ensure_loaded()
    col = st.session_state[SS_TEXT_COL]
    return active_df()[col].dropna().astype(str)


def has_geo() -> bool:
    ensure_loaded()
    return bool(st.session_state.get(SS_LON_COL) and st.session_state.get(SS_LAT_COL))


def geo_key() -> tuple[str, str, str, str]:
    """The (source, lon, lat, text) tuple that identifies this session's layers.

    Every ``core.geo.*_for()`` helper takes this as its leading arguments, so it
    doubles as the shared-cache key: two trainees on the same dataset and columns
    resolve to the same cached GeoDataFrame."""
    ensure_loaded()
    return (st.session_state[SS_SOURCE_KEY],
            st.session_state[SS_LON_COL],
            st.session_state[SS_LAT_COL],
            st.session_state[SS_TEXT_COL])


def cluster_params() -> tuple[float, int] | tuple[None, None]:
    """DBSCAN parameters this session last ran, or (None, None) if it has not."""
    return st.session_state.get(SS_CLUSTER_PARAMS, (None, None))
