# TALA v3 plan: place-first TALA (panel revisions)

Status: **implemented** (2026-10-20; Task J docs and QA screenshots in `docs/screenshots/`). Deviations: the bundled data names a place in all 12,000 comments (not ~10,000), 99.2% resolve (102 ambiguous); the recorder re-encodes to VP9 with Playwright's ffmpeg (the plan said no re-encode); the NLTK-free text stack keeps `TruncatedSVD` in `core/nlp.py`. Originally approved 2026-10-20. Meteor constants pending from the Wave 0 board (Task F falls back to the board defaults). Executor: Sonnet at medium effort, multi-agent, in waves, on branch
`feat/panel-revisions`. The orchestrator (Opus) does Wave 0 and the translations itself. Nobody pushes until the user approves.

## Decisions (user, 2026-10-20)

| Panel comment / request | Decision |
|---|---|
| 1. Wordy landing page | **Simple first, depth optional.** Short visual landing. The essay and About move to a **How TALA works** page. Per-page Learn panels stay, collapsed. |
| 2. Confusing sequence | **Guided, free to jump.** A constellation sidebar shows numbered steps with done/current/to-do states. Pages say when earlier steps were run for you. |
| 3. Video over tutorial text | **Automated, captioned tour**, one per UI language, recorded by a Playwright script. No voice-over. |
| 4. Looks like Dr. Rabajante's explorers | **Strong identity on Streamlit**, plus a **place-first redesign** that removes the method-by-method overlap (§1). |
| Overlap with his text apps | **Place-first:** drop the pages that mirror his tabs; keep word frequency, sentiment and themes only as comparisons between places; add four methods he does not have. |
| Settings overlap | **Appearance section removed.** One fixed TALA palette that is colour-blind safe by default (no pickers, no toggle). Custom stopwords move to the Data step. |
| START animation | **Single meteor wipe**: one meteor streaks across in sync with the existing *bulalakaw* START sound, and its tail wipes the splash away to reveal Home. A preview board is approved first (Wave 0). |

Supersedes `PLAN_SEAMLESS.md`'s audience line and its two-track structure.

---

## 0. Ground rules for every agent

Same as `PLAN_SEAMLESS.md` §0: `.venv`, session state holds keys never DataFrames, lazy heavy imports, language never
in a cache key, exports not localized, docstrings that say *why*, pytest green, `tools/i18n_tool.py check` clean.
Additions:

- **Locale keys go through a pending file.** Parallel agents never edit `locales/ui.en.json` directly. Each task
  writes its new or changed English keys to `locales/_pending/<task>.json` (key → text, with `null` meaning delete), and
  the orchestrator merges them after the wave. This avoids clobbered writes.
- **No new runtime dependencies.** Everything new is numpy/pandas/scikit-learn/geopandas, which are already installed.
  Dev tools reuse ARAW's Playwright install like `tools/smoke_e2e.cjs` does.
- **Keep it calm.** No new always-visible paragraphs. Each page header has one plain-language sentence; the depth goes
  in that page's collapsed Learn panel.
- **No method tabs.** Every page answers a *question about places* in its title (§1). A page that only "runs method X
  on all comments" is out of scope.
- **Stay in your lane.** Edit only owned files. Report needed changes elsewhere instead of making them.

---

## 1. Why place-first: the overlap and the answer

Rabajante's *Text Analytics Explorer* tabs are Word Cloud, Sentiment (NRC), Positive/Negative Word Cloud,
Bigram/Trigram Network, Topic Modeling (LDA), Top Noun Extraction, Keyword Extraction (RAKE) and Linguistic Metrics.
His *Filipino–Taglish Mini-Explorer* adds a combined Filipino–English exclusion list. His sidebar has palette choice
and editable excluded words. TALA's current Text track matches **7 of its 8 pages** to those tabs, almost in order,
and its Settings panel has the same two controls.

The answer is to change the *unit of analysis* from "all comments" to **places**. The bundled data makes this natural:
about 10,000 of 12,000 comments name a place (all 82 provinces and their capitals appear), while many coordinates
are wrong on purpose (row 0 says *Cagayan de Oro* but sits at 51.9°N, −0.46°E). TALA becomes the tool that **reads
where a comment is from, checks it against the GPS, and then compares what each place is saying**. None of his
apps touch location, so no TALA page maps to any of his tabs.

