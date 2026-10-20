"""Tests for the gazetteer, geoparser and text-vs-GPS check (core/places.py)."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import places  # noqa: E402


def parse(*texts):
    return places.geoparse(list(texts))


def test_gazetteer_shape_and_size():
    gz = places.load_gazetteer()
    assert list(gz.columns[:7]) == ["name", "aliases", "kind", "province", "region", "lon", "lat"]
    counts = gz["kind"].value_counts()
    assert counts["province"] == 82 and counts["region"] == 17
    assert counts["city"] >= 140 and counts["municipality"] > 1000
    assert GAZ_BYTES < 1_000_000
    assert gz["lon"].between(114, 128).all() and gz["lat"].between(4, 22).all()


GAZ_BYTES = places.GAZETTEER_FILE.stat().st_size


def test_simple_city_province_and_aliases():
    p = parse("Checked in at the clinic (in Cagayan de Oro).",
              "Visited a hospital in Davao de Oro today.",
              "Went to QC last week", "Quezon City: fine.", "Around Metro Manila, long lines.",
              "Waited in Ilocos Sur", "CDO was fine")
    assert list(p["place"][:2]) == ["Cagayan de Oro City", "Davao de Oro"]
    assert p["kind"][1] == "province" and p["region"][1] == "Davao Region"
    assert p["place"][2] == "Quezon City" and p["place"][3] == "Quezon City"
    assert p["kind"][4] == "region" and p["region"][4] == "National Capital Region"
    assert p["place"][5] == "Ilocos Sur"           # not "Ilocos" region: longest match
    assert p["place"][6] == "Cagayan de Oro City"
    assert (p["status"] == "found").all()
    assert p["lon_t"].between(116, 128).all()


def test_ambiguous_names_resolve_with_province_else_ambiguous():
    amb = parse("A visit in San Fernando.", "Clinic in San Jose", "Santa Cruz was crowded")
    assert (amb["status"] == "ambiguous").all() and amb["lon_t"].isna().all()
    ok = parse("Clinic in San Fernando, Pampanga.", "San Fernando, La Union was slow")
    assert list(ok["status"]) == ["found", "found"]
    assert list(ok["province"]) == ["Pampanga", "La Union"]
    assert ok["lon_t"].iloc[0] != ok["lon_t"].iloc[1]


def test_quezon_province_beats_towns_and_capital_city_beats_town():
    p = parse("Went to Quezon.", "Bacolod was fine.")
    assert p["kind"][0] == "province"
    assert p["place"][1] == "Bacolod City"


def test_stop_prefixes_and_case_rules():
    p = parse("Brgy. Mabini health center",            # barangay name, not a place
              "Sitio San Jose near Davao City",         # San Jose is skipped, Davao City found
              "Barangay Rizal in Cebu City",
              "went to naga yesterday",                 # lower-case: not a place name
              "Nothing to see here.")
    assert p["status"][0] == "no_place"
    assert p["place"][1] == "Davao City" and p["place"][2] == "Cebu City"
    assert p["status"][3] == "no_place" and p["status"][4] == "no_place"


def test_most_specific_place_wins_and_deterministic():
    t = ["Clinic in Bulacan near Baguio City", "Iloilo City, Iloilo", "", None, 5]
    a, b = parse(*t), parse(*t)
    pd.testing.assert_frame_equal(a, b)
    assert a["place"][0] == "Baguio City"            # city beats province
    assert a["place"][1] == "Iloilo City"
    assert list(a["status"][2:]) == ["no_place"] * 3
    assert list(a.columns) == ["place", "kind", "province", "region", "lon_t", "lat_t", "status"]


def test_series_index_is_preserved():
    s = pd.Series(["in Baguio City", "none"], index=[10, 20])
    assert list(places.geoparse(s).index) == [10, 20]


def _check(texts, lon, lat, km=50):
    parsed = places.geoparse(texts)
    return parsed, places.text_vs_gps(parsed, lon, lat, km)


def test_text_vs_gps_classes():
    texts = ["in Baguio City", "in Baguio City", "in Baguio City", "in Baguio City",
             "nothing named", "in San Jose", "nothing named"]
    lon = [120.60, 125.0, 51.9, 999, 121.0, 121.0, 0.0]
    lat = [16.41, 7.0, 51.5, 10, 14.5, 14.5, 0.0]
    parsed, chk = _check(texts, lon, lat)
    assert list(chk["status"]) == ["agree", "disagree", "gps_invalid", "gps_invalid",
                                   "no_place", "ambiguous", "gps_invalid"]
    assert chk["dist_km"][0] < 5 and chk["dist_km"][1] > 1000
    assert np.isnan(chk["dist_km"][4]) and np.isnan(chk["dist_km"][3])
    assert list(chk["gps_ok"]) == [True, True, False, False, True, True, False]
    # the threshold decides agree vs disagree
    near = places.text_vs_gps(parsed.iloc[:1], [120.9], [16.41], km=10)
    assert near["status"][0] == "disagree"
    assert places.text_vs_gps(parsed.iloc[:1], [120.9], [16.41], km=100)["status"][0] == "agree"


def test_locate_modes():
    texts = ["in Baguio City", "in Baguio City", "in Baguio City", "nothing named", "nothing named"]
    lon = [120.60, 125.0, 51.9, 121.0, 0.0]
    lat = [16.41, 7.0, 51.5, 14.5, 0.0]
    parsed, chk = _check(texts, lon, lat)
    rep = places.locate(parsed, chk, lon, lat, "repaired")
    assert list(rep["source"]) == ["gps", "place", "place", "gps", ""]
    assert rep["lon"][1] == parsed["lon_t"][1] and rep["lon"][0] == 120.60
    assert np.isnan(rep["lon"][4])
    gps = places.locate(parsed, chk, lon, lat, "gps")
    assert list(gps["source"]) == ["gps", "gps", "", "gps", ""]
    agree = places.locate(parsed, chk, lon, lat, "agree")
    assert list(agree["source"]) == ["gps", "", "", "", ""]


def test_assign_place_region_and_cluster():
    texts = ["in Baguio City"] * 3 + ["nothing named"] * 2 + ["in Davao City"] * 3
    rng = np.random.default_rng(1)
    lon = list(120.6 + rng.normal(0, 0.01, 3)) + [121.0, 125.5] + list(125.4 + rng.normal(0, 0.01, 3))
    lat = list(16.4 + rng.normal(0, 0.01, 3)) + [14.1, 7.2] + list(7.2 + rng.normal(0, 0.01, 3))
    parsed, chk = _check(texts, lon, lat)
    loc = places.locate(parsed, chk, lon, lat)
    reg = places.assign_place(loc, parsed, "region")
    assert list(reg[:3]) == ["Cordillera"] * 3 and list(reg[5:]) == ["Davao Region"] * 3
    assert reg[3] == "Calabarzon"                    # nearest region centroid to 121.0E, 14.1N
    assert reg[4] == "Davao Region"
    clu = places.assign_place(loc, parsed, "cluster", eps_m=5000, min_samples=3)
    assert clu[0] == clu[1] == clu[2] != "" and clu[5] == clu[6] == clu[7] != ""
    assert clu[0] != clu[5] and clu[3] == ""
    pts = places.place_points(loc, reg, "region")
    assert pts["n"].sum() == 8 and set(pts["place"]) >= {"Cordillera", "Davao Region"}


def test_bundled_gate_resolution_rate():
    """>=95% of comments that visibly name a place resolve to one."""
    df = pd.read_parquet(ROOT / "data" / "PH_Health_Services_Sentiments.parquet")
    p = places.geoparse(df["text"])
    named = df["text"].str.contains(r"\(in [A-Z]|\bin [A-Z][\w .'-]+[.,)]|^[A-Z][\w .'-]+:", regex=True)
    resolved = (p["status"] == "found")[named].mean()
    assert resolved >= 0.95, resolved
    chk = places.text_vs_gps(p, df["lon"], df["lat"])
    assert set(chk["status"]) <= {"agree", "disagree", "gps_invalid", "no_place", "ambiguous"}
    assert chk["status"].iloc[0] == "gps_invalid"        # row 0: Cagayan de Oro at 51.9N
