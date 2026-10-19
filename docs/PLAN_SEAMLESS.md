# TALA v2 plan: seamless flow, synth sound, pydeck maps

Status: approved for implementation (2026-10-19). Executor: Sonnet at medium effort, multi-agent, in waves.
Audience shift: TALA now targets **computer students with technical background**. Its UX bar is ARAW
(`C:\Users\mjmag\Desktop\ARAW\app`): guided flow, no dead ends, saved progress, language-first intro.
Visual redesign is **out of scope** (a later pass). Keep the current colours, fonts and layout language.

---

## 0. Ground rules for every agent

- **Environment.** Use `.venv` in the repo root (already created; Streamlit 1.66, pydeck 0.9.3).
  Python: `.venv/Scripts/python`. Tests: `.venv/Scripts/python -m pytest -q`. All 24 tests pass on `main` today.
- **Branch.** The orchestrator creates `feat/seamless-v2` from `main` before wave 1 and commits after each wave.
  Agents do not commit, push or open PRs. Nobody pushes until the user says so.
- **Stay in your lane.** Edit only the files your task owns (listed per task). If you need a change in a file you
  don't own, write it in your final report instead of making it.
- **Keep the house rules** in the existing docstrings. They are load-bearing:
  - Session state holds keys and parameters, **never DataFrames** (`core/data_loader.py`, enforced by `tests/test_concurrency.py`).
  - Heavy imports (sklearn, geopandas, pydeck, matplotlib, NLTK) stay **inside functions**, never at module top level in `core/`.
  - The active language is **never part of a cache key** (`tests/test_i18n.py`).
  - Exported CSV/GeoJSON field names and filenames are **not localized**.
- **i18n.** Every new user-visible string gets an English key in `locales/ui.en.json` under the page/area prefix
  (`audio.*`, `gate.*`, `track.*`, `home.*`, `geo_2_cluster.*` and so on). Do **not** write translations; missing keys
  fall back to English. If you delete a key, delete it from every `locales/ui.*.json` **and** `ui.*.draft.json`.
  Run `.venv/Scripts/python tools/i18n_tool.py check` before you finish.
- **Match the code style.** Explanatory docstrings that say *why*, `from __future__ import annotations`, and comment
  density like the surrounding code.
- **Finish with**: pytest green, i18n check clean, and a short report listing files changed, new public functions
  and their signatures, and anything left undone.

---

## 1. What we are building (summary)

| # | Feature | Owner task |
|---|---|---|
| 1 | Synth sound engine from the approved soundboard, replacing the MP3s, with per-area music | A |
| 2 | ARAW-style intro: **pick a language first** (that tap unlocks audio), then a loading splash **with sound**, then START | A |
| 3 | pydeck maps replace folium / streamlit-folium / branca | B |
| 4 | Guided tracks: progress strip, Back/Next, step done, track complete, Home "Continue" and "Your path" | C, D, E |
| 5 | Auto-run geo steps: no page ever stops on "run the previous page first" | E |
| 6 | Calmer layout: instant-apply data page, collapsed Learn panels, sidebar essentials + Settings | C |
| 7 | Smoothness: fragments, no dead-end `st.stop()`, toasts, fade-in, stable heights | C (infra), D, E (apply) |
| 8 | Save + resume in the browser (cookie): language, sound, settings, dataset, progress, last page | F |
| 9 | README and docs refresh, end-to-end smoke test | G |

---

## 2. Waves and file ownership

```
Wave 1 (parallel):  A  sound + intro        B  pydeck maps
Wave 2:             C  flow infrastructure + Home + Data page + layout
Wave 3 (parallel):  D  text pages 2-8       E  geo pages 1-5 + auto-run     F  save + resume
Wave 4:             G  docs + end-to-end QA
```
After each wave the orchestrator runs pytest and the i18n check, reviews the diff against this plan, then commits
(`feat(sound): …`, `feat(maps): …` and so on, each ending with the attribution trailer from the session).

