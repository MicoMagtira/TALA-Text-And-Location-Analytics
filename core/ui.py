"""Shared UI helpers: header, footer, sidebar, journey flow (chapters), and 'Learn' panels.

The 'Learn' expanders turn each page into live teaching material by pairing the
concept with the equivalent code from the source notebook / lab.

Every user-visible string here goes through :func:`core.i18n.t`, so the app
renders in the language chosen on the boot gate. Anything without a translation
falls back to English per key, which is what lets English copy be improved
without waiting on four translations.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st

from . import audio, data_loader as dl
from . import i18n, tracks
from .viz import DEFAULT_CATEGORICAL, DEFAULT_SEQUENTIAL, load_css

ASSETS = Path(__file__).resolve().parent.parent / "assets"

SS_TEACH = "teach_mode"
SS_CUSTOM_SW = "custom_stopwords"
SS_USE_TL = "use_tagalog"
SS_LANG_WIDGET = "lang_switcher"
SS_HERO_LANG = "tala_hero_lang"   # the language chips on Home's hero

# Which pill each page sits under. Kept here rather than passed per page so a
# page cannot drift out of its section when titles are edited.
_PILL = {"learn": "pill.learn"}

# English fallbacks for non-journey page headers until the catalog has the keys.
_TITLE_EN = {"about": "About the project"}
_BLURB_EN = {"about": "TALA is a hands-on learning module of AIKasalig, a project on "
                      "responsible AI in Philippine health care."}


def _t(key: str, default: str, **fmt) -> str:
    """``i18n.t`` with an English default for keys not yet merged into the catalog."""
    out = i18n.t(key, **fmt)
    return default.format(**fmt) if out == key else out


def nav_title(page: str) -> str:
    """A page's short name for the sidebar, strip and footer."""
    return _t(f"{page}.nav", tracks.NAV_EN.get(page, page))


def inject_css() -> None:
    css_path = ASSETS / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{load_css(str(css_path))}</style>", unsafe_allow_html=True)


def _on_hero_language() -> None:
    """A hero chip was pressed: switch language and keep the sidebar selectbox in step.

    The chips are a widget (not links) because a link reloads the tab and drops
    the session. Re-pressing the active chip deselects it (``None``); that is
    ignored and the chip snaps back on the next run."""
    code = st.session_state.get(SS_HERO_LANG)
    if code in i18n.LANGS:
        i18n.set_lang(code)
        st.session_state[SS_LANG_WIDGET] = code


def header() -> None:
    """Home's hero: the project banner, then the partner band right under it.

    The hero is a keyed container so the stylesheet can paint it
    (``.st-key-tala-hero``): an "AIKasalig · DOST-NICER" eyebrow, the TALA
    wordmark in gold, the tagline and the language chips, over the survey's own
    coordinates drawn as stars (``core.sky``). The evaluator read the old,
    smaller banner as a personal project, so the project is named before the app.

    The white partner band below it carries the ``sm`` logos (cached string, as
    Home re-renders on every chip press) and a link to the About page. It is a
    ``st.page_link``, not an anchor: an anchor would reload the tab and drop the
    session."""
    from . import brand, sky
    from .splash import GOLD, STAR, _sprite_svg

    star = _sprite_svg(STAR, {"#": GOLD}, pixel=7, extra_class="tala-hero-star")
    tagline = i18n.t("app.subtitle").replace(". ", ".<br>", 1)
    with st.container(key="tala-hero"):
        st.markdown(
            f'<div class="tala-hero-sky">{sky.active_sky_svg(1000, 400)}</div>'
            f'<div class="tala-hero-text"><span class="tala-hero-eyebrow">{brand.EYEBROW}</span>'
            f'<h1>{star}<span class="tala-hero-word">TALA</span></h1>'
            f'<div class="tala-hero-org">{i18n.t("app.wordmark_sub")}</div>'
            f'<p class="tala-hero-tag">{tagline}</p></div>',
            unsafe_allow_html=True,
        )
        # Assigned before the widget exists in this run, so a switch made in the
        # sidebar is reflected here.
        st.session_state[SS_HERO_LANG] = i18n.current()
        st.segmented_control(
            i18n.t("side.language_pick"), list(i18n.LANGS), key=SS_HERO_LANG,
            format_func=str.upper, on_change=_on_hero_language,
            label_visibility="collapsed",
        )
    with st.container(key="tala-partners"):
        st.markdown(brand.strip_html("sm"), unsafe_allow_html=True)
        st.page_link(tracks.path_of("about"),
                     label=_t("brand.module_line", "A learning module of the AIKasalig project"),
                     icon=":material/arrow_forward:", icon_position="right")


