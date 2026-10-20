"""Places: read where a comment says it is from, check it against the GPS.

TALA is place-first. Steps 2-3 of the journey turn free text into *places*:

1. :func:`geoparse` finds the Philippine place a comment names (longest
   title-case match against ``data/ph_gazetteer.csv``).
2. :func:`text_vs_gps` compares that place with the row's lon/lat.
3. :func:`locate` decides which coordinates Chapter 2 should use (the GPS, the
   named place, or only rows where the two agree).
4. :func:`assign_place` gives every row a place label: its Region (from the
   gazetteer) or its DBSCAN Cluster.

Why a rule-based parser and not NER: the vocabulary is closed (a few hundred
place names), the comments are short and consistently capitalised, and the
parser must be deterministic and explainable to a student in one paragraph.

Concurrency follows ``core/geo.py``: the pure functions take DataFrames; the
``*_for(source_key, ...)`` wrappers are ``cache_resource``-backed, keyed on the
dataset key and parameters (never on language), and return shared **read-only**
frames. Session state keeps only the parameters, never the frames.

Heavy deps (shapely, geopandas, sklearn) import inside the functions that need
them. Place data (c) GeoNames, CC BY 4.0.
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

GAZETTEER_FILE = Path(__file__).resolve().parent.parent / "data" / "ph_gazetteer.csv"
STOPWORD_FILE = Path(__file__).resolve().parent.parent / "data" / "english_stop_words.txt"

# "Brgy. Mabini" names a barangay, not a municipality: the word after one of
# these is skipped so it cannot be mistaken for a gazetteer place.
STOP_PREFIXES = frozenset({"brgy", "bgy", "barangay", "purok", "sitio"})
# Lower-case words allowed *inside* a place name ("Cagayan de Oro").
_CONNECTORS = frozenset({"de", "del", "dela", "ng", "sa", "y", "of", "la", "las", "los", "da"})
# Municipality names that are also everyday English words: matching them as a
# single capitalised token ("Bay", "Real") would flood the result with noise.
_COMMON_WORDS = frozenset({"bay", "real", "hope", "joy", "mercy", "banga", "bula", "lupi"})
MAX_TOKENS = 4
# A bare name resolves to its most populous namesake when that is >= 1.5x the next.
DOMINANCE = 1.5
_SAINT = re.compile(r"^(San|Santa|Santo|Sta|Sto)\b", re.I)

_SPECIFICITY = {"municipality": 3, "city": 3, "province": 2, "region": 1}
_TOKEN = re.compile(r"[^\W\d_](?:[\w'’\-]*\w)?")
_COLS = ["place", "kind", "province", "region", "lon_t", "lat_t", "status"]

_DERIVED_MAX, _DERIVED_TTL = 6, 1800


def _norm(token: str) -> str:
    """Lower-case, accent-free, punctuation-free: 'Las Piñas' -> 'las pinas'."""
    t = unicodedata.normalize("NFKD", token.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", t)


def _key(text: str) -> str:
    return " ".join(k for k in (_norm(w) for w in text.split()) if k)


# ---------------------------------------------------------------------------
# Gazetteer
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_gazetteer() -> pd.DataFrame:
    """The bundled gazetteer (regions, provinces, cities, municipalities).

    Shared and read-only. Missing file -> empty frame, so the page can say so
    instead of crashing."""
    cols = ["name", "aliases", "kind", "province", "region", "lon", "lat"]
    if not GAZETTEER_FILE.exists():
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(GAZETTEER_FILE, keep_default_na=False)
    df["lon"] = df["lon"].astype(float)
    df["lat"] = df["lat"].astype(float)
    return df


@st.cache_resource(show_spinner=False)
def _index() -> dict:
    """Lookup structures built once: normalised name/alias -> gazetteer rows."""
    gz = load_gazetteer()
    stops = set()
    if STOPWORD_FILE.exists():
        stops = {_norm(w) for w in STOPWORD_FILE.read_text(encoding="utf-8").split()}
    stops |= _COMMON_WORDS
    table: dict[str, list[int]] = {}
    for i, (name, aliases, kind) in enumerate(zip(gz["name"], gz["aliases"], gz["kind"])):
        forms = [name] + [a for a in str(aliases).split("|") if a]
        for form in dict.fromkeys(_key(f) for f in forms):
            if not form:
                continue
            if kind == "municipality" and " " not in form and form in stops:
                continue
            table.setdefault(form, []).append(i)
    return {"table": table,
            "pop": gz["pop"].astype(int).tolist() if "pop" in gz else [0] * len(gz),
            "kind": gz["kind"].tolist(), "name": gz["name"].tolist(),
            "province": gz["province"].tolist(), "region": gz["region"].tolist(),
            "lon": gz["lon"].to_numpy(), "lat": gz["lat"].to_numpy()}


# ---------------------------------------------------------------------------
# Geoparsing
# ---------------------------------------------------------------------------
def _candidates(text: str, ix: dict) -> list[tuple[str, list[int]]]:
    """Scan one comment; return ``[(key, [gazetteer rows])]`` in reading order."""
    toks = [(m.group(), _norm(m.group())) for m in _TOKEN.finditer(text)]
    table = ix["table"]
    n = len(toks)

    def longest(i: int):
        # A name starts with a capital, ends with a capital, and may contain
        # lower-case connectors in between ("Davao de Oro").
        if not toks[i][0][0].isupper():
            return None
        for length in range(min(MAX_TOKENS, n - i), 0, -1):
            span = toks[i:i + length]
            if length > 1 and (span[-1][0] in _CONNECTORS or not span[-1][0][0].isupper()):
                continue
            if any(not (w[0].isupper() or w in _CONNECTORS) for w, _ in span[1:-1]):
                continue
            key = " ".join(k for _, k in span if k)
            if key in table:
                return key, length
        return None

    out, i = [], 0
    while i < n:
        raw, norm = toks[i]
        if norm in STOP_PREFIXES:
            # skip the barangay/purok/sitio name that follows
            nxt = longest(i + 1) if i + 1 < n else None
            if nxt:
                i += 1 + nxt[1]
            elif i + 1 < n and toks[i + 1][0][0].isupper():
                i += 2
            else:
                i += 1
            continue
        hit = longest(i)
        if hit:
            out.append((hit[0], list(table[hit[0]])))
            i += hit[1]
        else:
            i += 1
    return out


def _pick(rows: list[int], hints_prov: set, hints_reg: set, ix: dict) -> int | None:
    """One gazetteer row out of several same-named candidates, or ``None``."""
    if len(rows) == 1:
        return rows[0]
    kinds = ix["kind"]
    top = [r for r in rows if kinds[r] in ("region", "province")]
    if len(top) == 1:                      # "Quezon" the province beats 6 towns
        return top[0]
    rows = top or rows
    for hints, col in ((hints_prov, "province"), (hints_reg, "region")):
        sel = [r for r in rows if ix[col][r] in hints]
        if len(sel) == 1:
            return sel[0]
        if sel:
            rows = sel
    # "Bacolod" the city beats Bacolod, Lanao del Norte; saint names never resolve
    # this way (San Fernando stays ambiguous without a province).
    by_pop = sorted(rows, key=lambda r: -ix["pop"][r])
    if (not _SAINT.match(ix["name"][by_pop[0]])
            and ix["pop"][by_pop[0]] >= DOMINANCE * max(ix["pop"][by_pop[1]], 1)):
        return by_pop[0]
    if len({(ix["province"][r], ix["kind"][r]) for r in rows}) == 1:
        return rows[0]                     # duplicate points of the same place
    return None


def _parse_one(text, ix) -> tuple:
    cands = _candidates(text, ix) if isinstance(text, str) else []
    if not cands:
        return ("", "", "", "", np.nan, np.nan, "no_place")
    resolved: list[int | None] = [_pick(rows, set(), set(), ix) if len(rows) == 1 else None
                                  for _, rows in cands]
    # Second pass: ambiguous names borrow a province/region named elsewhere in
    # the same comment ("San Fernando, Pampanga").
    for _ in range(2):
        known = [r for r in resolved if r is not None]
        hp = {ix["province"][r] for r in known if ix["province"][r]}
        hr = {ix["region"][r] for r in known if ix["region"][r]}
        for j, (_, rows) in enumerate(cands):
            if resolved[j] is None:
                resolved[j] = _pick(rows, hp, hr, ix)
    good = [(j, r) for j, r in enumerate(resolved) if r is not None]
    if good:
        j, r = max(good, key=lambda t: (_SPECIFICITY[ix["kind"][t[1]]], -t[0]))
        return (ix["name"][r], ix["kind"][r], ix["province"][r], ix["region"][r],
                float(ix["lon"][r]), float(ix["lat"][r]), "found")
    rows = cands[0][1]
    return (ix["name"][rows[0]], "", "", "", np.nan, np.nan, "ambiguous")


def geoparse(texts) -> pd.DataFrame:
    """Name the place each comment is about.

    Returns one row per input, same index when ``texts`` is a Series, with
    ``place, kind, province, region, lon_t, lat_t, status``. ``status`` is
    ``found``, ``ambiguous`` (e.g. a bare "San Fernando" with no province nearby;
    place filled, coordinates left empty) or ``no_place``. When a comment names
    several places the most specific resolved one wins (town > province > region),
    earliest first. Deterministic: same texts, same table."""
    index = texts.index if isinstance(texts, pd.Series) else None
    ix = _index()
    rows = [_parse_one(t, ix) for t in texts]
    out = pd.DataFrame(rows, columns=_COLS, index=index)
    return out


# ---------------------------------------------------------------------------
# Text vs GPS
# ---------------------------------------------------------------------------
def haversine_km(lon1, lat1, lon2, lat2) -> np.ndarray:
    lon1, lat1, lon2, lat2 = map(lambda a: np.radians(np.asarray(a, dtype=float)),
                                 (lon1, lat1, lon2, lat2))
    a = (np.sin((lat2 - lat1) / 2) ** 2
         + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2)
    return 6371.0088 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def _on_ph_land(lon: np.ndarray, lat: np.ndarray) -> np.ndarray:
    """Vectorised point-in-PH-land, reusing ``core.geo``'s land polygon."""
    import shapely

    from . import geo

    ok = np.isfinite(lon) & np.isfinite(lat)
    out = np.zeros(len(lon), dtype=bool)
    if ok.any():
        out[ok] = shapely.contains_xy(geo.ph_land(), lon[ok], lat[ok])
    return out