Shared file: only `locales/ui.en.json` is edited by parallel agents. Use the Edit tool and append keys inside
your own prefix. If an edit fails because the file changed, re-read it and retry. Never rewrite the whole file.

| Task | Owns (may edit) |
|---|---|
| A | `core/audio.py`, `core/sound_engine.js` (new), `core/gate.py`, `core/splash.py`, `static/audio/*` (delete), `.streamlit/config.toml`, `docs/AUDIO.md`, `tests/test_audio.py`, `tests/test_splash.py`, `app.py` (only the `audio.mount(...)` call and boot section), `locales/*` (`audio.*`, `gate.*`, `boot.*` keys) |
| B | `core/maps.py` (new), `core/geo.py` (remove folium helpers only), `core/viz.py` (colour helpers), map sections of `views/geo_*.py`, `requirements.txt`, `tests/test_maps.py` (new), `locales/ui.en.json` (map keys) |
| C | `core/tracks.py` (new), `core/ui.py`, `assets/styles.css`, `app.py` (navigation, area to `audio.mount`), `views/home.py`, `views/text_1_data.py`, `tests/test_tracks.py` (new), `locales/*` (`track.*`, `home.*`, `side.*`, `learn.*`, `text_1_data.*`) |
| D | `views/text_2_wordcloud.py` … `views/text_8_themes.py`, `locales/ui.en.json` (their prefixes) |
| E | `views/geo_1_ingest.py` … `views/geo_5_nlp.py`, `core/data_loader.py`, `tests/test_concurrency.py` (only to follow the removed `SS_POINTS_READY`), `locales/ui.en.json` (geo prefixes) |
| F | `core/persist.py` (new), `app.py` (restore/save hooks only), `core/ui.py` (only the "Forget me" button in Settings, added after C), `tests/test_persist.py` (new), `locales/ui.en.json` (`persist.*`) |
| G | `README.md`, `docs/*.md`, `.streamlit/config.toml` comments, `app.py` docstring, `tools/smoke_e2e.cjs` (new) |

---

## 3. Task A: synth sound engine and language-first intro

### A1. Engine (`core/sound_engine.js`)
- **Source of truth:** `docs/sound/soundboard.html`. The user approved **all 48 sounds and loops as they are**.
  Copy these sections **verbatim**: ENGINE (`pulseWave` … `mel`), instruments (`bell`, `kick`, `hat`, `brush`,
  `crash`, `chirp`, `twinkleNote`, `TWINKLE`), `S` (every sound), MUSIC (`SONGS`, `parseTrack`, `songSteps`,
  `playSong`, `stopSong`). Do **not** retune any sound. Drop everything that touches the board UI (sprites,
  catalog, verdicts, scope canvas, DOM building).
- Wrap it in an idempotent IIFE that installs `window.__talaSound` once and **updates** it on later injections:
  ```js
  window.__talaSound = {
    unlock(),                       // create/resume AudioContext; safe to call on every gesture
    unlocked: bool,
    setPrefs({musicOn, musicVol, sfxOn, sfxVol, style}),   // style: 'melody' | 'ambience'
    area(name),                     // 'gate'|'home'|'text'|'geo'; switches music only when the area changes
    play(name, arg, delayMs=0),     // any S key; no-op if locked or SFX off
    special(name),                  // 'trackDone' | 'fullSky': plays fanfare, then music → 'harana' until area changes
    bootTimeline(fromPct, seconds, segments), // schedules progress ticks + bootReady (see A3)
    startPressed(),                 // 'start' cue, then music fades in after ~1.3 s
  }
  ```
- Area → song: `gate`/`home` → `gabi`, `text` → `buwan`, `geo` → `bituin`; `style: 'ambience'` → `kuliglig` everywhere.
  Music changes crossfade over about 0.6 s on `musicBus` gain (fade out, `stopSong`, `playSong`, fade in).