def footer() -> None:
    """The project footer on every page: partner logos, one line, a small credit.

    It re-renders on every interaction, so it uses the ``sm`` logos only (a
    cached string of a few tens of KB). The developer credit stays, but small
    and below the project line: TALA is the project's, not a personal app."""
    from . import brand

    line = _t("footer.line", "A learning module of AIKasalig, DOST-NICER R&D Center on "
              "Natural Language Processing for Health Applications, National University")
    dev = _t("footer.dev", "Developed by {name}", name=brand.DEVELOPER)
    st.markdown(
        f'<div class="tala-footer">{brand.strip_html("sm", "tala-logos tala-logos-foot")}'
        f'<p class="tala-footer-line"><strong>TALA</strong> · {line}</p>'
        f'<p class="tala-footer-dev">{dev}</p></div>',
        unsafe_allow_html=True,
    )


# --- Tour dialog ----------------------------------------------------------------
# One captioned tour per UI language (tools/record_tour.cjs). The sidebar button
# opens it on every page; Home also embeds it inline.
VIDEO_DIR = ASSETS / "video"
SS_TOUR_OPEN = "_tala_tour_open"
SS_TOUR_LANG = "tala_tour_lang"     # the dialog's own picker; never the app language


def tour_files() -> dict[str, Path]:
    """``{lang: path}`` for every recorded tour, in the gate's language order."""
    return {code: p for code in i18n.LANGS
            if (p := VIDEO_DIR / f"tour_{code}.webm").exists()}


def tour_for(lang: str) -> Path | None:
    """The tour in ``lang``, else English, else any; None when none is recorded."""
    files = tour_files()
    return files.get(lang) or files.get("en") or next(iter(files.values()), None)


def _open_tour() -> None:
    """Sidebar button callback: ask this run to open the dialog in the UI language.

    A callback (not the button's return value) because the sidebar nav can be
    drawn twice in one run with different keys; a callback still fires for the
    copy that was clicked. The picker's value is set before it is created."""
    files = tour_files()
    lang = i18n.current()
    st.session_state[SS_TOUR_LANG] = lang if lang in files else next(iter(files), None)
    st.session_state[SS_TOUR_OPEN] = True


def _tour_body() -> None:
    """The dialog's content. A dialog is a fragment, so the picker reruns only this."""
    files = tour_files()
    if not files:
        return
    st.segmented_control(
        _t("tour.lang", "Tour language"), list(files), key=SS_TOUR_LANG,
        format_func=str.upper, required=True,
    )
    lang = st.session_state.get(SS_TOUR_LANG)
    path = files.get(lang) or tour_for(i18n.current())
    # VP9 WebM: st.video labels files video/mp4 by default, which Safari and
    # Firefox refuse to play when the bytes are actually WebM.
    st.video(str(path), format="video/webm", autoplay=True, muted=True)
    st.caption(_t("tour.note", "Captioned, no sound. The picker changes only the video, "
                               "not the app's language."))


def maybe_open_tour() -> None:
    """Open the tour dialog if the sidebar button asked for it in this run.

    Called once per run from ``sidebar_controls`` (outside the nav slot, which
    can be redrawn and would take the dialog with it). The title is resolved
    here, at run time, so it follows the reader's language."""
    if st.session_state.pop(SS_TOUR_OPEN, False) and tour_files():
        st.dialog(_t("tour.title", "Watch the tour"), width="large",
                  icon=":material/play_circle:")(_tour_body)()


