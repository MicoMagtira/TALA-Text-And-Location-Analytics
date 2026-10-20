// Automated, captioned tour recorder for TALA (docs/PLAN_PANEL.md, section 14).
//
// Usage (start the app first, e.g. .venv/Scripts/streamlit run app.py --server.headless true --server.port 8599):
//   node tools/record_tour.cjs [en|fil|ceb|ilo|hil|all]        (default: en)
// Environment:
//   BASE_URL         app address                     (default http://localhost:8599)
//   PLAYWRIGHT_PATH  playwright module to require    (default ARAW's install, like smoke_e2e.cjs)
//   OUT_DIR          where tour_<lang>.webm is put   (default assets/video)
//   SHOTS=1          also save a PNG per beat to %TEMP%/tala_tour_beat_<n>.png (for reviewing frames)
//
// How it works
//   One fresh browser + context per language, recording video at 1280x720 (no cookies, so the language gate and
//   the START splash/meteor are part of the video). It passes the gate by clicking the language card, presses
//   START, then walks the nine-beat storyboard with smooth mouse moves and a fake cursor dot (headless video has
//   no cursor). Navigation is always by clicking the sidebar st.page_link entries (found by their keyed container
//   class `.st-key-tala-nav-<state>-<page>`); page.goto would reload and reset the session.
//
// Captions
//   A fixed pill at the bottom centre of the page DOM, injected by page.evaluate before each beat (and re-injected
//   each time, so it survives navigation). Text for beat n is key `tour.c<n>` from locales/ui.<lang>.json (.t),
//   else locales/ui.en.json, else the English text in locales/_pending/I.json, else FALLBACK below.
//
// Failing loudly
//   Every beat names a selector that must appear within TIMEOUT; a st.exception anywhere also fails. On failure the
//   script prints the beat name and exits non-zero, and no video is written, so a broken UI never yields a quietly
//   broken tour.
//
// Re-recording after a UI change
//   Run it again for the languages you need (or `all`). If a beat fails, fix the selector in BEATS below (or the UI),
//   then rerun. Size budget is 4 MB; over budget the language is automatically re-recorded at 1024x576.
//   No ffmpeg re-encode is done.
const fs = require("fs");
const os = require("os");
const path = require("path");

const PW = process.env.PLAYWRIGHT_PATH || "C:/Users/mjmag/Desktop/ARAW/app/node_modules/playwright";
const { chromium } = require(PW);

const ROOT = path.resolve(__dirname, "..");
const BASE = process.env.BASE_URL || "http://localhost:8599";
const OUT_DIR = path.resolve(process.env.OUT_DIR || path.join(ROOT, "assets", "video"));
const SHOTS = process.env.SHOTS === "1";
const BUDGET = 4 * 1024 * 1024;
const TIMEOUT = 90000;
const LANGS = ["en", "fil", "ceb", "ilo", "hil"];
const ENDONYM = { en: "English", fil: "Filipino", ceb: "Bisaya", ilo: "Ilokano", hil: "Ilonggo" };

// ---- captions -------------------------------------------------------------------------------------------------
const readJson = (p) => { try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch { return {}; } };
const PENDING = readJson(path.join(ROOT, "locales", "_pending", "I.json"));
const EN = readJson(path.join(ROOT, "locales", "ui.en.json"));
const FALLBACK = {
  "tour.c1": "TALA reads 12,000 health-service comments: what people say, and where.",
  "tour.c2": "Many comments name a place. TALA checks it against the GPS.",
  "tour.c3": "Wrong coordinates are repaired from what people wrote.",
  "tour.c4": "Group comments into places.",
  "tour.c5": "See which words make a place different.",
  "tour.c6": "Compare how each place feels.",
  "tour.c7": "Find where complaints cluster beyond chance.",
  "tour.c8": "Each finished step lights a star. Jump anywhere, any time.",
  "tour.c9": "Want the theory? Open Learn on any page, or How TALA works.",
};
function captionFor(lang, n) {
  const key = `tour.c${n}`;
  const cat = lang === "en" ? {} : readJson(path.join(ROOT, "locales", `ui.${lang}.json`));
  return (cat[key] && cat[key].t) || EN[key] || PENDING[key] || FALLBACK[key];
}

