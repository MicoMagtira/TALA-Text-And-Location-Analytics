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
topic modeling + stability, RAKE keywords, spaCy noun/POS extraction, readability
metrics, and TF-IDF K-Means themes.

**Geospatial Analytics** — CRS/bounds validation, DBSCAN clustering (with a
k-distance elbow), grid/centroid generalization, Philippine land clipping,
interactive + publication maps, and **privacy-safe NLP per cluster**. The geo pages
chain their outputs through session state, mirroring the original Colab labs:

```
CSV → Ingest (points) → DBSCAN (clusters) → Generalization / NLP-per-cluster → Map & Exports
```

Every page has a **Learn** panel (toggle in the sidebar) that shows the concept and
the equivalent source code — turning the app into live teaching material.

## Run locally

```bash
cd tala_app
python -m venv .venv
# Windows:  .venv\Scripts\activate     macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm    # if the pinned wheel didn't install it
streamlit run app.py
```

First run downloads a small NLTK dataset (for RAKE) and the Natural Earth land
polygon (for clipping) — both cached afterward.

## Deploy to Streamlit Community Cloud

1. Push this `tala_app/` folder to a GitHub repo.
2. On [share.streamlit.io](https://share.streamlit.io), create an app pointing at
   `app.py` on your branch.
3. `requirements.txt` and `packages.txt` are picked up automatically (the latter
   installs the GDAL/GEOS/PROJ system libraries geopandas needs).

## Project layout

```
tala_app/
├── app.py                     # entry point + navigation
├── .streamlit/config.toml     # NU theme
├── requirements.txt / packages.txt
├── assets/styles.css          # brand + responsive CSS
├── data/                      # bundled example dataset + Tagalog stopwords
├── core/                      # data_loader, preprocess, nlp, geo, viz, ui
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
