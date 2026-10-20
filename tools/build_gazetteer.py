"""Build ``data/ph_gazetteer.csv`` from the GeoNames Philippines dump.

Run:  .venv/Scripts/python tools/build_gazetteer.py

Why a build step: TALA's place-first journey needs a Philippine place list
(regions, provinces, cities, municipalities) with real coordinates. Shipping the
~2.5 MB GeoNames zip would be wasteful, so this script downloads it once, keeps
only what the geoparser uses, and writes a compact CSV (well under 1 MB) that is
committed. Nothing here invents a coordinate: every lon/lat comes straight from
a GeoNames feature (ADM1 for regions, ADM2 for provinces, ADM3/PPLA for cities
and municipalities). If the download fails the script stops.

How GeoNames encodes the Philippines (checked against the dump, not assumed):
  * ADM1  = the 17 regions; admin1 code is "01".."15", "40", "41", "NCR".
  * ADM2  = provinces (``PH.<admin1>.<admin2>`` in admin2Codes.txt). The list also
            holds 4 NCR "districts" (dropped) and Cotabato City (a city, kept as one).
            82 real provinces remain, including the two Maguindanao halves.
  * ADM3  = cities and municipalities (names like "City of Lamitan", "Baguio City").
  * PPLA/PPLA2/PPLC = capitals; used only to add cities that have no ADM3 row
            (e.g. Cagayan de Oro, Manila). A municipality that merely is a provincial
            capital (San Jose, Antique) stays a municipality.

Data (c) GeoNames, https://www.geonames.org, licensed CC BY 4.0.
"""
from __future__ import annotations

import csv
import re
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

BASE = "https://download.geonames.org/export/dump/"
OUT = Path(__file__).resolve().parent.parent / "data" / "ph_gazetteer.csv"
MAX_BYTES = 1_000_000

# GeoNames names a few regions oddly; these are the names people actually write.
REGION_NAME = {"Davao": "Davao Region", "Bicol": "Bicol Region", "Ilocos": "Ilocos Region",
               "Cordillera Administrative Region": "Cordillera Administrative Region"}
REGION_ALIASES = {
    "01": "Region I", "02": "Region II", "03": "Region III", "05": "Region V",
    "06": "Region VI", "07": "Region VII", "08": "Region VIII", "09": "Region IX",
    "10": "Region X", "11": "Region XI", "12": "Region XII", "13": "Region XIII",
    "14": "BARMM|ARMM", "15": "CAR|Cordillera", "40": "Region IV-A|CALABARZON",
    "41": "Region IV-B|MIMAROPA", "NCR": "NCR|Metro Manila|Manila Metropolitan Area",
}
CITY_ALIASES = {"cagayan de oro": "CDO", "quezon": "QC", "ozamiz": "Ozamis"}  # hand-added short forms (lower-case core name)

# ``pop`` is the GeoNames population. The geoparser uses it only to resolve a bare
# name such as "Bacolod" or "Catarman" to the clearly larger place; saint names
# ("San Fernando", "Santa Cruz") are never resolved this way.
FIELDS = ["name", "aliases", "kind", "province", "region", "lon", "lat", "pop"]


def fetch(tmp: Path) -> dict[str, Path]:
    files = {}
    for fn in ("PH.zip", "admin1CodesASCII.txt", "admin2Codes.txt"):
        dest = tmp / fn
        print("downloading", fn, flush=True)
        urllib.request.urlretrieve(BASE + fn, dest)
        files[fn] = dest
    with zipfile.ZipFile(files["PH.zip"]) as z:
        z.extract("PH.txt", tmp)
    files["PH.txt"] = tmp / "PH.txt"
    return files


_LOWER_MID = {"De", "Del", "Dela", "Ng", "Sa", "Y", "Of", "Da"}


def tidy(name: str) -> str:
    """'Cagayan De Oro' -> 'Cagayan de Oro' (GeoNames title-cases connectors)."""
    parts = name.split(" ")
    return " ".join(p.lower() if i and p in _LOWER_MID else p for i, p in enumerate(parts))