- Volumes map exactly like the board: `gain = (vol/100) ** 1.6`, and the echo sends follow their bus volume.
  `master` is fixed at 0.8 and `echo` at 0.55 (the board defaults).
- Pause music on `visibilitychange` hidden, and resume on visible (ARAW does the same).

### A2. Python side (`core/audio.py`)
- Delete the MP3 machinery: `AUDIO_URLS`, `STATIC_AUDIO_URLS`, `<audio>` elements, iOS volume-lock CSS/note
  (Web Audio gain works on iOS). Delete the `audio.ios_volume_note` key in every locale file.
  Delete `static/audio/*.mp3`, and set `enableStaticServing = false` in `.streamlit/config.toml` (also fix its comment).
- Keep the session keys `audio_music_on|volume`, `audio_sfx_on|volume` and the defaults (music on 25, SFX on 65).
  Add `SS_MUSIC_STYLE = "audio_music_style"` (default `"melody"`). The selectbox for it lives in C's Settings expander,
  but A exposes `audio.style_options()` returning `[("melody", i18n key), ("ambience", i18n key)]`.
- `mount(area: str)` replaces the current `mount(...)`:
  - **Engine payload once per session.** Read `core/sound_engine.js`, then inject it through the existing
    base64 bootstrap pattern (no `eval`, CSP-safe) **only if** `st.session_state["_tala_engine_sent"]` is unset.
    Set the flag after injecting. The DOM survives reruns, so later runs send only a small config script.
  - Every run injects the small config script: `__talaSound?.setPrefs({...}); __talaSound?.area("<area>")`.
  - The capture listener (installed once by the engine; re-installing replaces the old one, as today) does this:
    - **Any `pointerdown`/`keydown` → `unlock()`.** This is the gesture that makes audio legal.
    - Then classifies `click` targets (check in this order):

      | Target | Sound |
      |---|---|
      | `[data-testid="stSidebarNav"] a`, `[data-testid="stPageLink"] a` | `nav` |
      | `details > summary` | `learnOpen` if `details.open` is false before the click, else `learnClose` |
      | `[role="switch"]`, checkbox inputs, `[data-baseweb="checkbox"]` | `toggleOn` / `toggleOff` from the pre-click `aria-checked` / `checked` |
      | `[role="radio"]`, `[data-baseweb="radio"]`, `[role="option"]`, `li[role="option"]` | `select` |
      | `[data-testid="stDownloadButton"] button` | `download` |
      | `[data-testid="stCode"] button` (copy) | `copy` |
      | `.tala-gate-lang` (gate card buttons, see A3) | `language`, plus start the `gate` music |
      | `#tala-start` (splash START, see A3) | handled by `startPressed()` |
      | any other `button, a[href], [role="button"], [role="tab"], [role="menuitem"]` | `click` |
    - `pointerup` / `keyup` on `[role="slider"]` → `slider`, throttled to one every 150 ms.
    - A `MutationObserver` on `document.body` plays `run` when a `[data-testid="stSpinner"]` appears (at most one
      per second). Spinners only show on cache misses, so `run` means real compute.
- `cue(name: str, arg=None, delay_ms: int = 0)`: emit a tiny `st.html(..., unsafe_allow_javascript=True)` script
  that calls `__talaSound?.play(name, arg, delay_ms)`. Include a per-session counter nonce in the markup so
  Streamlit re-executes it even when the content would otherwise be identical. It must render with **no visible
  gap**: add a CSS rule in `inject_css` (ask C) or wrap it in an element container hidden with
  `:has(script)`. A owns the cue function; C styles the gap.