def source_label() -> str:
    """The active dataset's name, localized when it is the bundled example.

    Uploads keep the user's own filename — translating that would be wrong."""
    src = st.session_state.get(dl.SS_SOURCE, "n/a")
    return i18n.t("data.bundled_label") if src == dl.BUNDLED_LABEL else src


def _on_language_change() -> None:
    """Commit a sidebar language switch.

    Switching costs nothing heavy: only the render layer is localized, so the
    shared geo layers and fitted models stay in cache and are reused verbatim
    in the new language."""
    i18n.set_lang(st.session_state[SS_LANG_WIDGET])


def _set_head(key: str) -> None:
    """A small uppercase group label inside the Settings panel."""
    st.markdown(f'<p class="tala-set-head">{i18n.t(key)}</p>', unsafe_allow_html=True)


def sidebar_controls() -> None:
    """Global sidebar: the page list, one Settings panel, then the dataset caption.

    Language and sound sit inside Settings with everything else, so the sidebar
    reads as track navigation first and configuration second."""
    dl.ensure_loaded()
    maybe_open_tour()

    with st.sidebar.expander(i18n.t("side.settings"), expanded=False,
                             icon=":material/settings:"):
        # Language first: a trainee who picked the wrong card on the gate, or a
        # trainer demoing the same page in two languages, should not have to reload.
        _set_head("side.language")
        st.session_state.setdefault(SS_LANG_WIDGET, i18n.current())
        st.selectbox(
            i18n.t("side.language_pick"), list(i18n.LANGS), key=SS_LANG_WIDGET,
            format_func=i18n.label, on_change=_on_language_change,
            label_visibility="collapsed",
        )

        audio.sidebar_settings(st)
        styles = dict(audio.style_options())
        st.selectbox(i18n.t("audio.style"), list(styles), key=audio.SS_MUSIC_STYLE,
                     format_func=lambda v: i18n.t(styles[v]))

        _set_head("side.learning")
        st.session_state.setdefault(SS_TEACH, True)
        st.toggle(i18n.t("side.show_learn"), key=SS_TEACH)

        # Workshop PCs are shared: let a trainee wipe what TALA saved here.
        if st.button(i18n.t("persist.forget"), key="tala_forget",
                     help=i18n.t("persist.forget_help"), icon=":material/delete:"):
            from . import persist

            persist.forget()

    st.sidebar.caption(i18n.t("side.data", source=source_label()))
    st.sidebar.caption(i18n.t("side.rows",
                              rows=f"{len(dl.active_df()):,}",
                              column=st.session_state.get(dl.SS_TEXT_COL)))


def palette() -> str:
    """The categorical palette name. Fixed: TALA has no palette picker, and the
    one palette is colour-blind safe (see ``core.viz``)."""
    return DEFAULT_CATEGORICAL


def seq_palette() -> str:
    """The sequential palette name (fixed, as :func:`palette`)."""
    return DEFAULT_SEQUENTIAL


def stopwords() -> set:
    from . import preprocess

    return preprocess.build_stopwords(
        st.session_state.get(SS_CUSTOM_SW, ""),
        st.session_state.get(SS_USE_TL, True),
    )