// Runs in every document: fake cursor dot + caption bar helper.
const INIT_SCRIPT = () => {
  const ensure = () => {
    if (!document.body) return null;
    let dot = document.getElementById("tala-fake-cursor");
    if (!dot) {
      dot = document.createElement("div");
      dot.id = "tala-fake-cursor";
      dot.style.cssText = "position:fixed;left:-50px;top:-50px;width:20px;height:20px;margin:-10px 0 0 -10px;" +
        "border-radius:50%;background:rgba(255,196,60,.85);border:2px solid #fff;box-shadow:0 0 8px rgba(0,0,0,.6);" +
        "z-index:2147483647;pointer-events:none;";
      document.body.appendChild(dot);
    }
    return dot;
  };
  let last = null;
  window.addEventListener("mousemove", (e) => {
    last = [e.clientX, e.clientY];
    const d = ensure();
    if (d) { d.style.left = e.clientX + "px"; d.style.top = e.clientY + "px"; }
  }, true);
  window.__talaCaption = (text) => {
    if (!document.body) return;
    let bar = document.getElementById("tala-tour-caption");
    if (!bar) {
      bar = document.createElement("div");
      bar.id = "tala-tour-caption";
      bar.style.cssText = "position:fixed;left:50%;bottom:28px;transform:translateX(-50%);max-width:80%;" +
        "padding:12px 24px;border-radius:999px;background:rgba(10,14,30,.82);color:#fff;font:500 20px/1.35 " +
        "system-ui,-apple-system,'Segoe UI',sans-serif;text-align:center;z-index:2147483646;pointer-events:none;" +
        "opacity:0;transition:opacity .4s ease;box-shadow:0 2px 14px rgba(0,0,0,.5);";
      document.body.appendChild(bar);
    }
    if (bar.textContent === text && bar.style.opacity === "1") return;
    bar.style.opacity = "0";
    setTimeout(() => { bar.textContent = text; bar.style.opacity = "1"; }, 250);
  };
  const keep = () => { const d = ensure(); if (d && last) { d.style.left = last[0] + "px"; d.style.top = last[1] + "px"; } };
  document.addEventListener("DOMContentLoaded", keep);
};

// ---- helpers --------------------------------------------------------------------------------------------------
class BeatError extends Error {}
const sleep = (page, ms) => page.waitForTimeout(ms);

async function settle(page, timeout = TIMEOUT) {
  await page.waitForTimeout(600);
  await page.waitForFunction(() => {
    const app = document.querySelector('[data-testid="stApp"]');
    const running = app && app.getAttribute("data-test-script-state") === "running";
    return app && !running && !document.querySelector('[data-testid="stStatusWidget"]');
  }, null, { timeout });
  await page.waitForTimeout(400);
}

async function noException(page) {
  const n = await page.locator('[data-testid="stException"]').count();
  if (n) {
    const msg = (await page.locator('[data-testid="stException"]').first().innerText()).slice(0, 200).replace(/\n/g, " ");
    throw new BeatError(`st.exception on page: ${msg}`);
  }
}

// Note: after a step completes the app redraws the nav with a `-r` key suffix, so match by prefix/contains.
// Sidebar link for a journey page id (p2_textgps, ...) or "home" / "learn".
const navLink = (page, id) => {
  const top = id === "home" || id === "learn";
  const cls = top ? `[class*="st-key-tala-nav-top-${id}"]` : `[class*="st-key-tala-nav-"][class*="-${id}"]`;
  return page.locator(`section[data-testid="stSidebar"] ${cls} a`).first();
};

