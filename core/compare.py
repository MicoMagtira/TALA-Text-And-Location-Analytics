"""Comparing places: the statistics behind Chapter 2 (Salita).

Pure numpy / pandas / scikit-learn, no Streamlit state, so every function is
unit-testable on a handful of rows. The pages hand in plain arrays and get small
aggregate tables back (privacy-safe: no comment text leaves these functions).

Methods
-------
* :func:`log_odds`        weighted log-odds with an informative Dirichlet prior
                          (Monroe, Colaresi & Quinn 2008, "Fightin' Words").
* :func:`place_sentiment` VADER compound per place with Wilson intervals.
* :func:`aspect_sentiment` sentiment of only the sentences that mention an aspect.
* :func:`gi_star`         Getis-Ord Gi* hotspot z-scores (binary distance band).
* :func:`theme_share`     share of each K-Means theme within each place.

Heavy imports (sklearn) happen inside the functions, as in ``core/geo.py``.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

from .nlp import VADER_THRESHOLD

ASPECTS_FILE = Path(__file__).resolve().parent.parent / "data" / "aspects.json"
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")

# Two-sided critical values for 90 / 95 / 99 % confidence.
Z_CRIT = {90: 1.6449, 95: 1.9600, 99: 2.5758}


# ---------------------------------------------------------------------------
# Contrastive keywords: weighted log-odds, informative Dirichlet prior
# ---------------------------------------------------------------------------
def log_odds(docs_a, docs_b, prior=None, prior_strength: float = 500.0,
             min_count: int = 1, ngram_range: tuple[int, int] = (1, 2)) -> pd.DataFrame:
    """Which terms separate group A from group B?

    ``docs_a``/``docs_b`` are lists of (already cleaned) documents. ``prior`` is an
    optional background corpus (e.g. every comment); by default it is A + B, which
    makes the result exactly antisymmetric: ``log_odds(A, B) == -log_odds(B, A)``.

    For each term w, with counts y_a, y_b, totals n_a, n_b and Dirichlet prior
    alpha_w (scaled so sum(alpha) = ``prior_strength``)::

        delta = log((y_a+alpha_w)/(n_a+a0-y_a-alpha_w))
              - log((y_b+alpha_w)/(n_b+a0-y_b-alpha_w))
        var   = 1/(y_a+alpha_w) + 1/(y_b+alpha_w)
        z     = delta / sqrt(var)

    The prior is what stops rare words from topping the list: a term seen twice in
    A and never in B is shrunk toward the background rate. Positive z means "more
    typical of A". Returns ``term, delta, z, count_a, count_b`` sorted by z."""
    from sklearn.feature_extraction.text import CountVectorizer

    a = [str(d) for d in docs_a if str(d).strip()]
    b = [str(d) for d in docs_b if str(d).strip()]
    cols = ["term", "delta", "z", "count_a", "count_b"]
    if not a or not b:
        return pd.DataFrame(columns=cols)
    bg = [str(d) for d in prior if str(d).strip()] if prior is not None else a + b

    vec = CountVectorizer(ngram_range=ngram_range, lowercase=True)
    try:
        vec.fit(a + b + bg)
    except ValueError:
        return pd.DataFrame(columns=cols)
    ya = np.asarray(vec.transform(a).sum(axis=0)).ravel().astype(float)
    yb = np.asarray(vec.transform(b).sum(axis=0)).ravel().astype(float)
    yp = np.asarray(vec.transform(bg).sum(axis=0)).ravel().astype(float)
    alpha = yp * (prior_strength / yp.sum())
    a0 = alpha.sum()
    na, nb = ya.sum(), yb.sum()

    pa, pb = ya + alpha, yb + alpha
    delta = np.log(pa / (na + a0 - pa)) - np.log(pb / (nb + a0 - pb))
    z = delta / np.sqrt(1.0 / pa + 1.0 / pb)
    out = pd.DataFrame({"term": vec.get_feature_names_out(), "delta": delta, "z": z,
                        "count_a": ya.astype(int), "count_b": yb.astype(int)})
    out = out[(out["count_a"] + out["count_b"]) >= min_count]
    return out.sort_values(["z", "term"], ascending=[False, True]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Sentiment per place
# ---------------------------------------------------------------------------
def wilson_interval(k, n, z: float = 1.96):
    """Wilson score interval for a proportion k/n (vectorised). Returns (lo, hi) in 0-1.

    Preferred over the normal approximation because places with few comments or
    proportions near 0/1 would otherwise get intervals outside [0, 1]."""
    k = np.asarray(k, dtype=float)
    n = np.asarray(n, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        p = np.where(n > 0, k / n, 0.0)
        denom = 1 + z * z / n
        centre = (p + z * z / (2 * n)) / denom
        half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    lo = np.where(n > 0, np.clip(centre - half, 0, 1), np.nan)
    hi = np.where(n > 0, np.clip(centre + half, 0, 1), np.nan)
    return lo, hi


def vader_compound(texts) -> np.ndarray:
    """VADER compound score per text, using ``core.nlp``'s shared analyzer."""
    from .nlp import _vader

    sia = _vader()
    return np.array([sia.polarity_scores(str(t))["compound"] for t in texts], dtype=float)


def place_sentiment(compound, place, min_n: int = 30,
                    drop_small: bool = False) -> pd.DataFrame:
    """Per-place sentiment: ``place, n, mean, pct_neg, lo, hi, ok``.

    ``pct_neg`` is the percentage of comments with compound <= -0.05 (VADER's own
    negative cut-off); ``lo``/``hi`` are its 95 % Wilson bounds, also in percent.
    Places with fewer than ``min_n`` comments stay in the table with ``ok=False``
    so the page can grey them out and say why; ``drop_small`` removes them.
    Rows with an empty place label are ignored."""
    df = pd.DataFrame({"place": np.asarray(place, dtype=object),
                       "c": np.asarray(compound, dtype=float)})
    df = df[(df["place"] != "") & df["place"].notna() & df["c"].notna()]
    if df.empty:
        return pd.DataFrame(columns=["place", "n", "mean", "pct_neg", "lo", "hi", "ok"])
    df["neg"] = df["c"] <= -VADER_THRESHOLD
    g = df.groupby("place").agg(n=("c", "size"), mean=("c", "mean"), neg=("neg", "sum"))
    lo, hi = wilson_interval(g["neg"].to_numpy(), g["n"].to_numpy())
    g["pct_neg"] = 100 * g["neg"] / g["n"]
    g["lo"], g["hi"] = 100 * lo, 100 * hi
    g["ok"] = g["n"] >= min_n
    g = g.drop(columns="neg").reset_index()
    if drop_small:
        g = g[g["ok"]]
    return g.sort_values(["pct_neg", "place"], ascending=[False, True]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Aspect sentiment
# ---------------------------------------------------------------------------
def load_aspects(path: Path | str | None = None) -> dict[str, list[str]]:
    """Aspect lexicon from ``data/aspects.json`` as ``{aspect: [terms]}``.

    Filipino terms are tagged with a ``fil:`` prefix so the matcher can allow a
    short affix before them (``naghintay``, ``hinihintay``)."""
    raw = json.loads(Path(path or ASPECTS_FILE).read_text(encoding="utf-8"))
    out = {}
    for aspect, langs in raw.items():
        if aspect.startswith("_"):
            continue
        out[aspect] = list(langs.get("en", [])) + [f"fil:{t}" for t in langs.get("fil", [])]
    return out


def _aspect_regex(terms: list[str]) -> re.Pattern:
    en, fil = [], []
    for t in terms:
        (fil if t.startswith("fil:") else en).append(re.escape(t.removeprefix("fil:")))
    parts = []
    if en:
        parts.append(r"\b(?:" + "|".join(en) + r")(?:s|es|ed|d|ing)?\b")
    if fil:
        parts.append(r"\b\w{0,5}(?:" + "|".join(fil) + r")\b")
    return re.compile("|".join(parts), re.IGNORECASE)


def aspect_sentiment(texts, place, lexicon: dict | None = None,
                     min_n: int = 1) -> pd.DataFrame:
    """Sentiment of the sentences that mention each aspect, per place.

    Splits every comment into sentences, keeps those matching an aspect's terms
    (English + Filipino) and scores them with VADER. One sentence can count for
    several aspects. Returns ``place, aspect, n, mean, pct_neg`` where ``n`` is the
    number of matching sentences; combinations with ``n < min_n`` are dropped."""
    lex = lexicon if lexicon is not None else load_aspects()
    rx = {a: _aspect_regex(list(terms)) for a, terms in lex.items()}
    rows_p, rows_s = [], []
    for t, p in zip(texts, place):
        if not isinstance(p, str) or p == "":
            continue
        for s in _SENT_SPLIT.split(str(t)):
            if s.strip():
                rows_p.append(p)
                rows_s.append(s)
    cols = ["place", "aspect", "n", "mean", "pct_neg"]
    if not rows_s:
        return pd.DataFrame(columns=cols)
    comp = vader_compound(rows_s)
    sent = pd.DataFrame({"place": rows_p, "s": rows_s, "c": comp})
    parts = []
    for aspect, pattern in rx.items():
        hit = sent[sent["s"].map(lambda s: bool(pattern.search(s)))]
        if hit.empty:
            continue
        g = hit.groupby("place").agg(n=("c", "size"), mean=("c", "mean"),
                                     neg=("c", lambda c: float((c <= -VADER_THRESHOLD).sum())))
        g["pct_neg"] = 100 * g["neg"] / g["n"]
        g["aspect"] = aspect
        parts.append(g.drop(columns="neg").reset_index())
    if not parts:
        return pd.DataFrame(columns=cols)
    out = pd.concat(parts, ignore_index=True)[cols]
    out = out[out["n"] >= min_n]
    return out.sort_values(["aspect", "place"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Getis-Ord Gi* hotspots
# ---------------------------------------------------------------------------
def gi_star(values, xy_m, radius_m: float) -> np.ndarray:
    """Getis-Ord Gi* z-score per location, binary distance-band weights.

    ``w_ij = 1`` when location j is within ``radius_m`` of i (i itself included,
    which is what the star means). With n locations, mean X-bar and standard
    deviation S of the values::

        Gi*_i = (sum_j w_ij x_j - X-bar * W_i)
                / (S * sqrt((n * sum_j w_ij^2 - W_i^2) / (n - 1)))

    where W_i = sum_j w_ij. For binary weights sum w^2 = W_i. Neighbours come
    from a ``BallTree`` so a few thousand grid cells stay fast. Returns zeros when
    the values do not vary (S = 0) or a location's band covers everything."""
    from sklearn.neighbors import BallTree

    x = np.asarray(values, dtype=float)
    xy = np.asarray(xy_m, dtype=float).reshape(len(x), 2)
    n = len(x)
    if n < 2:
        return np.zeros(n)
    xbar = x.mean()
    s = np.sqrt((x ** 2).mean() - xbar ** 2)
    if s == 0:
        return np.zeros(n)
    tree = BallTree(xy)
    neigh = tree.query_radius(xy, r=radius_m)
    z = np.zeros(n)
    for i, idx in enumerate(neigh):
        w = len(idx)
        denom = s * np.sqrt((n * w - w * w) / (n - 1))
        if denom > 0:
            z[i] = (x[idx].sum() - xbar * w) / denom
    return z


def hotspot_class(z) -> np.ndarray:
    """Label z-scores ``hot_99/hot_95/hot_90``, ``cold_99/cold_95/cold_90`` or ``ns``
    (two-sided critical z of 2.576 / 1.960 / 1.645).

    Note for the Learn panel: thousands of cells are tested at once, so a few "hot"
    cells at 90 % are expected by chance; the 99 % class is the safer reading."""
    z = np.asarray(z, dtype=float)
    out = np.full(z.shape, "ns", dtype=object)
    for level in (90, 95, 99):            # later (stricter) levels overwrite
        out[z >= Z_CRIT[level]] = f"hot_{level}"
        out[z <= -Z_CRIT[level]] = f"cold_{level}"
    return out


# ---------------------------------------------------------------------------
# Themes per place
# ---------------------------------------------------------------------------
def theme_labels(corpus, k: int = 4, seed: int = 42):
    """K-Means theme per document via ``core.nlp.tfidf_kmeans`` (reused, not copied).

    ``tfidf_kmeans`` silently drops blank documents, so its labels are shorter than
    the corpus. This realigns them: returns ``(labels, result)`` where ``labels`` has
    one entry per input document (``-1`` for blanks) and ``result`` is the raw dict
    (top terms, sizes), or ``(None, None)`` when there is too little text."""
    from .nlp import tfidf_kmeans

    docs = tuple(str(d) for d in corpus)
    res = tfidf_kmeans(docs, k=k, seed=seed)
    if res is None:
        return None, None
    labels = np.full(len(docs), -1, dtype=int)
    labels[[i for i, d in enumerate(docs) if d.strip()]] = res["labels"]
    return labels, res


def theme_share(labels, place, normalize: bool = True) -> pd.DataFrame:
    """Rows = places, columns = theme ids, values = share (rows sum to 1) or counts.

    Documents with label ``-1`` or an empty place are ignored."""
    df = pd.DataFrame({"place": np.asarray(place, dtype=object),
                       "theme": np.asarray(labels)})
    df = df[(df["theme"] >= 0) & (df["place"] != "") & df["place"].notna()]
    tab = pd.crosstab(df["place"], df["theme"])
    if normalize and len(tab):
        tab = tab.div(tab.sum(axis=1), axis=0)
    return tab


def silhouette(corpus, labels, sample: int = 2000, seed: int = 42) -> float:
    """Silhouette of a theme assignment on TF-IDF vectors (cosine), sampled for speed.

    The same vectorizer settings as ``tfidf_kmeans`` are used, so the score describes
    the clustering the user actually sees. Returns NaN with fewer than two themes."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import silhouette_score

    labels = np.asarray(labels)
    keep = [i for i, (d, lab) in enumerate(zip(corpus, labels)) if str(d).strip() and lab >= 0]
    if len({labels[i] for i in keep}) < 2:
        return float("nan")
    docs = [str(corpus[i]) for i in keep]
    X = TfidfVectorizer(ngram_range=(1, 2), max_df=0.9, min_df=3,
                        max_features=1200).fit_transform(docs)
    try:
        return float(silhouette_score(X, labels[keep], metric="cosine",
                                      sample_size=min(sample, len(docs) - 1),
                                      random_state=seed))
    except ValueError:
        return float("nan")