def core_name(raw: str) -> tuple[str, bool]:
    """('City of Lamitan') -> ('Lamitan', True); strips parentheticals."""
    name = re.sub(r"\s*\(.*?\)", "", raw).strip()
    is_city = False
    m = re.match(r"^(?:City of|Municipality of)\s+(.*)$", name)
    if m:
        is_city = name.startswith("City of")
        name = m.group(1)
    m = re.match(r"^(?:Science City of|Island Garden City of)\s+(.*)$", name)
    if m:
        is_city, name = True, m.group(1)
    if name.endswith(" City"):
        is_city, name = True, name[:-5]
    return tidy(name.strip()), is_city


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="geonames_"))
    try:
        files = fetch(tmp)
    except Exception as exc:  # no network etc.: never invent data
        print("DOWNLOAD FAILED:", exc, file=sys.stderr)
        return 1

    admin1 = {}
    for line in files["admin1CodesASCII.txt"].read_text(encoding="utf-8").splitlines():
        code, name, *_ = line.split("\t")
        if code.startswith("PH."):
            admin1[code[3:]] = name
    admin2 = {}
    for line in files["admin2Codes.txt"].read_text(encoding="utf-8").splitlines():
        code, name, *_ = line.split("\t")
        if code.startswith("PH."):
            _, a1, a2 = code.split(".", 2)
            admin2[(a1, a2)] = name

    feats = []
    for line in files["PH.txt"].read_text(encoding="utf-8").splitlines():
        f = line.split("\t")
        feats.append({"name": f[1], "lat": float(f[4]), "lon": float(f[5]), "fcode": f[7],
                      "a1": f[10], "a2": f[11], "pop": int(f[14] or 0)})

    region_of = {c: REGION_NAME.get(n, n) for c, n in admin1.items()}
    rows: list[dict] = []

    # Regions (ADM1) --------------------------------------------------------
    for f in feats:
        if f["fcode"] == "ADM1":
            rname = region_of[f["a1"]]
            rows.append(dict(name=rname, aliases=REGION_ALIASES.get(f["a1"], ""), kind="region",
                             province="", region=rname, lon=f["lon"], lat=f["lat"], pop=0))

    # Provinces (ADM2) --------------------------------------------------------
    prov_name = {}
    for f in feats:
        if f["fcode"] != "ADM2":
            continue
        raw = admin2.get((f["a1"], f["a2"]), f["name"])
        if f["a1"] == "NCR":          # Manila "districts", not provinces
            continue
        if raw == "Cotabato City":    # independent city, handled below
            continue
        name = re.sub(r"^Province of ", "", raw)
        prov_name[(f["a1"], f["a2"])] = name
        rows.append(dict(name=name, aliases="Maguindanao" if name.startswith("Maguindanao") else "",
                         kind="province", province=name,
                         region=region_of[f["a1"]], lon=f["lon"], lat=f["lat"], pop=0))
    prov_name[("NCR", "*")] = "Metro Manila"

    def province_for(f):
        if f["a1"] == "NCR":
            return "Metro Manila"
        return prov_name.get((f["a1"], f["a2"]), "")

    reserved = {r["name"].lower() for r in rows if r["kind"] in ("region", "province")}
    for r in rows:
        reserved.update(a.lower() for a in r["aliases"].split("|") if a)

    # Capitals that may be cities without a "City" ADM3 name -------------------
    capitals = {}
    for f in feats:
        if f["fcode"] in ("PPLA", "PPLA2", "PPLC"):
            capitals[(f["a1"], f["a2"], f["name"].lower())] = f

    # Cities & municipalities (ADM3) ---------------------------------------------
    seen = set()
    muni_rows, city_rows = [], []
    for f in feats:
        if f["fcode"] != "ADM3":
            continue
        core, is_city = core_name(f["name"])
        seen.add((f["a1"], f["a2"], core.lower()))
        (city_rows if is_city else muni_rows).append((f, core))
    for key, f in capitals.items():           # capitals with no ADM3 twin
        core, _ = core_name(f["name"])
        if (f["a1"], f["a2"], core.lower()) not in seen and f["a1"] in region_of:
            seen.add((f["a1"], f["a2"], core.lower()))
            city_rows.append((f, core))
    for f in feats:                           # Cotabato City is an ADM2 point
        if (f["fcode"] == "ADM2" and admin2.get((f["a1"], f["a2"])) == "Cotabato City"
                and not any(c.lower() == "cotabato" for _, c in city_rows)):
            city_rows.append((f, "Cotabato"))

    def add(f, core, kind):
        alias = []
        if kind == "city":
            name = f"{core} City"
            if core.lower() not in reserved:
                alias.append(core)
            if core.lower() in CITY_ALIASES:
                alias.append(CITY_ALIASES[core.lower()])
        else:
            name = core
        rows.append(dict(name=name, aliases="|".join(dict.fromkeys(alias)), kind=kind,
                         province=province_for(f), region=region_of.get(f["a1"], ""),
                         lon=f["lon"], lat=f["lat"],
                         pop=f["pop"]))

    for f, core in sorted(city_rows, key=lambda t: (t[0]["a1"], t[1])):
        add(f, core, "city")
    # Municipalities: biggest first, only while the file stays under 1 MB.
    for f, core in sorted(muni_rows, key=lambda t: -t[0]["pop"]):
        add(f, core, "municipality")

    # Manila: GeoNames models it as NCR districts; the city is the capital point.
    if not any(r["name"] == "Manila City" for r in rows):
        print("warning: Manila not found", file=sys.stderr)

    def render(rs):
        import io

        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rs:
            r = dict(r, lon=f"{r['lon']:.5f}", lat=f"{r['lat']:.5f}")
            w.writerow(r)
        return buf.getvalue()

    text = render(rows)
    while len(text.encode("utf-8")) > MAX_BYTES:       # drop smallest municipalities
        rows.pop()
        text = render(rows)
    OUT.write_text(text, encoding="utf-8", newline="")
    from collections import Counter

    print(OUT, len(text.encode("utf-8")), "bytes", dict(Counter(r["kind"] for r in rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