let mouse = { x: 640, y: 360 };
async function glide(page, x, y, steps = 28) {
  await page.mouse.move(x, y, { steps });
  mouse = { x, y };
}
async function glideTo(page, loc, dx = 0.5, dy = 0.5) {
  await loc.scrollIntoViewIfNeeded({ timeout: 15000 });
  const b = await loc.boundingBox();
  if (!b) throw new BeatError("target has no bounding box");
  await glide(page, b.x + b.width * dx, b.y + b.height * dy);
}
async function glideClick(page, loc) {
  await glideTo(page, loc);
  await sleep(page, 350);
  await loc.click();
}
async function must(page, selector, what) {
  try {
    await page.waitForSelector(selector, { state: "visible", timeout: TIMEOUT });
  } catch {
    throw new BeatError(`required selector not found: ${what || selector}`);
  }
}
async function goTo(page, id) {
  const link = navLink(page, id);
  try { await link.waitFor({ state: "visible", timeout: 30000 }); }
  catch { throw new BeatError(`sidebar link for ${id} not found`); }
  await glideClick(page, link);
  await settle(page);
}

// Smoothly scroll the first match to the middle of the main pane (maps sit below the fold at 720p).
async function centre(page, selector) {
  await page.evaluate((sel) => {
    const el = document.querySelector(`[data-testid="stMain"] ${sel}`);
    if (el) el.scrollIntoView({ block: "center", behavior: "smooth" });
  }, selector);
  await page.waitForTimeout(1100);
}

const MAP = '[data-testid="stDeckGlJsonChart"] canvas';

async function showMap(page, what) {
  await must(page, MAP, what);
  await centre(page, '[data-testid="stDeckGlJsonChart"]');
}