- `special(name)`: same, but calls `__talaSound?.special(name)`.
- `result(sig: str, params: tuple)` is a **context manager** for page results:
  ```python
  with audio.result("text5", (n_topics, seed, min_df)):
      topics = nlp.lda_topics(...)
  ```
  On exit it compares `(sig, params)` with `st.session_state["_tala_last_result"][sig]`. If they are unchanged,
  it plays nothing (a plain rerun). If they changed and elapsed ≥ 0.3 s, it plays `sig` (the page signature).
  If they changed but the call was faster, it plays `cached`. Then it stores the params. Exceptions propagate
  and play nothing.
- `sidebar_settings()` keeps Music and SFX toggles plus sliders (sliders disabled when the toggle is off). Remove
  `gate_settings()`'s hint about autoplay and keep the expander.

### A3. Intro flow, ARAW-style (`core/gate.py`, `core/splash.py`, `app.py` boot section)
ARAW's reference: `ARAW/app/src/app/boot.ts` (language landing, then splash with loading bar and START, once per session).

1. **Language gate** (no START button any more):
   - Five language cards (`st.button`, class hook: wrap them in `st.container(key="tala-gate-langs")`, and
     the click map uses `.st-key-tala-gate-langs button` for `language`). **The first tap is the gesture that unlocks
     audio**, so the `gate` music (`gabi`) starts right there and the card plays `language`.
   - Tapping highlights the card and previews the prompt in that language (existing behaviour, keep it).
   - Below the cards: a primary **"Continue ▸"** button (disabled until a language is picked) and the Sound
     settings expander. Continue → `i18n.set_lang(pick)`, `audio.mark_started()`, `st.rerun()`.
   - While the gate is visible and audio is unlocked, the engine plays `twinkle` every 7–9 s (stop when the gate
     element disappears; detect it with a marker class such as `.tala-gate-sky` in the gate art).
2. **Boot splash with sound** (`core/splash.py`):
   - The splash now always starts **after** a gesture (Continue), so audio is unlocked and the loading is audible.
   - Keep the real server-driven progress plus the client-side tail. In `finish()`, emit a cue script calling
     `__talaSound?.bootTimeline(from_pct, remaining_s, segments)`. The engine schedules one `progress(i)` tick per
     progress-bar segment as the CSS fills it (`i` = 1…8 climbing, matching the CSS timing), then `bootReady` at 100%.
   - At 100% the overlay shows a pixel **"▶ START"** button (`<button id="tala-start">`, plain HTML in the
     overlay, `pointer-events:auto`, focused automatically, Enter/Space work). Localize the label with `gate.start`.
   - **START is client-only:** `startPressed()` plays `start` (the shooting star), adds `tala-boot-complete` to
     `<body>` (the existing reveal mechanism), and sets the session cookie `tala_booted=1; path=/; SameSite=Lax`
     (no max-age). There is **no server rerun**: the page underneath is already rendered.
     Remove the old `_reveal_chrome_after` timer path.
   - **Fallback so nobody is trapped:** if JS or the engine is blocked, a CSS-only animation reveals the app
     12 s after 100%.
   - `boot()` returns `None` (no splash) if `st.context.cookies.get("tala_booted") == "1"`, so a refresh in the same
     browser session goes straight to the page (ARAW plays the splash once per session).
3. `prefers-reduced-motion`: keep the existing reduced-motion handling for the splash animation. Sound is unaffected.

### A4. Tests and docs
- Rewrite `tests/test_audio.py`:
  - `sound_engine.js` exists and contains every approved sound id. Assert the list: the 38 sound ids (the 48 rated
    cards minus 5 `music-*` and 5 `scene-*`), plus the song ids `gabi buwan bituin harana kuliglig`.
  - No `.mp3` files remain, and `enableStaticServing` is false.
  - The engine is sent once per session (simulate two `mount` calls with a fake session state, or test the flag logic).
  - `result()` plays nothing for unchanged params, `cached` for fast changed calls and the signature for slow ones
    (monkeypatch `cue` and `time.monotonic`).
