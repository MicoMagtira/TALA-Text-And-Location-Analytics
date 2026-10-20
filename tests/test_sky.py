import re
import xml.etree.ElementTree as ET

import pandas as pd
import pytest

from core import sky

PARQUET = "data/PH_Health_Services_Sentiments.parquet"


@pytest.fixture(scope="module")
def bundled():
    return pd.read_parquet(PARQUET)


def _circles(svg):
    return len(re.findall(r"<circle", svg))


def test_deterministic_and_valid(bundled):
    a = sky.build_sky_svg(bundled)
    assert a == sky.build_sky_svg(bundled)
    root = ET.fromstring(a)
    assert root.tag.endswith("svg")


def test_fallback_without_coords():
    svg = sky.build_sky_svg(pd.DataFrame({"text": ["a", "b"]}))
    ET.fromstring(svg)
    assert 'data-points="0"' in svg and _circles(svg) > 0


def test_fallback_all_out_of_box():
    df = pd.DataFrame({"lon": [-0.1, 77.0], "lat": [51.5, 28.6]})
    assert 'data-points="0"' in sky.build_sky_svg(df)


def test_point_cap_and_box():
    df = pd.DataFrame({"lon": [121.0] * 5000 + [0.0], "lat": [14.0] * 5000 + [51.0]})
    svg = sky.build_sky_svg(df, max_points=300)
    assert 'data-points="300"' in svg


def test_size_budget(bundled):
    svg = sky.build_sky_svg(bundled)
    assert len(svg.encode()) < 120_000
    assert 'data-points="0"' not in svg