def text_vs_gps(parsed: pd.DataFrame, lon, lat, km: float = 50.0) -> pd.DataFrame:
    """Compare the named place with the GPS point, row by row.

    Columns: ``status``, ``dist_km`` (GPS to named place; NaN unless both exist),
    ``gps_ok``. Status priority: ``gps_invalid`` (missing, out of lon/lat range or
    off PH land) > ``no_place`` > ``ambiguous`` > ``agree`` (within ``km``) or
    ``disagree``. An invalid GPS wins because it needs repair whatever the text says;
    :func:`locate` then uses the named place when there is one."""
    lo = pd.to_numeric(pd.Series(np.asarray(lon)), errors="coerce").to_numpy(float)
    la = pd.to_numeric(pd.Series(np.asarray(lat)), errors="coerce").to_numpy(float)
    in_range = (np.abs(lo) <= 180) & (np.abs(la) <= 90)
    lo = np.where(in_range, lo, np.nan)
    la = np.where(in_range, la, np.nan)
    gps_ok = _on_ph_land(lo, la)

    lon_t = parsed["lon_t"].to_numpy(float)
    lat_t = parsed["lat_t"].to_numpy(float)
    have = np.isfinite(lo) & np.isfinite(lat_t) & np.isfinite(lon_t) & np.isfinite(la)
    dist = np.full(len(parsed), np.nan)
    dist[have] = haversine_km(lo[have], la[have], lon_t[have], lat_t[have])

    st_ = parsed["status"].to_numpy()
    status = np.where(~gps_ok, "gps_invalid",
             np.where(st_ == "no_place", "no_place",
             np.where(st_ == "ambiguous", "ambiguous",
             np.where(dist <= km, "agree", "disagree"))))
    return pd.DataFrame({"status": status, "dist_km": dist, "gps_ok": gps_ok},
                        index=parsed.index)