- Update `tests/test_splash.py` for the START button and the cookie skip.
- Rewrite `docs/AUDIO.md`: synth engine, buses, echo, per-area music, event map (the table above), how to add a sound
  (prototype in the soundboard first, then copy), and the licensing section (everything is original, so no third-party rights).

---

## 4. Task B: pydeck maps

- New `core/maps.py`. Lazy-import `pydeck` inside the functions. Public API:
  ```python
  def view_for(lonlat_df) -> pdk.ViewState            # pdk.data_utils.compute_view, with a PH fallback (12.8, 121.8, zoom 5)
  def points_layer(df, color=(53,64,142,180), radius_px=3) -> pdk.Layer   # ScatterplotLayer, radiusUnits="pixels"
  def cluster_layer(gdf, palette_hexes) -> pdk.Layer   # colour per cluster_id; noise (-1) grey (153,153,153,120), smaller
  def grid_layer(cells_gdf, seq_hexes) -> pdk.Layer    # GeoJsonLayer from the server's occupied cells, fill by n_points
  def centroid_layer(cent_gdf, color_by=None) -> pdk.Layer  # radius by n_points (metres scaled), optional sentiment colour
  def land_layer() -> pdk.Layer                         # GeoJsonLayer of geo.ph_land(), faint fill + outline
  def deck(layers, view, tooltip_html=None) -> pdk.Deck # map_style=None so Streamlit's theme-aware Carto basemap is used
  def to_frame(gdf, extra_cols=(), tip=None, cap=50_000) -> pd.DataFrame
  ```
  - `to_frame` turns a GeoDataFrame into a **plain** DataFrame (`lon`, `lat` float, extra columns, `tip` str ≤ 90
    chars). It never passes shapely objects to pydeck, and samples down to `cap` rows (stable `random_state=1`)
    with a caption-worthy flag. It must not mutate its input (concurrency contract).
  - Colours: add `viz.hex_to_rgba(hex, alpha=200) -> list[int]` and reuse `viz.categorical` / `viz.sequential_hexes`.
- Replace each folium map **one-for-one** (same place on the page, height 520, `width="stretch"`):
  - `geo_1`: `points_layer` for **all** valid points (not a 3,000 sample), tooltip = first 90 chars of text.
  - `geo_2`: `cluster_layer`, tooltip "Cluster C3" / "Noise". Use `on_select="rerun"`, `selection_mode="single-object"`,
    `key="geo2_map"`. Under the map show the selected point's cluster: id and size, plus an `st.page_link` to
    "NLP per cluster". Put the map and the selection readout in an `@st.fragment` so a click reruns only that block.
  - `geo_3` grid: `grid_layer` plus a small legend (min to max, rendered with `st.caption` and a CSS gradient bar).
    Centroids: `centroid_layer`.
  - `geo_4`: `land_layer` + kept points (`cluster_layer`, or `points_layer` when there are no clusters). Add a
    checkbox **"Show removed points"** that adds a red layer of the points the clip removed (computed as the
    validated points not in the clipped set). This is a teaching win for CRS and bounds validation.
  - `geo_5`: `centroid_layer` coloured by majority sentiment (same colours as today), with a tooltip holding the
    same fields as today.
- Delete `base_map` and `cluster_marker_map` from `core/geo.py`. Remove `folium`, `streamlit-folium` and `branca` from
  `requirements.txt`, and add `pydeck>=0.9,<1` under "geospatial" with a one-line why-comment.