**Dropped** (they mirrored his tabs): plain word cloud and frequencies, NRC emotions, positive/negative word clouds,
n-gram and co-occurrence networks, LDA topics and topic stability, RAKE keywords, noun/POS extraction, readability
and linguistic metrics, and the sidebar palette pickers.
**Dependencies removed:** `wordcloud`, `nrclex`, `rake-nltk`, `textstat`, and NLTK POS-tagger data. This makes the
container lighter on Community Cloud.

---

## 2. The new journey: two chapters, nine steps

```
Chapter 1  LUGAR · WHERE ARE PEOPLE?            (in order)
  1 Data                    load, map columns, cleaning preview, custom stopwords
  2 Text vs GPS             geoparse places in text, validate GPS, agree/disagree/repair
  3 Places                  group by Region (gazetteer) or Cluster (DBSCAN + k-distance)
Chapter 2  SALITA · WHAT IS EACH PLACE SAYING?  (any order; Chapter 1 auto-runs with defaults)
  4 What sets a place apart contrastive keywords: weighted log-odds, place vs rest or A vs B
  5 How each place feels    VADER sentiment per place, % negative with intervals, bubble map
  6 What they praise or fault aspect sentiment: waiting, staff, cost, medicine, facilities, access
  7 What they talk about    TF-IDF + K-Means themes, theme share per place
  8 Where complaints cluster Getis-Ord Gi* hotspots of negative sentiment on a grid
  9 Place report            privacy-safe generalized map, report cards per place, exports
```

| # | Page id | Built from | New methods |
|---|---|---|---|
| 1 | `p1_data` | `text_1_data` (+ custom stopwords moved in from Settings) | none |
| 2 | `p2_textgps` | `geo_1_ingest` validation + `geo_4_map` land clip | **Geoparsing + Text vs GPS check** |
| 3 | `p3_places` | `geo_2_cluster` | region grouping from the gazetteer |
| 4 | `p4_apart` | new | **Contrastive keywords** (Monroe, Colaresi & Quinn 2008) |
| 5 | `p5_feel` | VADER part of `text_3_sentiment` + `geo_5_nlp` | per-place intervals, min-n filter |
| 6 | `p6_aspects` | new | **Aspect sentiment** |
| 7 | `p7_themes` | `text_8_themes` | theme share per place, silhouette for k |
| 8 | `p8_hotspots` | new | **Getis-Ord Gi\* hotspots** |
| 9 | `p9_report` | `geo_3_generalize` + `geo_4_map` exports + `geo_5_nlp` profiles | report cards |

**Place unit.** On step 3 the user chooses the unit, which is used by steps 4–9: **Region** (the default, readable for
non-technical users, from the gazetteer) or **Cluster** (DBSCAN, the ML route). There are no new polygons: regions are
drawn as bubbles at their gazetteer centroid.

**Location source.** On step 2 the user chooses which coordinates downstream steps use: **Repaired** (the default:
GPS when it agrees or no place is named, otherwise the named place's coordinates), **GPS only** (validated +
land-clipped), or **Agreeing only**.

---

## 3. Target layouts

### Landing (`views/home.py`)

```
┌──────────────────────────────────────────────────────────────┐
│  ✦ TALA                          [EN][FIL][CEB][ILO][HIL]    │  night-sky hero; stars =
│  Every comment is a star.                                    │  dataset coords (PH shape)
│  See what people say, and where they say it.   · · ·:·.·     │
├──────────────────────────────────────────────────────────────┤
│  ▶ Continue: How each place feels (step 5/9)  [Continue →]   │  only if saved progress
├─────────────────────────────┬────────────────────────────────┤
│  LUGAR                      │  SALITA                        │
│  Where are people?          │  What is each place saying?    │
│  ★★☆  2/3 · in order        │  ☆☆☆☆☆☆  0/6 · any order        │
│  [Continue →]               │  [Start →]                     │
├─────────────────────────────┴────────────────────────────────┤
│  ▶  Watch the 1-minute tour      (video, in the UI language) │
├──────────────────────────────────────────────────────────────┤
│  ▸ Peek at the data (collapsed)    New here? How TALA works →│
└──────────────────────────────────────────────────────────────┘
```

### Sidebar (constellation navigation)