// ---- the storyboard -------------------------------------------------------------------------------------------
// Each beat: name, run(page, ctx). The caption for beat n is shown before its first action. `ctx.shot` is a
// no-op unless SHOTS=1.
const BEATS = [
  ["1 hero", async (page, c) => {
    await must(page, ".st-key-tala-hero", "Home hero (.st-key-tala-hero)");
    await glide(page, 640, 220, 20);
    await c.shot();
    await sleep(page, 4500);
  }],
  ["2 text vs gps", async (page, c) => {
    const card = page.locator(".st-key-tala-card-where a").first();
    await must(page, ".st-key-tala-card-where a", "chapter card link (.st-key-tala-card-where)");
    await glideClick(page, card);                 // lands on step 1, Data
    await settle(page);
    await goTo(page, "p2_textgps");
    await showMap(page, "Text vs GPS map canvas");
    await sleep(page, 1500);
    await glide(page, 640, 400, 30);              // hover the map: lines of disagreement
    await glide(page, 820, 470, 30);
    await c.shot();
    await sleep(page, 3000);
  }],
  ["3 repaired", async (page, c) => {
    const radio = '.st-key-p2_mode label:not([data-testid="stWidgetLabel"])';
    await must(page, radio, "location source radio (.st-key-p2_mode)");
    const labels = page.locator(radio);
    // Repaired is the default (first); show the contrast with GPS-only, then come back to Repaired.
    await glideClick(page, labels.nth(1));
    await settle(page);
    await showMap(page, "map after switching to GPS only");
    await sleep(page, 1800);
    await glideClick(page, labels.nth(0));
    await settle(page);
    await showMap(page, "map after switching to Repaired");
    await c.shot();
    await sleep(page, 3000);
  }],
  ["4 places region", async (page, c) => {
    await goTo(page, "p3_places");
    await must(page, '.st-key-p3_unit label:not([data-testid="stWidgetLabel"])', "unit radio (.st-key-p3_unit)");
    await glideClick(page, page.locator('.st-key-p3_unit label:not([data-testid="stWidgetLabel"])').first());   // Region
    await settle(page);
    await must(page, `${MAP}, .js-plotly-plot`, "places chart or map");
    await c.shot();
    await sleep(page, 4500);
  }],
  ["5 sets a place apart", async (page, c) => {
    await goTo(page, "p4_apart");
    await must(page, ".st-key-p4_a input", "place A select (.st-key-p4_a)");
    await glideClick(page, page.locator(".st-key-p4_a input").first());
    await page.keyboard.press("Control+A");
    await page.keyboard.type("Davao", { delay: 120 });
    await sleep(page, 700);
    const opt = page.locator('[role="option"]').first();
    if (await opt.count()) { await glideClick(page, opt); } else { await page.keyboard.press("Escape"); }
    await settle(page);
    await must(page, ".js-plotly-plot", "contrastive keywords chart");
    await centre(page, ".js-plotly-plot");
    await glide(page, 760, 520, 25);
    await c.shot();
    await sleep(page, 4000);
  }],
  ["6 feel bubble map", async (page, c) => {
    await goTo(page, "p5_feel");
    await showMap(page, "sentiment bubble map");
    await sleep(page, 1200);
    await glide(page, 600, 380, 30);
    await glide(page, 760, 440, 30);
    await c.shot();
    await sleep(page, 4500);
  }],
  ["7 hotspots", async (page, c) => {
    await goTo(page, "p8_hotspots");
    await showMap(page, "hotspot grid map");
    await sleep(page, 1200);
    await glide(page, 640, 420, 30);
    await c.shot();
    await sleep(page, 5500);
  }],
  ["8 stars and report", async (page, c) => {
    // Hover the sidebar stars top to bottom, then open the report and scroll through its cards.
    for (const id of ["p1_data", "p2_textgps", "p3_places", "p4_apart", "p5_feel", "p6_aspects", "p7_themes", "p8_hotspots"]) {
      const l = navLink(page, id);
      if (await l.count()) { await glideTo(page, l); await sleep(page, 250); }
    }
    await c.shot();
    await goTo(page, "p9_report");
    await showMap(page, "report generalized map");
    await must(page, ".st-key-p9_top", "report cards (cards-per-place slider .st-key-p9_top)");   // cards sit right below it
    await centre(page, ".st-key-p9_top");
    await glide(page, 780, 420, 20);
    for (let i = 0; i < 3; i++) { await page.mouse.wheel(0, 320); await sleep(page, 900); }
    await c.shot();
    await sleep(page, 1500);
  }],
  ["9 learn then home", async (page, c) => {
    const main = '[data-testid="stMain"]';
    await page.evaluate(() => { const m = document.querySelector('[data-testid="stMain"]'); if (m) m.scrollTo({ top: 0, behavior: "smooth" }); });
    await sleep(page, 900);
    const sum = page.locator(`${main} [data-testid="stExpander"] summary`).first();
    await must(page, `${main} [data-testid="stExpander"] summary`, "Learn expander");
    await glideClick(page, sum);
    await sleep(page, 2600);
    await c.shot();
    await glideClick(page, sum);                  // close again
    await sleep(page, 600);
    await goTo(page, "home");
    await must(page, ".st-key-tala-hero", "Home hero at the end");
    await sleep(page, 2500);
  }],
];