- Do **not** change page gating or flow (that's E). Touch only the map blocks and their imports.
- `tests/test_maps.py`:
  - each builder returns a layer, and `deck(...).to_json()` serializes;
  - `to_frame` has no geometry column, respects `cap` and leaves its input unchanged;
  - noise points are grey;
  - `grep`: no file under `core/`, `views/` or `app.py` imports `folium` or `branca`.

---

## 5. Task C: flow infrastructure, Home, Data page, calmer layout

### C1. `core/tracks.py` (new)
```python
TRACKS = {
  "text": ["text_1_data", "text_2_wordcloud", "text_3_sentiment", "text_4_ngrams",
           "text_5_topics", "text_6_keywords", "text_7_metrics", "text_8_themes"],
  "geo":  ["geo_1_ingest", "geo_2_cluster", "geo_3_generalize", "geo_4_map", "geo_5_nlp"],
}
SIGNATURE = {"text_1_data": "text1", ..., "geo_5_nlp": "geo5"}   # page → sound id
SS_DONE, SS_LAST_PAGE, SS_CELEBRATED = "tala_done_pages", "tala_last_page", "tala_celebrated"

def track_of(page) -> str | None
def position(page) -> tuple[str, int, int] | None   # (track, 1-based index, total)
def path_of(page) -> str                             # "views/<page>.py"
def neighbours(page) -> tuple[str | None, str | None]
def done_pages() -> set[str]                          # stored as a sorted list in session state
def mark_done(page) -> None
def area_for(url_path: str) -> str                   # 'home' | 'text' | 'geo'
```
`mark_done(page)`, the first time per page per session, does this:
- adds the page to `SS_DONE`;
- plays `audio.cue("step", delay_ms=700)`, so the step sound comes after the page signature (see the "Walking the geo pipeline" scene);
- if the track is now complete and not yet in `SS_CELEBRATED`, plays `audio.special("trackDone")` and shows a
  celebratory card (see C2);
- if **both** tracks are complete, plays `audio.special("fullSky")` (once).

### C2. `core/ui.py`
- `page_header(page, section)` adds two things. For track pages it shows a **progress strip** under the title:
  `TEXT TRACK · 3 / 8` with pixel segments (done = gold, current = outlined, to do = dim). Each segment is a
  tooltip-titled `st.page_link`, or a plain HTML link to the page's URL path. It also records
  `SS_LAST_PAGE = page`. Only Home keeps the big header. Track pages get a compact one-line header.
- `page_done(page)` calls `tracks.mark_done`. If this call completed a track, it renders the **track complete card**:
  "★ Text track complete", one line of what was covered, and buttons to start the other track or go Home.
- `track_footer(page)`: **◂ Back** and **Next ▸** as `st.page_link` buttons in a footer row. On the last page of a track,
  Next becomes "Finish → Home" (or "Start the Geo track" if Geo isn't done).
- `warn(msg)`, `error(msg)`, `info(msg)`: wrap `st.warning/error/info` and play `warn` / `error` (info is silent).
- `locked(msg, link_page, link_label)`: friendly card for pages that genuinely cannot run (for example no
  coordinates). It plays `locked` and shows a page link to fix it. **No bare `st.stop()` without one of these.**
- `learn_page(...)`: the expander is **collapsed by default** (`expanded=False`), titled `📖 Learn: <title>`.
  The sidebar toggle still hides it entirely.
- `sidebar_controls()` reorganized:
  1. Language select (as today);
  2. Sound: Music and SFX toggles and sliders (`audio.sidebar_settings()`);
  3. `⚙ Settings` expander: palettes, Filipino stopwords, custom stopwords, Learn toggle, music style
     (`audio.style_options()`);
  4. dataset caption.
- CSS (`assets/styles.css`):
  - main block fade-in on page change, 180 ms (disabled under `prefers-reduced-motion`);
  - progress strip and footer styles (pixel look, reuse the existing navy and gold);
  - hide the empty element containers made by cue scripts;
  - fixed min-heights for chart/map slots so pages don't jump while they compute.
- Replace `st.success(..., icon="➡️")` "go to the next page" nudges with the footer. Use `st.toast` for confirmations.

### C3. `app.py`
- Navigation stays in the sidebar. Compute `area = tracks.area_for(nav.url_path)` (or the page's url path) **before**
  `nav.run()`, then call `audio.mount(area)`.
- Keep the boot order (gate, then splash, then the rest), as reshaped by A.

### C4. `views/home.py`, ARAW-style
Top to bottom:
1. Greeting line.
2. **Continue card** (if `SS_LAST_PAGE` is set): "Continue: Topic Modeling (Text 5/8)" with a page link.
3. **Your path**: two track cards (Text 8 steps, Geo 5 steps) with progress segments, a done count, and
   Start / Continue / Review buttons.
4. Dataset summary (existing metrics plus a 15-row preview, collapsed in an expander).
5. Learn panel (collapsed).

### C5. `views/text_1_data.py`: instant apply
- The source radio shows the **current** source (bundled vs upload).
- The upload auto-activates with the guessed columns, then `st.toast` and `audio.cue("upload")`. Only on a **new** upload
  key, not on every rerun.
- Column selects apply on change (`on_change` → `dl.set_active`). Remove the "Use this dataset" button.
- The cleaning preview slider and output go inside `@st.fragment`.
- At the bottom: `ui.page_done(PAGE)` and `ui.track_footer(PAGE)`.

### C6. Guidance for D and E: the per-page recipe
Write it as a module docstring at the top of `core/tracks.py` so D and E can follow it:
```python
PAGE = "text_5_topics"
ui.page_header(PAGE, "text")
ui.learn_page(PAGE, code=...)
@st.fragment
def _controls_and_result():
    n = st.slider(...)
    with audio.result(tracks.SIGNATURE[PAGE], (n, ...)):
        res = nlp.lda_topics(...)
    ... render charts ...
_controls_and_result()
ui.page_done(PAGE)
ui.track_footer(PAGE)
```
Use a fragment only when its widgets affect nothing outside it. Otherwise leave the code unfragmented.
`tests/test_tracks.py` covers `position`, `neighbours`, `area_for`, idempotent `mark_done` (monkeypatch audio),
celebration once per track, and `fullSky` once.

---

## 6. Task D: text pages 2–8
For each of `text_2_wordcloud` … `text_8_themes`, apply the C6 recipe:
- `audio.result(<signature>, <params that change the fit>)` around the page's **main** compute
  (word cloud freqs, VADER, n-grams, LDA, RAKE, readability, TF-IDF K-Means).
- `@st.fragment` around self-contained control-and-result blocks (for example the sentiment threshold slider and its two
  charts; the word cloud colormap and size; topic count and words-per-topic; k for K-Means).
- `st.warning` / `st.error` → `ui.warn` / `ui.error`; `st.success` nudges → removed (the footer replaces them).
- End every page with `ui.page_done(PAGE)` then `ui.track_footer(PAGE)`.
- Keep the Learn code snippets and every teaching note.

## 7. Task E: geo pages 1–5 and auto-run
- `core/data_loader.py`:
  - delete `SS_POINTS_READY`;
  - `cluster_params()` returns the session params, else the defaults `DEFAULT_EPS_M = 15000.0`, `DEFAULT_MIN_SAMPLES = 10`;
  - add `cluster_params_are_default() -> bool`;
  - `reset_geo_chain()` keeps clearing the cluster and generalization params.
  - Update `tests/test_concurrency.py` only where it references the removed key.
- Every geo page: **no "run the previous page first" warnings**. Pages call the cached `geo.*_for` helpers directly.
  The first visit computes with defaults (the spinner shows, and the engine plays `run`). When defaults are in use,
  show one caption: "Using default DBSCAN (eps 15 km, min_samples 10). Tune it on Clustering", with a page link.
- The no-coordinates case → `ui.locked(msg, "text_1_data", "Pick coordinate columns")`.
- `geo_2`: writing `SS_CLUSTER_PARAMS` stays as it is today. Keep B's map fragment.
- `geo_3` centroids: use `cluster_params()` (now always available).
- Apply the C6 recipe: `audio.result("geoN", params)`, fragments, `ui.warn/error`, `ui.page_done`, `ui.track_footer`.

## 8. Task F: save and resume (`core/persist.py`)
- One cookie, `tala_prefs`: base64url(JSON), `{"v":1, ...}`, `Max-Age` 180 days, `Path=/`, `SameSite=Lax`.
  Read it with `st.context.cookies`. Write it with a tiny `st.html(..., unsafe_allow_javascript=True)` script
  (`document.cookie = ...`), **only when the payload changed** (keep a hash in session state).
- Saved fields:
  - language;
  - music and SFX on/volume, music style;
  - both palettes, Learn toggle, Filipino stopwords, custom stopwords (trimmed to 1,000 chars);
  - dataset (`source_key`, text/lon/lat columns, label);
  - cluster and generalization params;
  - done pages;
  - last page.

  Keep the encoded cookie ≤ 3,800 bytes. If it is too big, drop custom stopwords first.
- `restore()` runs at the very top of `app.py` (after `set_page_config`, **before** the gate check), once per session
  (flag `_tala_restored`). It validates every field and ignores bad or old data silently. If the saved upload key no
  longer resolves (`dl.dataset(key) is None`), it falls back to the bundled dataset. A restored language means
  `i18n.is_set()` is true, so **returning visitors skip the gate**. Together with A's `tala_booted` session cookie, a
  refresh lands straight on the same page (the URL path already identifies it).
- Audio for a returning visitor stays locked until their first click (browser rule). The engine starts the area
  music on that first `unlock()`.
- `save()` runs at the end of `app.py`, after `nav.run()` (in the `finally`, after `boot.finish`).
- Settings expander gets a **"Forget me on this computer"** button (workshop PCs are shared). It expires the cookie,
  clears session state, and reruns to the gate.
- `tests/test_persist.py`: round trip, size cap, a corrupt cookie is ignored, a bad language code is ignored, an evicted
  upload falls back, and no DataFrames end up in the payload.

## 9. Task G: docs and end-to-end QA
- **README**:
  - What it does (guided tracks, pydeck maps, save/resume);
  - **Sound** (synth engine, no audio files, soundboard at `docs/sound/soundboard.html`, per-area music);
  - Run locally: fix `cd tala_app` → repo root, and mention `.venv`;
  - Fitting in 1 GB: folium → pydeck, the MP3 removal saves 7 MB per visitor;
  - Project layout: `core/maps.py`, `core/tracks.py`, `core/persist.py`, `core/sound_engine.js`;
  - remove the stale "publication maps" claim unless one exists;
  - audience line: computer students.

  Also fix the stale `enforceSerializableSessionState` comment in `config.toml`, and update the `app.py` docstring
  (no folium; the intro order is language, then splash, then START).
- `tools/smoke_e2e.cjs` uses Playwright from `C:/Users/mjmag/Desktop/ARAW/app/node_modules/playwright` (Chromium
  already installed). Run it with the app started as
  `.venv/Scripts/streamlit run app.py --server.headless true --server.port 8599`. The script:
  1. opens `/`, taps "Filipino", checks the prompt changed, presses Continue;
  2. waits for the splash START, presses it, and checks that the overlay is gone and the sidebar is visible;
  3. visits all 13 pages by URL path; on each it waits for the script to finish and asserts no
     `[data-testid="stException"]` and no console errors;
  4. opens `/geo_4_map` directly in a fresh context with the saved cookie, and checks there is no gate, no splash
     (`tala_booted` set) and that the map renders (auto-run);
  5. reloads a page and checks it is the same page with the same language.

  Print a pass/fail table.
- Final: pytest green, i18n check clean, smoke green. Report to the user.

---

## 10. Out of scope (later)
- Visual redesign (night theme for the app chrome, typography): a separate pass.
- Deeper Learn content for CS students (maths, complexity, "export as notebook").
- Translating new strings (English fallback until the reviewer workbook round).
