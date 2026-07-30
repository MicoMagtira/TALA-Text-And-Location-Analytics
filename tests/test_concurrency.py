"""Guards for the multi-user memory model.

TALA is deployed for a whole workshop cohort on one ~1 GB container. The design
that makes that fit rests on two invariants, and both are easy to break with an
innocent-looking edit:

1. **Shared datasets are shared.** ``cache_resource`` hands every session the same
   object. If someone switches a loader back to ``cache_data``, each session
   silently gets a private ~6.4 MB copy again and the container OOMs at ~30 users
   with no error message to explain why.
2. **Nothing mutates a shared object.** Sharing is only safe because every
   transform copies first. A single in-place assignment would let one trainee's
   action corrupt what everyone else sees.

Run with either::

    python -m pytest tests/ -q     # if pytest is installed
    python tests/test_concurrency.py   # plain stdlib fallback

pytest is intentionally not a runtime dependency — the container that runs this
app has a hard memory budget, so the test file works without it.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402

from core import data_loader as dl  # noqa: E402
from core import geo  # noqa: E402

LON, LAT, TEXT = "lon", "lat", "text"
KEY = (dl.BUNDLED_KEY, LON, LAT, TEXT)


# ---------------------------------------------------------------------------
# 1. Sharing
# ---------------------------------------------------------------------------
def test_bundled_dataset_is_one_shared_object():
    """Every session must resolve to the *same* frame, not a copy of it."""
    frames = [dl.dataset(dl.BUNDLED_KEY) for _ in range(25)]
    first = frames[0]
    assert all(f is first for f in frames), (
        "load path is copying per caller — check that the loader uses "
        "st.cache_resource and not st.cache_data"
    )


def test_derived_geo_layers_are_shared():
    """Identical parameters must not rebuild or duplicate a 14 MB layer."""
    a, _ = geo.points_for(*KEY)
    b, _ = geo.points_for(*KEY)
    assert a is b

    c, _ = geo.clusters_for(*KEY, 15000.0, 10)
    d, _ = geo.clusters_for(*KEY, 15000.0, 10)
    assert c is d


def test_different_parameters_give_different_layers():
    """Sharing must not go so far as to hand back the wrong result."""
    a, info_a = geo.clusters_for(*KEY, 15000.0, 10)
    b, info_b = geo.clusters_for(*KEY, 40000.0, 10)
    assert a is not b
    assert info_a["eps_m"] != info_b["eps_m"]


# ---------------------------------------------------------------------------
# 2. Purity — the transforms must never write to what they were given
# ---------------------------------------------------------------------------
def _fingerprint(df: pd.DataFrame):
    return (df.shape, tuple(df.columns), pd.util.hash_pandas_object(df).sum())


def test_build_points_does_not_mutate_the_shared_frame():
    df = dl.dataset(dl.BUNDLED_KEY)
    before = _fingerprint(df)
    geo.build_points(df, LON, LAT, TEXT)
    assert _fingerprint(df) == before, "build_points mutated the shared dataset"


def test_run_dbscan_does_not_mutate_its_input():
    pts, _ = geo.points_for(*KEY)
    before = (pts.shape, tuple(pts.columns))
    geo.run_dbscan(pts, eps_m=15000, min_samples=10)
    assert (pts.shape, tuple(pts.columns)) == before, (
        "run_dbscan added a column to the shared points layer"
    )
    assert "cluster_id" not in pts.columns


def test_clip_to_ph_does_not_mutate_its_input():
    pts, _ = geo.points_for(*KEY)
    before = pts.shape
    geo.clip_to_ph(pts)
    assert pts.shape == before, "clip_to_ph dropped rows from the shared layer"


def test_downstream_stages_leave_the_base_dataset_untouched():
    """Walk the whole pipeline, then confirm the shared dataset is pristine."""
    df = dl.dataset(dl.BUNDLED_KEY)
    before = _fingerprint(df)
    geo.points_for(*KEY)
    geo.clusters_for(*KEY, 15000.0, 10)
    geo.grid_for(*KEY, 20000.0)
    geo.centroids_for(*KEY, 15000.0, 10, True)
    geo.clipped_for(*KEY, 15000.0, 10)
    assert _fingerprint(df) == before, "the geo walkthrough mutated shared data"


def test_grid_cell_size_is_preserved_for_sparse_extents():
    """A requested grid size must not be silently replaced to cap empty cells."""
    fine = geo.grid_for(*KEY, 5_000.0)
    coarse = geo.grid_for(*KEY, 100_000.0)
    assert len(fine) > len(coarse), "grid cell size does not change occupied cells"
    assert fine["n_points"].sum() == coarse["n_points"].sum(), (
        "grid aggregation lost points while changing cell size"
    )


# ---------------------------------------------------------------------------
# 3. Session state stays small
# ---------------------------------------------------------------------------
def test_no_dataframes_in_the_session_state_contract():
    """The keys a session stores must all be scalars/tuples, never frames.

    This asserts on the declared contract rather than a live session, so it fails
    loudly if someone reintroduces a ``SS_DF``-style key."""
    heavy = [name for name in dir(dl)
             if name.startswith("SS_") and "DF" in name.upper()]
    assert not heavy, f"session-state keys that look like frame storage: {heavy}"

    expected = {"SS_SOURCE_KEY", "SS_TEXT_COL", "SS_LON_COL", "SS_LAT_COL",
                "SS_SOURCE", "SS_POINTS_READY", "SS_CLUSTER_PARAMS",
                "SS_GEN_PARAMS"}
    actual = {n for n in dir(dl) if n.startswith("SS_")}
    assert actual == expected, f"session-state key set changed: {actual ^ expected}"


def _run_standalone() -> int:
    """Minimal runner so the guards work without pytest installed."""
    tests = [(n, v) for n, v in sorted(globals().items())
             if n.startswith("test_") and callable(v)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"  PASS  {name}")
        except Exception as exc:  # noqa: BLE001 - report and continue
            failed += 1
            print(f"  FAIL  {name}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} concurrency guards pass")
    return 1 if failed else 0


if __name__ == "__main__":
    import sys

    raise SystemExit(_run_standalone())