# ---------------------------------------------------------------------------
# Page scaffolding — every page renders through these two calls
# ---------------------------------------------------------------------------
def page_header(page: str, section: str) -> None:
    """Pill + title + blurb, resolved from the catalog by page name.

    ``page`` is the view's module stem (``p5_feel``), which is also the
    key prefix and the name of its Learn essay file. One identifier, so a page
    cannot drift out of sync with its own translations.

    Track pages get a compact header and the progress strip, and record
    themselves as the last page visited (Home's "Continue" card reads it). Only
    Home keeps the big banner (``header()``, drawn by app.py)."""
    # ``section`` is a chapter key ("where"/"what"), "home", "learn", or a legacy
    # track name. Chapter pills show the untranslated chapter name.
    # The About page's pill is the project's name, untranslated like the chapters.
    if section in tracks.NAMES:
        pill = tracks.NAMES[section]
    elif section == "about":
        from . import brand

        pill = brand.PROJECT
    else:
        pill = i18n.t(_PILL[section])
    st.markdown(f'<span class="tala-pill">{pill}</span>', unsafe_allow_html=True)
    # "learn.title" is already the Learn panel's "Learn: {title}" format, so the
    # How TALA works page keeps its own title key.
    title_key, default = (("learn.page_title", "How TALA works") if page == "learn"
                          else (f"{page}.title", _TITLE_EN.get(page) or tracks.NAV_EN.get(page, page)))
    st.markdown(f"## {_t(title_key, default)}")
    pos = tracks.position(page)
    if pos:
        st.session_state[tracks.SS_LAST_PAGE] = page
        _progress_strip(page, *pos)
    blurb = _t(f"{page}.blurb", _BLURB_EN.get(page, ""))
    if blurb:
        st.markdown(blurb)


def strip_html(chapter: str, current: str | None = None) -> str:
    """A chapter's steps as a static constellation (Home's chapter cards).

    Same visual language as the page progress strip: one star per step on a
    connecting line, gold when done, glowing for the current step."""
    done = tracks.done_pages()
    stars = []
    for p in tracks.CHAPTERS[chapter]:
        state = "current" if p == current else ("done" if p in done else "todo")
        stars.append(f'<i class="tala-star tala-star-{state}" title="{nav_title(p)}"></i>')
    return f'<div class="tala-constellation">{"".join(stars)}</div>'


def _progress_strip(page: str, chapter: str, index: int, total: int) -> None:
    """``LUGAR . Step 2 of 9`` plus the chapter as a row of clickable stars.

    The sidebar numbers steps 1-9 across the journey, so the strip uses the same
    number; a per-chapter "1 / 6" would call one page both step 1 and step 4.

    Stars are ``st.page_link`` rather than plain anchors: an anchor would reload
    the browser tab and start a fresh session. Each sits in a keyed container so
    the stylesheet can draw it by state (done, current, to do); the step number
    stays in the link text for screen readers."""
    step = _t("track.step_of", "Step {n} of {total}",
              n=tracks.step_number(page), total=len(tracks.ALL_PAGES))
    st.caption(f"{tracks.NAMES.get(chapter, chapter).upper()} \u00b7 {step}")
    done = tracks.done_pages()
    with st.container(key="tala-strip"):
        for col, p in zip(st.columns(total, gap="small"), tracks.CHAPTERS[chapter]):
            state = "current" if p == page else ("done" if p in done else "todo")
            with col, st.container(key=f"tala-seg-{state}-{p}"):
                n = tracks.step_number(p)
                # No ``help=``: a tooltip makes Streamlit render the link twice.
                # The visually hidden label carries the step and page name instead.
                st.page_link(tracks.path_of(p), label=f"{n}. {nav_title(p)}",
                             disabled=(p == page))


def _step_ranges(pages: list[str]) -> str:
    """Journey step numbers as ``2\u20133`` / ``1, 3`` for the auto-ran line."""
    nums = sorted(tracks.step_number(p) for p in pages)
    runs: list[list[int]] = []
    for n in nums:
        if runs and n == runs[-1][-1] + 1:
            runs[-1].append(n)
        else:
            runs.append([n])
    return ", ".join(str(r[0]) if len(r) == 1 else f"{r[0]}\u2013{r[-1]}" for r in runs)


