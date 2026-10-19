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

TALA is aimed at **computer students with a technical background**. It walks them
through two guided tracks over one dataset (`id, text, lon, lat`). A progress strip,
**Back / Next** buttons and a "track complete" card keep the path obvious, Home offers
**Continue** and **Your path**, and nothing ends in a "run the previous page first" dead end.

**Text track (8 steps)**: cleaning with Filipino/Taglish stopwords, word clouds and
frequencies, VADER sentiment + NRC emotions, n-grams and co-occurrence networks, LDA
topic modeling + stability, RAKE keywords, NLTK noun/POS extraction, readability
metrics, and TF-IDF K-Means themes.

**Geo track (5 steps)**: CRS/bounds validation, DBSCAN clustering (with a k-distance
elbow), grid/centroid generalization, Philippine land clipping, and privacy-safe NLP per
cluster. Maps are interactive **pydeck** maps (click a point to see its cluster). The geo pages
run their upstream steps automatically with sensible defaults, so any page can be opened first:

```
Parquet -> Ingest (points) -> DBSCAN (clusters) -> Generalization / NLP-per-cluster -> Map
```

**Save and resume.** Language, sound settings, palettes, dataset choice, cluster
parameters, finished steps and the last page are kept in one browser cookie (`tala_prefs`,
180 days), so a returning visitor skips the language gate and continues where they left
off. Settings has a **Forget me on this computer** button for shared workshop PCs.

Every page has a collapsed **Learn** panel (toggle in the sidebar) that shows the concept
and the equivalent source code, which makes the app live teaching material.

## Sound

TALA synthesizes all of its sound in the browser with the Web Audio API
(`core/sound_engine.js`). There are **no audio files**: nothing to download, no
licensing, and about 7 MB less per visitor than the old MP3s. Music follows the area
you are in (language gate and Home, Text track, Geo track), SFX react to clicks, toggles,
sliders, downloads and compute, and two fanfares mark a finished track and the full sky.
Music and SFX have independent toggles and volume sliders, plus a melody/ambience style
choice in Settings.

The intro is language first: the first tap on a language card unlocks audio (browsers
require a gesture), then a loading splash plays with sound, then **START**.

Every sound was prototyped and approved in the soundboard,
[`docs/sound/soundboard.html`](docs/sound/soundboard.html); open it in a browser to audition
them. See [`docs/AUDIO.md`](docs/AUDIO.md) for the engine, the event map and how to add a sound.

## Languages

TALA ships in **English, Filipino, Cebuano, Ilocano and Hiligaynon**. A new session
opens on a language gate (pixel-art cards and a Continue button), then the 8-bit boot
splash with a START button. The sidebar can switch language mid-session.

There is **one** set of views. Prose is data, not code:

| Store | Holds | Edited by |
|---|---|---|
| `locales/ui.<lang>.json` | short strings: labels, buttons, spinners, errors | `ui.<lang>.draft.json` + `stamp` |
| `locales/pages/<lang>/<page>.md` | the long-form Learn essays, one block per paragraph | directly |

Three rules make five languages maintainable while the app is still changing:

1. **English is canonical.** Every key exists in English first.
2. **Missing translations fall back to English, per unit.** So an English
   improvement ships today and is translated next week — nothing breaks, nothing
   blocks. Keys that should *stay* English (the brand name, `Topic Modeling`,
   `Clustering (DBSCAN)`, `Flesch Reading Ease`) are simply left untranslated.
3. **Every translated unit stores a hash of the English it came from.** When the
   English moves, `i18n_tool.py check` names exactly which units drifted, in
   which languages. Nobody has to remember what went stale.

```bash
python tools/i18n_tool.py check    # what drifted since it was translated?
python tools/i18n_tool.py stamp    # publish drafts, recording English hashes
python tools/i18n_tool.py export   # reviewer workbook (.xlsx) for native speakers
python tools/i18n_tool.py import   # read reviewer edits back into the drafts
```

**Register.** Everyday spoken language, not formal or literary vocabulary.
Technical terms stay in English inline (`DBSCAN`, `cluster`, `sentiment`,
`stopwords`) — that is how the audience actually speaks, and it keeps trainees
able to follow the English documentation the course prepares them for.

**Cost.** Catalogs are tens of KB behind `cache_resource`, so a cohort shares one
copy per language. The active language never enters an analysis cache key, so a
Cebuano trainee and a Tagalog trainee still share the same 14 MB clustered layer —
localization is a render-layer concern only, and `tests/test_i18n.py` enforces it.

**Not localized, deliberately:** the dataset, exported CSV/GeoJSON field names and
filenames (geo_4 calls these a stable output contract — a shared worksheet breaks
if columns differ by language), and the code snippets in the Learn panels.

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

1. Push this repository to GitHub.
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
| Only `streamlit` + `pandas` on the base import path; sklearn, matplotlib, geopandas, pydeck and NLTK load inside the functions that use them | `core/*.py` |
| Multi-page navigation, so a page's code runs only when opened | `app.py` |
| Parquet instead of CSV (0.5 MB vs 2.5 MB, no text parsing) | `core/data_loader.py` |
| Coordinates downcast to `float32` | `core/data_loader.py` |
| Natural Earth land polygon precomputed at build time to an 11 KB GeoJSON instead of downloaded per container | `core/geo.py` |
| sklearn's 318-word English stopword list vendored as data, so the text pipeline does not import sklearn | `data/english_stop_words.txt` |
| `TruncatedSVD` on the sparse TF-IDF matrix instead of `PCA` on a densified copy (which allocated ~115 MB) | `core/nlp.py` |
| LDA cached on the parameters that change the *fit*, so the display-only "words per topic" slider no longer refits | `core/nlp.py` |
| NLTK POS tagging instead of spaCy (~150 MB of model + runtime saved) | `core/nlp.py` |
| Every slow cached function names its work, so waits are legible | `show_spinner=` args |
| pydeck maps instead of folium: the browser renders the points (WebGL) and the server sends a plain DataFrame, with no HTML map document per rerun | `core/maps.py` |
| Synth sound instead of MP3s: no audio files to ship, and the 7 MB per visitor is gone | `core/sound_engine.js` |
| 8-bit boot splash with server-driven progress | `core/splash.py` |

## Project layout

```
.
├── app.py                     # entry point + navigation + boot sequence
├── .streamlit/config.toml     # NU theme + runtime tuning
├── requirements.txt
├── assets/styles.css          # brand + responsive CSS + loading states
├── data/                      # Parquet dataset, PH land polygon, stopword lists
├── docs/                      # AUDIO.md, PLAN_SEAMLESS.md, sound/soundboard.html
├── locales/                   # ui.<lang>.json + pages/<lang>/*.md (5 languages)
├── tools/                     # i18n_tool, extract, seed, smoke_e2e.cjs (browser smoke test)
├── core/
│   ├── data_loader, preprocess, nlp, geo, viz   # data + analysis
│   ├── maps.py                # pydeck layers and decks
│   ├── tracks.py              # track order, progress, step/track completion
│   ├── persist.py             # save + resume cookie
│   ├── sound_engine.js        # Web Audio synth (sounds + songs)
│   └── ui, i18n, gate, splash, audio
├── tests/                     # concurrency, i18n, audio, maps, tracks, persist guards
└── views/                     # one script per page (text_*, geo_*, home)
```

### End-to-end smoke test

With the app running (`streamlit run app.py --server.headless true --server.port 8599`):

```bash
node tools/smoke_e2e.cjs            # needs Playwright; set PLAYWRIGHT_PATH to override
```

It walks the intro, visits all 13 pages, then checks resume from a saved cookie and reload.

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