// ---- one language -----------------------------------------------------------------------------------------
async function recordOnce(lang, size) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), `tala_rec_${lang}_`));
  const browser = await chromium.launch({ headless: true, args: ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"] });
  const ctx = await browser.newContext({
    viewport: size, recordVideo: { dir: tmp, size }, storageState: { cookies: [], origins: [] },
  });
  await ctx.addInitScript(INIT_SCRIPT);
  const page = await ctx.newPage();
  const t0 = Date.now();
  let failure = null;
  mouse = { x: size.width / 2, y: size.height / 2 };
  try {
    // Language gate
    await page.goto(BASE + "/", { waitUntil: "domcontentloaded" });
    await must(page, ".tala-prompt", "language gate (.tala-prompt)");
    await sleep(page, 800);
    await glideClick(page, page.getByRole("button", { name: ENDONYM[lang], exact: true }).first());
    await page.waitForFunction(() => {
      const b = [...document.querySelectorAll("button")].find((x) => x.textContent.includes("\u25b8"));
      return b && !b.disabled;
    }, null, { timeout: 15000 });
    await sleep(page, 500);
    await glideClick(page, page.getByRole("button", { name: /\u25b8/ }).last());
    // Splash: START, then the meteor plays (kept in the video).
    await must(page, "#tala-start", "splash START button");
    await sleep(page, 600);
    await glideClick(page, page.locator("#tala-start"));
    await page.waitForFunction(() => document.body.classList.contains("tala-boot-complete"), null, { timeout: 20000 })
      .catch(() => { throw new BeatError("splash never completed (tala-boot-complete)"); });
    await settle(page);

    let n = 0;
    for (const [name, run] of BEATS) {
      n += 1;
      const num = n;
      console.log(`  [${lang}] beat ${name}  (${((Date.now() - t0) / 1000).toFixed(0)}s)`);
      const text = captionFor(lang, num);
      try {
        await page.evaluate((t) => window.__talaCaption && window.__talaCaption(t), text);
        await sleep(page, 700);
        await run(page, {
          shot: async () => {
            if (!SHOTS) return;
            const f = path.join(os.tmpdir(), `tala_tour_beat_${num}.png`);
            await page.screenshot({ path: f });
            console.log(`    shot ${f}`);
          },
        });
        await noException(page);
      } catch (e) {
        throw new BeatError(`beat "${name}": ${e.message.split("\n")[0]}`);
      }
    }
  } catch (e) {
    failure = e;
    const f = path.join(os.tmpdir(), `tala_tour_fail_${lang}.png`);
    await page.screenshot({ path: f }).then(() => console.error(`  failure screenshot: ${f}`)).catch(() => {});
  }
  const video = page.video();
  await page.close().catch(() => {});
  await ctx.close().catch(() => {});
  await browser.close().catch(() => {});
  if (failure) throw failure;
  return { file: await video.path(), seconds: (Date.now() - t0) / 1000 };
}

async function recordLang(lang) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  let size = { width: 1280, height: 720 };
  let res = await recordOnce(lang, size);
  let bytes = fs.statSync(res.file).size;
  let note = "";
  if (bytes > BUDGET && process.env.NO_DOWNSIZE !== "1") {
    // Playwright encodes VP8 at a roughly fixed bitrate (~1 Mbps), so a smaller frame often saves little; keep
    // whichever recording is smaller and say so. Set NO_DOWNSIZE=1 to skip this second pass.
    console.log(`  [${lang}] ${(bytes / 1048576).toFixed(2)} MB is over the 4 MB budget; re-recording at 1024x576`);
    const small = await recordOnce(lang, { width: 1024, height: 576 });
    const sb = fs.statSync(small.file).size;
    note = ` (1024x576 pass: ${(sb / 1048576).toFixed(2)} MB)`;
    if (sb < bytes) { res = small; bytes = sb; size = { width: 1024, height: 576 }; note += " used"; }
    else note += " not smaller, kept 1280x720";
  }
  const dest = path.join(OUT_DIR, `tour_${lang}.webm`);
  fs.copyFileSync(res.file, dest);
  try { fs.rmSync(path.dirname(res.file), { recursive: true, force: true }); } catch {}
  const mb = (bytes / 1048576).toFixed(2);
  console.log(`OK ${lang}: ${dest}  ${mb} MB, ~${res.seconds.toFixed(0)} s wall-clock${note}` +
    (bytes > BUDGET ? "  WARNING: still over the 4 MB budget" : ""));
  return bytes <= BUDGET;
}

(async () => {
  const arg = (process.argv[2] || "en").toLowerCase();
  const langs = arg === "all" ? LANGS : [arg];
  if (!langs.every((l) => LANGS.includes(l))) {
    console.error(`Unknown language "${arg}". Use one of ${LANGS.join(", ")}, all.`);
    process.exit(2);
  }
  let overBudget = false;
  for (const lang of langs) {
    try {
      if (!(await recordLang(lang))) overBudget = true;
    } catch (e) {
      console.error(`FAIL ${lang}: ${e.message}`);
      process.exit(1);
    }
  }
  process.exit(overBudget ? 3 : 0);
})();