def auto_ran(page: str) -> None:
    """A quiet line when earlier steps were skipped: TALA ran them with defaults.

    Never stops the page and plays no sound; it only says what happened and
    links to the earliest skipped step so the trainee can go and tune it."""
    skipped = tracks.skipped_upstream(page, tracks.done_pages())
    if not skipped:
        return
    steps = _step_ranges(skipped)
    key = "auto.ran_one" if len(skipped) == 1 else "auto.ran_many"
    default = ("Step {steps} hasn't been opened yet, so TALA ran it with default settings."
               if len(skipped) == 1 else
               "Steps {steps} haven't been opened yet, so TALA ran them with default settings.")
    first = skipped[0]
    with st.container(border=True, key="tala-autoran"):
        st.markdown(f":material/info: {_t(key, default, steps=steps)}")
        st.page_link(tracks.path_of(first),
                     label=_t("auto.open", "Open step {n}: {title}",
                              n=tracks.step_number(first), title=nav_title(first)),
                     icon=":material/arrow_forward:", icon_position="right")


def sidebar_nav(current: str = "", redraw: bool = False) -> None:
    """The constellation navigation: Home, How TALA works, then both chapters.

    ``st.navigation(position="hidden")`` hides Streamlit's own list, and this
    draws the real one. Every entry is ``st.page_link`` (an anchor would reload
    the tab and drop the session; the engine's click sound also matches
    ``stPageLink``). Step links sit in keyed containers
    ``tala-nav-{done|current|todo}-{page}`` so the stylesheet can draw stars on
    a connecting line. ``current`` is the active page's url_path ("" for Home).

    ``redraw=True`` is for the second draw in one run (after a step was just
    completed): container keys must be unique per run, so it adds a ``-r`` suffix
    that the stylesheet's prefix selectors ignore."""
    done = tracks.done_pages()
    sfx = "-r" if redraw else ""
    with st.container(key=f"tala-navbox{sfx}"):
        for page, label_key, label_default, icon in (
                ("home", "nav.home", "Home", ":material/home:"),
                ("learn", "nav.learn", "How TALA works", ":material/menu_book:"),
                ("about", "nav.about", "About the project", ":material/info:")):
            with st.container(key=f"tala-nav-top-{page}{sfx}"):
                st.page_link(tracks.path_of(page), label=_t(label_key, label_default), icon=icon)
        # The tour sits with the top links on every page. A button, not a link:
        # it opens a dialog over the current page (see maybe_open_tour).
        if tour_files():
            with st.container(key=f"tala-nav-top-tour{sfx}"):
                st.button(_t("tour.button", "Watch the tour"), key=f"tala-tour-btn{sfx}",
                          on_click=_open_tour, icon=":material/play_circle:",
                          type="tertiary", width="stretch")
        for chapter, pages in tracks.CHAPTERS.items():
            hint = (_t("nav.hint_ordered", "in order") if tracks.ORDERED[chapter]
                    else _t("nav.hint_any", "any order"))
            q = _t(f"nav.q_{chapter}", "Where are people?" if chapter == "where"
                   else "What is each place saying?")
            st.markdown(
                f'<div class="tala-nav-chap"><span class="tala-nav-name">{tracks.NAMES[chapter]}</span>'
                f'<span class="tala-nav-hint">{hint}</span>'
                f'<span class="tala-nav-q">{q}</span></div>',
                unsafe_allow_html=True)
            with st.container(key=f"tala-navchap-{chapter}{sfx}"):
                for p in pages:
                    state = ("current" if p == current else
                             "done" if p in done else "todo")
                    with st.container(key=f"tala-nav-{state}-{p}{sfx}"):
                        st.page_link(tracks.path_of(p),
                                     label=f"{tracks.step_number(p)}  {nav_title(p)}")


def page_done(page: str) -> None:
    """Mark this page's step finished; if that completed a chapter, show the card.

    The card is tied to the page that completed the chapter, so it stays put across
    reruns of that page instead of vanishing on the first slider touch."""
    was_done = page in tracks.done_pages()
    tracks.mark_done(page)
    if not was_done and tracks.chapter_of(page):
        st.toast(i18n.t("track.step_done"), icon=":material/star:")
    just = st.session_state.get(tracks.SS_JUST_COMPLETED)
    if just and just[0] == page:
        _track_complete_card(just[1])