def locate(parsed: pd.DataFrame, check: pd.DataFrame, lon, lat,
           mode: str = "repaired") -> pd.DataFrame:
    """The coordinates Chapter 2 uses. Columns ``lon``, ``lat``, ``source``.

    * ``repaired`` (default): the GPS when it is valid and agrees or no place is
      named; the named place's coordinates when the GPS is invalid or disagrees.
    * ``gps``: validated, land-clipped GPS only.
    * ``agree``: only rows where text and GPS agree.

    Rows that end up with no usable point get NaN coordinates and an empty source,
    so the row index stays aligned with the dataset."""
    if mode not in ("repaired", "gps", "agree"):
        raise ValueError(f"unknown mode {mode!r}")
    lo = pd.to_numeric(pd.Series(np.asarray(lon)), errors="coerce").to_numpy(float)
    la = pd.to_numeric(pd.Series(np.asarray(lat)), errors="coerce").to_numpy(float)
    s = check["status"].to_numpy()
    gps_ok = check["gps_ok"].to_numpy(bool)
    place_ok = np.isfinite(parsed["lon_t"].to_numpy(float))
    if mode == "gps":
        use_gps, use_place = gps_ok, np.zeros(len(s), bool)
    elif mode == "agree":
        use_gps, use_place = s == "agree", np.zeros(len(s), bool)
    else:
        use_gps = gps_ok & (s != "disagree")
        use_place = ~use_gps & place_ok
    lon_o = np.where(use_gps, lo, np.where(use_place, parsed["lon_t"].to_numpy(float), np.nan))
    lat_o = np.where(use_gps, la, np.where(use_place, parsed["lat_t"].to_numpy(float), np.nan))
    src = np.where(use_gps, "gps", np.where(use_place, "place", ""))
    return pd.DataFrame({"lon": lon_o, "lat": lat_o, "source": src}, index=parsed.index)


