// End-to-end smoke test for TALA. Start the app first:
//   .venv/Scripts/streamlit run app.py --server.headless true --server.port 8599
// Run:  node tools/smoke_e2e.cjs      (BASE_URL / PLAYWRIGHT_PATH override the defaults)
const PW = process.env.PLAYWRIGHT_PATH || "C:/Users/mjmag/Desktop/ARAW/app/node_modules/playwright";
const { chromium } = require(PW);

const BASE = process.env.BASE_URL || "http://localhost:8599";
const PAGES = [
  "", "learn", "p1_data", "p2_textgps", "p3_places", "p4_apart", "p5_feel",
  "p6_aspects", "p7_themes", "p8_hotspots", "p9_report",
];
// Known-benign console noise (not app bugs).
const IGNORE = [/favicon/i, /Failed to load resource.*(404|net::ERR_ABORTED)/i, /\[vite\]/i];

const rows = [];
const record = (name, ok, detail = "") => {
  rows.push({ name, ok, detail });
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}${detail ? "  -- " + detail : ""}`);
};

// Streamlit shows a status widget (and data-test-script-state) while a script runs.
async function settle(page, timeout = 90000) {
  await page.waitForTimeout(600);
  await page.waitForFunction(() => {
    const app = document.querySelector('[data-testid="stApp"]');
    const running = app && app.getAttribute("data-test-script-state") === "running";
    return app && !running && !document.querySelector('[data-testid="stStatusWidget"]');
  }, null, { timeout });
  await page.waitForTimeout(500);
}

function watch(page, bucket) {
  page.on("console", (m) => {
    if (m.type() !== "error") return;
    const t = m.text();
    if (!IGNORE.some((r) => r.test(t))) bucket.push(t.slice(0, 200));
  });
  page.on("pageerror", (e) => bucket.push("pageerror: " + String(e.message).slice(0, 200)));
}

(async () => {
  const browser = await chromium.launch({ headless: true, args: ["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"] });
  const ctx = await browser.newContext({ viewport: { width: 1360, height: 900 } });
  const page = await ctx.newPage();
  const errors = [];
  watch(page, errors);

  // 1. Language gate
  try {
    await page.goto(BASE + "/", { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".tala-prompt", { timeout: 60000 });
    const before = (await page.textContent(".tala-prompt")).trim();
    await page.getByRole("button", { name: "Filipino" }).first().click();
    await page.waitForFunction((b) => {
      const el = document.querySelector(".tala-prompt");
      return el && el.textContent.trim() !== b;
    }, before, { timeout: 30000 });
    const after = (await page.textContent(".tala-prompt")).trim();
    record("1a gate: tap Filipino changes prompt", after !== before, `"${before}" -> "${after}"`);
    const cont = page.getByRole("button", { name: /▸/ }).last();
    await page.waitForFunction(() => {
      const b = [...document.querySelectorAll("button")].find((x) => x.textContent.includes("▸"));
      return b && !b.disabled;
    }, null, { timeout: 15000 });
    await cont.click();
    record("1b gate: Continue pressed", true);
  } catch (e) { record("1 gate", false, e.message.split("\n")[0]); }

  // 2. Splash START
  try {
    await page.waitForSelector("#tala-start", { state: "visible", timeout: 90000 });
    await page.click("#tala-start");
    await page.waitForFunction(() => document.body.classList.contains("tala-boot-complete"), null, { timeout: 15000 });
    await page.waitForTimeout(1500);
    const splashGone = await page.evaluate(() => {
      const s = document.querySelector(".tala-splash");
      if (!s) return true;
      const cs = getComputedStyle(s);
      return cs.display === "none" || cs.visibility === "hidden" || parseFloat(cs.opacity) === 0 || cs.pointerEvents === "none";
    });
    record("2a splash: START dismisses overlay", splashGone);
    await settle(page);
    record("2b sidebar visible", await page.locator('section[data-testid="stSidebar"]').isVisible());
  } catch (e) { record("2 splash", false, e.message.split("\n")[0]); }
  await page.waitForTimeout(1500); // let the prefs cookie write
  const state = await ctx.storageState();
  const cookieNames = state.cookies.map((c) => c.name);
  record("2c cookies saved (tala_booted, tala_prefs)", cookieNames.includes("tala_booted") && cookieNames.includes("tala_prefs"), cookieNames.join(","));

  // 3. Home, How TALA works and the nine journey pages
  for (const p of PAGES) {
    const label = "3 page /" + p;
    const n0 = errors.length;
    try {
      await page.goto(`${BASE}/${p}`, { waitUntil: "domcontentloaded" });
      await page.waitForSelector('[data-testid="stApp"]', { timeout: 60000 });
      await settle(page, 120000);
      const exc = await page.locator('[data-testid="stException"]').count();
      const newErr = errors.slice(n0);
      const gate = await page.locator(".tala-prompt").count();
      record(label, exc === 0 && newErr.length === 0 && gate === 0,
        exc ? `${exc} exception(s): ${(await page.locator('[data-testid="stException"]').first().innerText()).slice(0, 160).replace(/\n/g, " ")}` :
        newErr.length ? "console: " + newErr[0] : gate ? "gate shown" : "");
    } catch (e) { record(label, false, e.message.split("\n")[0]); }
  }

  await page.close(); await ctx.close();

  // 4. Fresh context with saved cookies, straight to p9_report
  const ctx2 = await browser.newContext({ viewport: { width: 1360, height: 900 }, storageState: state });
  const p2 = await ctx2.newPage();
  const errors2 = []; watch(p2, errors2);
  try {
    await p2.goto(`${BASE}/p9_report`, { waitUntil: "domcontentloaded" });
    await p2.waitForSelector('[data-testid="stApp"]', { timeout: 60000 });
    await settle(p2, 120000);
    const gate = await p2.locator(".tala-prompt").count();
    const splash = await p2.locator(".tala-splash").count();
    record("4a resume: no gate, no splash", gate === 0 && splash === 0, `gate=${gate} splash=${splash}`);
    const deck = await p2.locator('[data-testid="stDeckGlJsonChart"]').count();
    const exc = await p2.locator('[data-testid="stException"]').count();
    await p2.waitForTimeout(1500);
    const canvas = await p2.locator('[data-testid="stDeckGlJsonChart"] canvas').count();
    record("4b resume: map renders (auto-run)", deck > 0 && canvas > 0 && exc === 0, `deck=${deck} canvas=${canvas} exc=${exc}`);
    const lang = await p2.evaluate(() => document.documentElement.lang);
    var urlBefore = p2.url();
    var sideBefore = (await p2.locator('section[data-testid="stSidebar"]').innerText()).slice(0, 400);

    // 5. Reload keeps page + language
    await p2.reload({ waitUntil: "domcontentloaded" });
    await p2.waitForSelector('[data-testid="stApp"]', { timeout: 60000 });
    await settle(p2, 120000);
    const sideAfter = (await p2.locator('section[data-testid="stSidebar"]').innerText()).slice(0, 400);
    const gate2 = await p2.locator(".tala-prompt").count();
    record("5 reload: same page and language", p2.url() === urlBefore && sideAfter === sideBefore && gate2 === 0, p2.url());
    record("4/5 no console errors on resume", errors2.length === 0, errors2[0] || "");
  } catch (e) { record("4/5 resume", false, e.message.split("\n")[0]); }

  await browser.close();
  const failed = rows.filter((r) => !r.ok).length;
  console.log(`\n${rows.length - failed}/${rows.length} passed`);
  process.exit(failed ? 1 : 0);
})();
