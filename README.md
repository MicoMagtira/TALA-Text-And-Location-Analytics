# TALA — Text And Location Analytics

An interactive **NLP + Geospatial** analytics explorer for data-science training.
Built for DOST-NICER training sessions and styled in **National University Manila**
colors.

> **TALA** = **T**ext **A**nd **L**ocation **A**nalytics · *tala* is Filipino for
> *star* and for a *record / note*.
>
> Developed by **Mico C. Magtira** — Senior Data and NLP-Geospatial Scientist,
> DOST-NICER.

## What it does

Two connected tracks over one dataset (`id, text, lon, lat`):

**Text Analytics** — cleaning with Filipino/Taglish stopwords, word clouds &
frequencies, VADER sentiment + NRC emotions, n-grams & co-occurrence networks, LDA
topic modeling + stability, RAKE keywords, NLTK noun/POS extraction, readability
metrics, and TF-IDF K-Means themes.

**Geospatial Analytics** — CRS/bounds validation, DBSCAN clustering (with a
k-distance elbow), grid/centroid generalization, Philippine land clipping,
interactive + publication maps, and **privacy-safe NLP per cluster**. The geo pages
chain their outputs through session state, mirroring the original Colab labs:

```
Parquet → Ingest (points) → DBSCAN (clusters) → Generalization / NLP-per-cluster → Map & Exports
```

Every page has a **Learn** panel (toggle in the sidebar) that shows the concept and
the equivalent source code — turning the app into live teaching material.

## Run locally

```bash
cd tala_app
python -m venv .venv
# Windows:  .venv\Scripts\activate     macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Hot reload is off by default (see `fileWatcherType` below). For development:

```bash
streamlit run app.py --server.fileWatcherType auto
```

First run downloads a small NLTK dataset (tagger + corpora for RAKE and POS),
cached afterward. Everything else — including the Philippine land polygon — ships
with the repo, so the app works offline.

## Deploy to Streamlit Community Cloud

1. Push this `tala_app/` folder to a GitHub repo.
2. On [share.streamlit.io](https://share.streamlit.io), create an app pointing at
   `app.py` on your branch.
3. `requirements.txt` is picked up automatically. There is **no `packages.txt`** —
   the shapely / pyproj / pyogrio wheels bundle GEOS, PROJ and GDAL themselves, so
   installing `libgeos-dev` & friends via apt only duplicated them and added
   several minutes to every rebuild.

### Fitting in a free 1 GB container

The free tier gives ~1 GB RAM and a shared CPU, which this app is tuned for:

| Technique | Where |
|---|---|
| Only `streamlit` + `pandas` on the base import path; sklearn, matplotlib, geopandas, folium and NLTK load inside the functions that use them | `core/*.py` |
| Multi-page navigation, so a page's code runs only when opened | `app.py` |
| Parquet instead of CSV (0.5 MB vs 2.5 MB, no text parsing) | `core/data_loader.py` |
| Coordinates downcast to `float32` | `core/data_loader.py` |
| Natural Earth land polygon precomputed at build time to an 11 KB GeoJSON instead of downloaded per container | `core/geo.py` |
| sklearn's 318-word English stopword list vendored as data, so the text pipeline does not import sklearn | `data/english_stop_words.txt` |
| `TruncatedSVD` on the sparse TF-IDF matrix instead of `PCA` on a densified copy (which allocated ~115 MB) | `core/nlp.py` |
| LDA cached on the parameters that change the *fit*, so the display-only "words per topic" slider no longer refits | `core/nlp.py` |
| NLTK POS tagging instead of spaCy (~150 MB of model + runtime saved) | `core/nlp.py` |
| Every slow cached function names its work, so waits are legible | `show_spinner=` args |
| 8-bit boot splash with server-driven progress | `core/splash.py` |

## Project layout

```
tala_app/
├── app.py                     # entry point + navigation + boot sequence
├── .streamlit/config.toml     # NU theme + runtime tuning
├── requirements.txt
├── assets/styles.css          # brand + responsive CSS + loading states
├── data/                      # Parquet dataset, PH land polygon, stopword lists
├── core/                      # data_loader, preprocess, nlp, geo, viz, ui, splash
└── views/                     # one script per page (text_*, geo_*, home)
```

## Colors

- Navy / Chambray `#35408E` (primary) · Gold / Maize `#F5D89E` (accent) ·
  Mine Shaft `#333333` (text).
- Chart **series** colors use a colorblind-safe categorical palette validated with
  the data-viz color checks (worst adjacent CVD ΔE ≈ 9.1); the brand hexes drive the
  app chrome. Swap palettes live from the sidebar.

## Notes

- VADER and the NRC lexicon are **English-tuned**; on Taglish text they give a useful
  but imperfect signal — a deliberate teaching point.
- The bundled coordinates are intentionally "dirty" (some fall outside the
  Philippines) so CRS/bounds validation and land-clipping can be taught, not hidden.