def _nearest_region(lon: np.ndarray, lat: np.ndarray) -> np.ndarray:
    gz = load_gazetteer()
    reg = gz[gz["kind"] == "region"].reset_index(drop=True)
    out = np.full(len(lon), "", dtype=object)
    ok = np.isfinite(lon) & np.isfinite(lat)
    if ok.any() and len(reg):
        d = haversine_km(lon[ok][:, None], lat[ok][:, None],
                         reg["lon"].to_numpy()[None, :], reg["lat"].to_numpy()[None, :])
        out[ok] = reg["name"].to_numpy()[d.argmin(axis=1)]
    return out


def assign_place(located: pd.DataFrame, parsed: pd.DataFrame, unit: str = "region",
                 eps_m: float = 15000.0, min_samples: int = 10) -> pd.Series:
    """A place label per row. ``""`` means unassigned (no point, or DBSCAN noise).

    * ``region``: the region of the named place; rows without one take the nearest
      region centroid to their located point.
    * ``cluster``: ``"Cluster N"`` from :func:`core.geo.run_dbscan` on the located
      points (the ML route)."""
    if unit == "region":
        lo = located["lon"].to_numpy(float)
        la = located["lat"].to_numpy(float)
        named = parsed["region"].to_numpy(object)
        nearest = _nearest_region(lo, la)
        label = np.where(named != "", named, nearest)
        label = np.where((named == "") & ~np.isfinite(lo), "", label)
        return pd.Series(label, index=located.index, name="place")
    if unit != "cluster":
        raise ValueError(f"unknown unit {unit!r}")

    import geopandas as gpd

    from . import geo

    ok = located["lon"].notna().to_numpy()
    out = pd.Series("", index=located.index, name="place", dtype=object)
    if ok.sum() < 2:
        return out
    pts = gpd.GeoDataFrame(
        {"row": np.flatnonzero(ok)},
        geometry=gpd.points_from_xy(located["lon"][ok], located["lat"][ok]), crs="EPSG:4326")
    clustered, _ = geo.run_dbscan(pts, eps_m=eps_m, min_samples=min_samples)
    ids = clustered["cluster_id"].to_numpy()
    labels = np.where(ids >= 0, [f"Cluster {i}" for i in ids], "")
    out.iloc[clustered["row"].to_numpy()] = labels
    return out


