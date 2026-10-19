"""pydeck map builders: serialisable, geometry-free frames, no folium left."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import geopandas as gpd  # noqa: E402
import numpy as np  # noqa: E402

from core import maps, viz  # noqa: E402

PALETTE = viz.categorical(n=3)


def _gdf(n=200):
    rng = np.random.default_rng(0)
    lon = 121 + rng.random(n)
    lat = 14 + rng.random(n)
    g = gpd.GeoDataFrame(
        {"cluster_id": rng.integers(-1, 3, n), "n_points": rng.integers(1, 50, n),
         "text": [f"comment {i}" for i in range(n)]},
        geometry=gpd.points_from_xy(lon, lat), crs="EPSG:4326")
    return g


def _view(g):
    return maps.view_for(maps.to_frame(g))


def test_builders_return_layers_and_deck_serializes():
    from core import geo

    g = _gdf()
    frame = maps.to_frame(g, tip="text")
    cells = geo.grid_aggregate(g, 20000)
    layers = [
        maps.points_layer(frame),
        maps.cluster_layer(g, PALETTE),
        maps.grid_layer(cells, viz.sequential_hexes(n=6)),
        maps.centroid_layer(g, color_by={"positive": "#008300"}),
        maps.land_layer(),
    ]
    for layer in layers:
        assert layer.type in ("ScatterplotLayer", "GeoJsonLayer")
        assert maps.deck([layer], _view(g), "{tip}").to_json()


def test_to_frame_plain_capped_and_non_mutating():
    g = _gdf(300)
    before = g.copy()
    out = maps.to_frame(g, extra_cols=("cluster_id",), tip="text", cap=100)
    assert "geometry" not in out.columns
    assert len(out) == 100 and out.attrs["sampled"] and out.attrs["total"] == 300
    assert out["tip"].str.len().max() <= 90
    assert list(out.columns) == ["lon", "lat", "cluster_id", "tip"]
    assert g.equals(before) and list(g.columns) == list(before.columns)


def test_noise_is_grey_and_smaller():
    g = _gdf()
    df = maps.cluster_frame(g, PALETTE)
    noise = df[df["cluster_id"] == -1]
    assert len(noise) and all(c == list(maps.NOISE_RGBA) for c in noise["color"])
    assert (noise["radius"] < df[df["cluster_id"] != -1]["radius"].min()).all()
    assert set(noise["tip"]) == {"Noise"}


def test_view_falls_back_to_philippines():
    v = maps.view_for(maps.to_frame(None))
    assert (v.latitude, v.longitude) == (12.8, 121.8)


def test_hex_to_rgba():
    assert viz.hex_to_rgba("#35408E", 100) == [53, 64, 142, 100]


def test_no_folium_or_branca_imports():
    files = list((ROOT / "core").rglob("*.py")) + list((ROOT / "views").rglob("*.py"))
    files.append(ROOT / "app.py")
    pat = re.compile(r"^\s*(import|from)\s+(folium|branca|streamlit_folium)\b", re.M)
    assert [f.name for f in files if pat.search(f.read_text(encoding="utf-8"))] == []