```
✦ Home
✦ How TALA works
LUGAR · WHERE ARE PEOPLE?          in order
  ★ 1 Data                        done
  ✷ 2 Text vs GPS                 ← current (glow)
  ☆ 3 Places
SALITA · WHAT IS EACH PLACE SAYING? any order
  ☆ 4 What sets a place apart
  …
  ☆ 9 Place report
⚙ Settings (collapsed: language, sound, forget me)
Dataset: PH Health Services · 12,000 rows
```

---

## 4. Waves and file ownership

```
Wave 0 (Opus):      meteor preview board → user approves
Wave 1 (parallel):  A analytics core     B sky hero     C journey + navigation skeleton
Wave 2 (parallel):  D Chapter 1 pages    E Chapter 2 pages    F landing, Learn page, identity, chrome, meteor
Wave 3 (parallel):  G cleanup + Learn essays (EN)    I tour recorder
          then      H translations (Opus)
Wave 4:             J record 5 videos, README, smoke test, QA screenshots
```

After each wave the orchestrator merges `locales/_pending/*`, runs pytest, the i18n check and the smoke test, reviews
against this plan, then commits (`feat(places): …`, and so on, with the session's attribution trailer).

---

## 5. Wave 0: START meteor preview (`docs/motion/start_meteor.html`, Opus)

This is a standalone board like the soundboard. It loads the real `core/sound_engine.js` and shows a mock splash over
a mock Home, with controls for duration, angle, glow and sparkle dust, plus Replay. The meteor head and its trailing
"wipe edge" are kept on one line, so the splash is erased behind the meteor and Home shows through. It must respect
`prefers-reduced-motion` (a plain fade). The user picks the values, and they become the production constants.

---

## 6. Task A: analytics core (no UI)

**Owns:** `tools/build_gazetteer.py`, `data/ph_gazetteer.csv`, `core/places.py`, `core/compare.py`,
`data/aspects.json`, `tests/test_places.py`, `tests/test_compare.py`.

1. **Gazetteer.** `tools/build_gazetteer.py` downloads the GeoNames `PH` dump (CC BY 4.0) and writes
   `data/ph_gazetteer.csv` (`name, aliases, kind, province, region, lon, lat`). It covers regions, all 82 provinces,
   every city and Metro Manila; municipalities are added only if the file stays under 1 MB. Hand-added aliases include
   `CDO`, `QC`, `NCR`, `Metro Manila` and `Brgy`/`Purok`/`Sitio` as stop-prefixes. Attribution goes in README and How
   TALA works. **Gate:** at least 95% of the place mentions in the bundled data resolve.
2. **`core/places.py`.**
   - `geoparse(texts) -> DataFrame[place, kind, province, region, lon_t, lat_t, status]`: longest title-case match up
     to 4 tokens against the gazetteer and aliases. Ambiguous names (*San Fernando*, *San Jose*, *Santa Cruz*) resolve
     through a co-mentioned province, otherwise `ambiguous`.
   - `text_vs_gps(parsed, lon, lat, km=50) -> status per row`: `agree`, `disagree`, `gps_invalid` (out of range or
     off PH land), `no_place`, or `ambiguous`, plus a distance in km.
   - `locate(source_key, …, mode="repaired"|"gps"|"agree")`: the coordinates every Chapter 2 page uses. It is cached on
     the dataset key and parameters.
   - `assign_place(…, unit="region"|"cluster")`: a place label per row (DBSCAN reuses `core/geo.run_dbscan`).
3. **`core/compare.py`** (pure numpy/sklearn, unit-tested on tiny synthetic inputs):
   - `log_odds(tokens_a, tokens_b, prior) -> DataFrame[term, delta, z]`: weighted log-odds with an informative
     Dirichlet prior, over unigrams and bigrams.
   - `place_sentiment(compound, place, min_n=30) -> DataFrame[place, n, mean, pct_neg, lo, hi]` with Wilson intervals.
   - `aspect_sentiment(texts, place, lexicon) -> DataFrame[place, aspect, n, pct_neg]`: split sentences, keep those
     containing aspect terms (English + Filipino in `data/aspects.json`), and score them with VADER.
   - `gi_star(values, xy_m, radius_m) -> z`: Getis-Ord Gi\* with a binary distance band (sklearn `BallTree`), plus
     `hotspot_class(z)` → hot/cold at 90/95/99%.
   - `theme_share(labels, place)`, which reuses `nlp.tfidf_kmeans` and adds a silhouette score.

**Accept:** Gi\* matches a hand-computed 5-point example; log-odds is symmetric (A vs B = −(B vs A)); and the
geoparse gate passes.

## 7. Task B: sky hero (`core/sky.py`, `tests/test_sky.py`)

This is unchanged from the previous draft. `sky_svg(df_key)` builds an inline SVG band from about 1,500 sampled PH
coordinates (deterministic, roughly 8% twinkle, reduced-motion safe), with a generic starfield fallback. It is cached
on the dataset key only and stays under about 120 KB. Points are filtered to the PH bounding box, which already drops
the bogus London/India coordinates.

## 8. Task C: journey and navigation skeleton

**Owns:** `app.py` (navigation), `core/tracks.py`, `core/ui.py` (`sidebar_nav`, `auto_ran`, progress strip, footer),
`core/persist.py` (migration only), `core/audio.py` (signature/area map only), `views/p*.py` **stubs**,
`views/learn.py` stub, `tests/test_tracks.py`, `tests/test_persist.py`, the nav section of `assets/styles.css`.

1. `tracks.CHAPTERS = {"where": [p1, p2, p3], "what": [p4 … p9]}` and `tracks.ORDERED = {"where": True, "what": False}`.
   Progress strip, Back/Next, the chapter-complete card and the `fullSky` celebration all follow chapters.
2. `st.navigation(..., position="hidden")` plus `ui.sidebar_nav()`: Home, How TALA works, then two chapter groups with
   numbered `st.page_link`s in keyed containers `tala-nav-{done|current|todo}-{page}`, styled as stars on a connecting
   line.
3. `ui.auto_ran(page)` with `tracks.skipped_upstream(page, done)`: a compact callout, e.g. *"Steps 2–3 haven't been
   opened yet, so TALA ran them with default settings."*, with a link. It is silent and never stops the page.
4. **Persist migration:** unknown page names in a saved cookie are dropped, and an unknown last page falls back to Home.
5. **Sound:** chapter 1 uses the `geo` music area and chapter 2 the `text` area. The nine page signatures reuse
   existing cues (no new sounds).
6. Stub views render the header, a placeholder and the footer, so the app runs end to end after Wave 1.

## 9. Task D: Chapter 1 pages (`views/p1_data.py`, `p2_textgps.py`, `p3_places.py`)

- **p1:** the current data page plus the custom-stopword box and the Filipino-stopword toggle (moved out of Settings).
- **p2:** metrics (named a place / agree / disagree / GPS invalid), a pydeck map coloured by status with *lines from
  the GPS point to the named place* for disagreements (a sample of up to 400), a km-threshold slider, a location-source
  choice, and a sample table of disagreements (ids and place names only, no full text). This is where the
  "a third of this data is wrong" lesson now lands, early and visibly.
- **p3:** a Region/Cluster unit toggle. Cluster mode keeps DBSCAN eps/min-samples and the k-distance elbow. Both
  modes show a place-size bar chart and a bubble map.
- Learn essays (EN) for p1–p3 at a technical level, with code snippets, collapsed.

## 10. Task E: Chapter 2 pages (`views/p4_apart.py` … `p9_report.py`)

- **p4:** place A vs *rest* (or vs place B); a diverging bar chart of the top ±15 terms by z; a min-count slider. No
  word cloud.
- **p5:** a bubble map (size = n, colour = % negative); a ranked dot plot with Wilson intervals; places with n < min_n
  greyed out with the reason shown.
- **p6:** a place × aspect heatmap (% negative) with a click-through aspect picker → map.
- **p7:** a k slider with a silhouette readout, theme cards (top terms, auto-label), and a 100% stacked bar of theme
  share per place.
- **p8:** sliders for cell km, radius km and min comments per cell; a Gi\* hot/cold grid map; a significance legend and a
  multiple-testing note in Learn.
- **p9:** generalization choice (grid or centroids), one report card per place (distinctive words, sentiment, worst
  aspect, main theme, hotspot flag), and exports (GeoJSON, CSV, `metadata.json`), keeping the existing export field
  names where they still apply.
- Learn essays (EN) for p4–p9 with the maths (log-odds prior, Wilson, Gi\* formula) and code.

## 11. Task F: landing, How TALA works, identity, chrome, meteor

**Owns:** `views/home.py`, `views/learn.py`, `core/ui.py` (`header`, `sidebar_controls` Settings section),
`core/viz.py` (palette), `core/splash.py` + `core/sound_engine.js` (`startPressed` meteor only), `assets/styles.css`
(except nav), `.streamlit/config.toml`, `app.py` (`page_icon` only), `locales/pages/*/home.md` → `learn.md`.

1. The landing page exactly as §3: hero with `sky.sky_svg`, the tagline, language chips (a styled
   `st.segmented_control` calling `i18n.set_lang`), the Continue card, two chapter cards, the tour video (the
   `tour_<lang>.webm` for the UI language, else English, else hidden), "Peek at the data", and a How TALA works link.
2. **How TALA works:** the old home essay (updated for the place-first story), About, "what each chapter does", the
   GeoNames attribution, and a short "how TALA differs" note (place-first, text vs GPS, five languages). It stays
   factual and does not mention other tools by name.
3. **Identity copy:** chapter names **Lugar** (Where are people?) and **Salita** (What is each place saying?) shown as
   small gold labels above the question titles on Home, in the sidebar and in the progress strip (not translated: they
   are names). The tagline *"Every comment is a star. See what people say, and where they say it."*, no
   "Explorer" anywhere, and chapter titles as questions.
4. **Fixed palette, no Appearance section:** remove the Appearance group (both palette pickers) from Settings, plus the
   custom-stopword box and Filipino toggle (Task D moves them to p1; the session keys `SS_CUSTOM_SW`/`SS_USE_TL` stay
   in `core/ui.py`). `core/viz.py` keeps one categorical palette (Okabe–Ito-based, tuned to the night/gold identity),
   one sequential (cividis-like) and one diverging (blue–gold), all colour-blind safe. `ui.palette()` and
   `ui.seq_palette()` return those fixed names.
5. **Chrome:** hide the Streamlit decoration bar, Deploy and the footer badge; favicon `assets/favicon.png` (pixel star).
6. **Meteor:** port the Wave 0 board's approved constants into the splash. `startPressed()` sets the viewport-derived
   CSS variables and adds `tala-boot-complete`. The CSS runs the meteor and the mask wipe, then removes the overlay. The
   existing 12 s no-JS fallback fade and the reduced-motion fade stay.

## 12. Task G: cleanup and Learn essays

Delete the old `views/text_*` and `views/geo_*`, the unused `core/nlp.py` and `core/geo.py` functions, the
dropped requirements and their locale keys (in every catalog and draft) and `locales/pages/*/text_*|geo_*.md`. Move
any reused translated strings to their new keys so existing Filipino/Cebuano/Ilocano/Hiligaynon work carries over.
Update `tests/test_maps.py` and `tests/test_concurrency.py` for the new pages.

## 13. Task H: translations (Opus)

Translate every new or drifted key and the new Learn essays into Filipino, Cebuano, Ilocano and Hiligaynon, then
`i18n_tool.py stamp`. Flag all of it in `review_notes.json` as **needs native review**.

## 14. Task I: tour recorder (`tools/record_tour.cjs`)

The same harness as the smoke test. One fresh context per language, `recordVideo` 1280×720, captions burned in as a
DOM bar, fails loudly on a missing selector. The output is `assets/video/tour_<lang>.webm` with a **4 MB budget**
(drop to 1024×576 if over).

| t (s) | Action | Caption |
|---|---|---|
| 0–6 | START → meteor → Home hero | "TALA reads 12,000 health-service comments: what people say, and where." |
| 6–14 | *Where are people?* → Text vs GPS, disagreement lines on the map | "Many comments name a place. TALA checks it against the GPS." |
| 14–22 | Location source → Repaired; the map snaps into the Philippines | "Wrong coordinates are repaired from what people wrote." |
| 22–30 | Places → Region | "Group comments into places." |
| 30–40 | What sets a place apart: Davao vs rest | "See which words make a place different." |
| 40–50 | How each place feels → bubble map | "Compare how each place feels." |
| 50–60 | Where complaints cluster → hotspot grid | "Find where complaints cluster beyond chance." |
| 60–70 | Sidebar stars, then Place report cards | "Each finished step lights a star. Jump anywhere, any time." |
| 70–76 | Open a Learn panel, end on the hero | "Want the theory? Open Learn on any page, or How TALA works." |

## 15. Task J: record, docs, QA

Record all five tours and spot-check frames. Update `smoke_e2e.cjs` (hidden native nav, nine pages, Learn page, every
sidebar link). Update the README (place-first story, new methods, gazetteer attribution, tour, how to re-record, removed
dependencies). Save before/after screenshots to `docs/screenshots/` for the panel response.

---

## 16. Acceptance, mapped to the panel

| # | Concern | Done when |
|---|---|---|
| 1 | Wordy landing | Home = hero, two chapter cards, video, collapsed data peek; theory is one click away. |
| 2 | Confusing sequence | The constellation sidebar shows numbered steps with states and in-order/any-order hints; cold-opened pages say what was run for you. |
| 3 | Video over text | A ~75 s captioned tour plays on Home in the UI language; one-sentence page intros; Learn collapsed. |
| 4 | Too similar to Rabajante | No page corresponds to one of his tabs; four methods he lacks; data-as-stars hero, question-titled chapters, constellation progress, five languages, custom chrome, meteor intro, no "Explorer". |

## 17. Resolved items (user, 2026-10-20)

Tagline kept. Chapter names **Lugar** and **Salita** approved. Video budget of about 20 MB approved. One-sentence page intros
approved. Appearance section removed (no palette pickers, no colour-blind toggle; the fixed palette is colour-blind
safe). Pending: meteor constants from `docs/motion/start_meteor.html`.

## 18. Out of scope

Leaving Streamlit, voice-over, per-step clips, region polygons/choropleths, and new sounds.

---

## 19. Addendum (2026-10-20): project identity, About page, tours everywhere

Evaluator comment: TALA comes from the **AIKasalig** project, but it looks like a personal project. It needs the project's
logos and description, and a more pronounced TALA banner. The user also asked for logos on the loading screen, a dedicated
About page, and clean per-language access to the tour videos, all responsive on web and mobile.

**Context** (from the proposal and MOA, kept out of git): AIKasalig is *Project 4* of the DOST **NICER** program "R&D Center
on Natural Language Processing for Health Applications" (RDC-NLPHA) at **National University**. Its full title is "Advancing
Responsible AI in Philippine Healthcare: A Multi-Year NLP-Driven Roadmap for Trust, Transparency, and Ethical AI", and it runs
from February 2026 to January 2029 (dates confirmed by the user; the proposal said January–December). Its goal is a multilingual AI Trust Toolkit (NLP in Filipino, Cebuano, Ilocano,
Hiligaynon and English), with AI-literacy modules among its outputs. TALA fits as a hands-on learning module in the same five
languages. The other projects in the program are HealthPH+, AdvocAid PH and Bantay Lamok PH.

**Logo order (fixed):** DOST, DOST-PCHRD, National University, NICER (DOST), NICER RDC-NLPHA, AIKasalig. The assets are in
`assets/logos/` (built by `tools/build_logos.py`, in `lg` and `sm` sizes) and rendered only through `core/brand.py`
(`strip_html(size)`, a white strip with optical sizing via `--logo-h`).

| # | Change | Where |
|---|---|---|
| 1 | **Loading screen:** a white logo strip at the bottom of the splash, with the line "AIKasalig · DOST-NICER RDC-NLPHA · National University". It uses the `lg` logos, sent once per session. Mobile: 3×2 wrap. | `core/splash.py` |
| 2 | **More pronounced TALA banner:** a taller hero, a larger wordmark with a gold glow, a bigger and brighter archipelago constellation, an "AIKasalig · DOST-NICER" eyebrow pill, and a white partner band directly under the hero (`sm` logos plus "A learning module of the AIKasalig project"). Mobile: text over a dimmed constellation, logos wrap. | `ui.header()`, `views/home.py`, CSS |
| 3 | **About the project page** (`views/about.py`, in the sidebar under How TALA works): the AIKasalig and program description, how TALA fits, a logo wall on a white card (`lg`), the four sister projects, the implementing agency and duration, and credits (project leader, TALA developer). The prose lives in `locales/pages/<lang>/about.md`. | new page |
| 4 | **Project footer on every page:** replace the personal-looking footer with a compact white `sm` logo strip and one line naming AIKasalig, NICER RDC-NLPHA and National University, plus a small developer credit. | `ui.footer()` |
| 5 | **Tours everywhere:** a sidebar "Watch the tour" button opens a `st.dialog` with the video. It defaults to the UI language, with a language picker inside the dialog that switches only the video. Home keeps its tour section. | `core/ui.py` |
| 6 | Translations for new strings and `about.md` (Opus); re-record the five tours (the UI changed); update the README and screenshots. | — |