def place_points(located: pd.DataFrame, labels: pd.Series, unit: str = "region") -> pd.DataFrame:
    """One bubble per place: ``place, n, lon, lat``. Regions sit at their
    gazetteer centroid (no polygons); clusters at the mean of their members."""
    df = pd.DataFrame({"place": labels.to_numpy(), "lon": located["lon"].to_numpy(),
                       "lat": located["lat"].to_numpy()})
    df = df[df["place"] != ""]
    g = df.groupby("place").agg(n=("place", "size"), lon=("lon", "mean"), lat=("lat", "mean"))
    g = g.reset_index()
    if unit == "region":
        gz = load_gazetteer()
        reg = gz[gz["kind"] == "region"].set_index("name")
        g["lon"] = g["place"].map(reg["lon"]).fillna(g["lon"])
        g["lat"] = g["place"].map(reg["lat"]).fillna(g["lat"])
    return g.sort_values(["n", "place"], ascending=[False, True]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Shared pipeline entry points (cached on dataset key + parameters)
# ---------------------------------------------------------------------------
def _dataset(source_key: str):
    from . import data_loader as dl

    return dl.dataset(source_key)


@st.cache_resource(show_spinner=False, max_entries=_DERIVED_MAX, ttl=_DERIVED_TTL)
def parsed_for(source_key: str, text_col: str) -> pd.DataFrame | None:
    """Step 2a: geoparse of the dataset's text column. Read-only, shared."""
    df = _dataset(source_key)
    if df is None or text_col not in df.columns:
        return None
    return geoparse(df[text_col].reset_index(drop=True))


@st.cache_resource(show_spinner=False, max_entries=_DERIVED_MAX, ttl=_DERIVED_TTL)
def check_for(source_key: str, lon_col: str, lat_col: str, text_col: str,
              km: float) -> pd.DataFrame | None:
    """Step 2b: text-vs-GPS status per row. Read-only, shared."""
    df = _dataset(source_key)
    parsed = parsed_for(source_key, text_col)
    if df is None or parsed is None:
        return None
    return text_vs_gps(parsed, df[lon_col], df[lat_col], km=km)


@st.cache_resource(show_spinner=False, max_entries=_DERIVED_MAX, ttl=_DERIVED_TTL)
def locate_for(source_key: str, lon_col: str, lat_col: str, text_col: str,
               km: float, mode: str) -> pd.DataFrame | None:
    """Step 2c: the coordinates every Chapter 2 page uses. Read-only, shared."""
    df = _dataset(source_key)
    parsed = parsed_for(source_key, text_col)
    check = check_for(source_key, lon_col, lat_col, text_col, km)
    if df is None or parsed is None or check is None:
        return None
    return locate(parsed, check, df[lon_col], df[lat_col], mode=mode)


@st.cache_resource(show_spinner=False, max_entries=_DERIVED_MAX, ttl=_DERIVED_TTL)
def assign_place_for(source_key: str, lon_col: str, lat_col: str, text_col: str,
                     km: float, mode: str, unit: str, eps_m: float,
                     min_samples: int) -> pd.Series | None:
    """Step 3: place label per row. Read-only, shared."""
    located = locate_for(source_key, lon_col, lat_col, text_col, km, mode)
    parsed = parsed_for(source_key, text_col)
    if located is None or parsed is None:
        return None
    return assign_place(located, parsed, unit=unit, eps_m=eps_m, min_samples=min_samples)


# ---------------------------------------------------------------------------
# Journey state: the Step 2/3 choices every Chapter 2 page reads
# ---------------------------------------------------------------------------
# Step 2 (Text vs GPS) and Step 3 (Places) write these keys; Chapter 2 pages only
# read them through the accessors below. A page opened cold gets the defaults,
# which is what "TALA ran them with default settings" refers to. Values are plain
# parameters, never frames, so they persist and cache-key cleanly.
SS_KM = "place_km"            # agree threshold in km (Step 2)
SS_MODE = "place_mode"        # "repaired" | "gps" | "agree" (Step 2)
SS_UNIT = "place_unit"        # "region" | "cluster" (Step 3)
DEFAULT_KM = 50.0
DEFAULT_MODE = "repaired"
DEFAULT_UNIT = "region"
MODES = ("repaired", "gps", "agree")
UNITS = ("region", "cluster")


def params() -> dict:
    """The active journey parameters, defaults filled in.

    Cluster parameters reuse ``data_loader.SS_CLUSTER_PARAMS`` (eps_m,
    min_samples) so the DBSCAN controls keep one home."""
    from . import data_loader as dl

    eps_m, min_samples = st.session_state.get(
        dl.SS_CLUSTER_PARAMS, (dl.DEFAULT_EPS_M, dl.DEFAULT_MIN_SAMPLES))
    return {
        "source_key": st.session_state.get(dl.SS_SOURCE_KEY, dl.BUNDLED_KEY),
        "text_col": st.session_state.get(dl.SS_TEXT_COL),
        "lon_col": st.session_state.get(dl.SS_LON_COL),
        "lat_col": st.session_state.get(dl.SS_LAT_COL),
        "km": float(st.session_state.get(SS_KM, DEFAULT_KM)),
        "mode": st.session_state.get(SS_MODE, DEFAULT_MODE),
        "unit": st.session_state.get(SS_UNIT, DEFAULT_UNIT),
        "eps_m": float(eps_m),
        "min_samples": int(min_samples),
    }


def has_geo() -> bool:
    """Whether the active dataset has text and both coordinate columns mapped."""
    p = params()
    return bool(p["text_col"] and p["lon_col"] and p["lat_col"])


def active_parsed() -> pd.DataFrame | None:
    p = params()
    return parsed_for(p["source_key"], p["text_col"]) if p["text_col"] else None


def active_check() -> pd.DataFrame | None:
    p = params()
    if not has_geo():
        return None
    return check_for(p["source_key"], p["lon_col"], p["lat_col"], p["text_col"], p["km"])


def active_located() -> pd.DataFrame | None:
    """Coordinates per row (``lon, lat, source``) under the chosen location source."""
    p = params()
    if not has_geo():
        return None
    return locate_for(p["source_key"], p["lon_col"], p["lat_col"], p["text_col"],
                      p["km"], p["mode"])


def active_places() -> pd.Series | None:
    """Place label per row ("" = unassigned/noise) under the chosen unit."""
    p = params()
    if not has_geo():
        return None
    return assign_place_for(p["source_key"], p["lon_col"], p["lat_col"], p["text_col"],
                            p["km"], p["mode"], p["unit"], p["eps_m"], p["min_samples"])
