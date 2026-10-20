"""Unit tests for core/compare.py on tiny synthetic inputs."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import compare  # noqa: E402


def test_gi_star_matches_hand_computation():
    # 5 points on a line, 1 km apart; band 1.5 km => neighbours are +-1 and self.
    x = np.array([10.0, 8.0, 1.0, 1.0, 0.0])
    xy = np.column_stack([np.arange(5) * 1000.0, np.zeros(5)])
    z = compare.gi_star(x, xy, radius_m=1500)
    n, xbar = 5, x.mean()                       # 4.0
    s = np.sqrt((x ** 2).mean() - xbar ** 2)    # sqrt(33.2 - 16)
    w = np.array([2, 3, 3, 3, 2])
    sums = np.array([18.0, 19.0, 10.0, 2.0, 1.0])
    expect = (sums - xbar * w) / (s * np.sqrt((n * w - w ** 2) / (n - 1)))
    np.testing.assert_allclose(z, expect, rtol=1e-9)
    # Hand-checked first value: (18 - 4*2) / (sqrt(17.2) * sqrt((10-4)/4))
    assert abs(z[0] - 10 / (np.sqrt(17.2) * np.sqrt(1.5))) < 1e-9
    assert z[0] > 0 > z[4]


def test_gi_star_constant_values_are_zero():
    z = compare.gi_star(np.ones(6), np.random.default_rng(0).random((6, 2)) * 1e4, 3000)
    assert (z == 0).all()


def test_hotspot_class_levels():
    z = np.array([3.0, 2.0, 1.7, 0.0, -1.7, -2.0, -3.0])
    assert list(compare.hotspot_class(z)) == [
        "hot_99", "hot_95", "hot_90", "ns", "cold_90", "cold_95", "cold_99"]


A = ["long wait queue nurse rude", "wait hours queue slow", "queue wait delay"] * 5
B = ["clean room kind doctor", "free medicine nice nurse", "clean facility doctor kind"] * 5


def test_log_odds_antisymmetric():
    ab = compare.log_odds(A, B).set_index("term")
    ba = compare.log_odds(B, A).set_index("term")
    assert set(ab.index) == set(ba.index)
    np.testing.assert_allclose(ab["delta"], -ba.loc[ab.index, "delta"], atol=1e-12)
    np.testing.assert_allclose(ab["z"], -ba.loc[ab.index, "z"], atol=1e-12)
    assert ab["z"].idxmax() in {"wait", "queue", "wait queue"}
    assert ab.loc["clean", "z"] < 0


def test_log_odds_deterministic_and_min_count():
    r1, r2 = compare.log_odds(A, B), compare.log_odds(A, B)
    pd.testing.assert_frame_equal(r1, r2)
    assert (compare.log_odds(A, B, min_count=10)[["count_a", "count_b"]].sum(axis=1) >= 10).all()
    assert compare.log_odds([], B).empty


def test_wilson_bounds_sane():
    lo, hi = compare.wilson_interval([0, 5, 10, 3], [10, 10, 10, 0])
    assert lo[0] == 0 and 0 < hi[0] < 0.4
    assert 0.2 < lo[1] < 0.5 < hi[1] < 0.8
    assert hi[2] == 1 and 0.6 < lo[2] < 1
    assert np.isnan(lo[3])
    big_lo, big_hi = compare.wilson_interval([500], [1000])
    assert (big_hi - big_lo)[0] < 0.07           # narrower with more data


def test_place_sentiment_counts_and_min_n():
    comp = np.array([-0.8, -0.5, 0.6, 0.9, 0.0, -0.1] + [0.5] * 30)
    place = ["A"] * 6 + ["B"] * 30
    out = compare.place_sentiment(comp, place, min_n=10).set_index("place")
    assert out.loc["A", "n"] == 6 and out.loc["A", "pct_neg"] == 100 * 3 / 6
    assert not out.loc["A", "ok"] and out.loc["B", "ok"]
    assert out.loc["B", "pct_neg"] == 0 and out.loc["B", "lo"] == 0
    assert out.loc["A", "lo"] < out.loc["A", "pct_neg"] < out.loc["A", "hi"]
    assert list(compare.place_sentiment(comp, place, min_n=10, drop_small=True)["place"]) == ["B"]
    assert compare.place_sentiment(comp[:2], ["", ""]).empty


def test_aspect_sentiment_filipino_and_english():
    texts = ["The staff were rude. Waited 4 hours for a refill.",
             "Naghintay ako ng matagal. Mabait ang nars, salamat!",
             "Nothing else to say."]
    out = compare.aspect_sentiment(texts, ["X", "X", "X"])
    got = {(r.place, r.aspect): r.n for r in out.itertuples()}
    assert got[("X", "waiting")] == 2          # "Waited 4 hours", "Naghintay ... matagal"
    assert ("X", "staff") in got               # "rude", "nars"
    neg = out.set_index(["place", "aspect"])["pct_neg"]
    assert neg[("X", "staff")] > 0
    assert compare.aspect_sentiment(["x"], [""]).empty


def test_lexicon_has_all_aspects_in_both_languages():
    lex = compare.load_aspects()
    assert set(lex) == {"waiting", "staff", "cost", "medicine", "facilities", "access"}
    assert all(any(t.startswith("fil:") for t in terms) for terms in lex.values())


def test_theme_share_rows_sum_to_one():
    labels = np.array([0, 0, 1, 1, 1, -1, 0])
    place = ["a", "a", "a", "b", "b", "b", ""]
    share = compare.theme_share(labels, place)
    np.testing.assert_allclose(share.sum(axis=1), 1.0)
    assert share.loc["a", 0] == 2 / 3 and share.loc["b", 1] == 1.0
    assert compare.theme_share(labels, place, normalize=False).loc["a", 1] == 1


def test_theme_labels_and_silhouette_on_separable_corpus():
    corpus = (["waiting queue hours slow delay"] * 12 + ["clean doctor kind staff nurse"] * 12
              + ["", "  "])
    labels, res = compare.theme_labels(corpus, k=2)
    assert labels is not None and len(labels) == len(corpus)
    assert labels[-1] == -1 and labels[-2] == -1
    assert len(set(labels[:12])) == 1 and labels[0] != labels[12]
    assert compare.silhouette(corpus, labels) > 0.9


def test_no_heavy_imports_at_module_top_level():
    code = ("import sys; sys.path.insert(0, %r); import core.compare, core.places; "
            "bad=[m for m in ('sklearn','geopandas','shapely','pydeck','nltk','matplotlib') "
            "if m in sys.modules]; print(bad)" % str(ROOT))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert out.stdout.strip().splitlines()[-1] == "[]", out.stdout + out.stderr