def _track_complete_card(chapter: str) -> None:
    other = tracks.other_chapter(chapter)
    with st.container(border=True, key="tala-complete"):
        st.markdown(f"### {_t(f'track.complete_{chapter}', 'Chapter complete: ' + tracks.NAMES[chapter])}")
        st.write(_t(f"track.covered_{chapter}", ""))
        c1, c2 = st.columns(2)
        with c1:
            if not tracks.track_complete(other):
                st.page_link(tracks.path_of(tracks.first_todo(other)),
                             label=_t(f"track.start_{other}", "Start " + tracks.NAMES[other]),
                             icon=":material/arrow_forward:", icon_position="right")
        with c2:
            st.page_link(tracks.path_of("home"), label=i18n.t("track.go_home"),
                         icon=":material/home:")


def track_footer(page: str) -> None:
    """Back and Next at the foot of a journey page: the page's only way onward.

    On a chapter's last page Next becomes "start the other chapter" (while it is
    unfinished) or "Finish, Home"."""
    chapter = tracks.chapter_of(page)
    if chapter is None:
        return
    prev, nxt = tracks.neighbours(page)
    other = tracks.other_chapter(chapter)
    if nxt:
        target, label = nxt, i18n.t("track.next")
    elif not tracks.track_complete(other):
        target, label = tracks.first_todo(other), _t(f"track.start_{other}", "Start " + tracks.NAMES[other])
    else:
        target, label = "home", i18n.t("track.finish")
    # Back and Next sit side by side in the centre, styled as one pair.
    with st.container(key="tala-footnav", horizontal=True,
                      horizontal_alignment="center", gap="medium"):
        if prev:
            st.page_link(tracks.path_of(prev), label=i18n.t("track.back"),
                         help=nav_title(prev), icon=":material/arrow_back:")
        st.page_link(tracks.path_of(target), label=label,
                     icon=":material/arrow_forward:", icon_position="right")


def warn(msg: str) -> None:
    """``st.warning`` that also plays the warning sound."""
    st.warning(msg)
    audio.cue("warn")


def error(msg: str) -> None:
    """``st.error`` that also plays the error sound."""
    st.error(msg)
    audio.cue("error")


def info(msg: str) -> None:
    """``st.info``; silent by design."""
    st.info(msg)


def locked(msg: str, link_page: str, link_label: str) -> None:
    """A friendly card for a page that genuinely cannot run (no coordinates, say).

    Shows the reason and a link to where it is fixed, plays ``locked``, draws the
    track footer so the page is never a dead end, then ends the run. Callers do
    not need their own ``st.stop()``."""
    audio.cue("locked")
    with st.container(border=True, key="tala-locked"):
        st.markdown(f"#### :material/lock: {msg}")
        st.page_link(tracks.path_of(link_page), label=link_label,
                     icon=":material/arrow_forward:", icon_position="right")
    last = st.session_state.get(tracks.SS_LAST_PAGE)
    if last:
        track_footer(last)
    st.stop()


def learn_page(page: str, code: str | None = None, lang: str = "python") -> None:
    """Render a page's Learn essay from ``locales/pages/<lang>/<page>.md``.

    The prose lives in the catalogs, not in the view, so translating a page
    never means touching Python and improving the English never means editing
    fourteen files. ``code`` stays in the view because code snippets are not
    translated in any language — a trainee retypes them into Colab as-is."""
    if not st.session_state.get(SS_TEACH, True):
        return
    keys = [k for k in i18n.page_blocks(page) if k != "title"]
    body = "\n\n".join(filter(None, (i18n.tm(page, k) for k in keys)))
    with st.expander(i18n.t("learn.title", title=i18n.tm(page, "title")),
                     expanded=False):
        st.markdown(f"> {i18n.t('learn.routine')}")
        st.markdown(i18n.t("learn.understand"))
        st.markdown(body)
        st.markdown(i18n.t("learn.try_heading"))
        st.markdown(i18n.t("learn.try_body"))
        st.markdown(i18n.t("learn.discuss_heading"))
        st.markdown(i18n.t("learn.discuss_body"))
        if code:
            with st.expander(i18n.t("learn.see_code"), expanded=False):
                st.code(code, language=lang)
