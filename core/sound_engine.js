/* TALA sound engine: a synth built on the Web Audio API, no audio files.
 *
 * Source of truth: docs/sound/soundboard.html. The ENGINE, instruments, sounds (S) and MUSIC
 * sections below are copied from the approved board verbatim; only the board UI is dropped and
 * `ensure()` reuses one AudioContext across re-injections. To change a sound, prototype it on
 * the board first, then copy it here (see docs/AUDIO.md).
 *
 * The file is injected once per session by core/audio.py as a base64 bootstrap (no eval, CSP-safe).
 * It installs `window.__talaSound`; injecting it again replaces the old instance and carries the
 * unlocked AudioContext, the preferences and the current area over.
 */
(() => {
'use strict';
const prev = window.__talaSound;
if (prev && prev._dispose) prev._dispose();

/* ============================== ENGINE ============================== */
const FR = 1 / 60; // envelopes move in 60 Hz frames, like the old consoles
let ctx = null, master, sfxBus, musicBus, sfxSend, musicSend, echoWet, analyser, W = {}, NB = {};
const vol = { master: 0.8, sfx: 0.9, music: 0.6, echo: 0.55 };
const live = new Set();
const timers = new Set();

function later(fn, ms) { const id = setTimeout(() => { timers.delete(id); fn(); }, ms); timers.add(id); return id; }

function pulseWave(c, duty) {
  const n = 64, re = new Float32Array(n), im = new Float32Array(n);
  for (let k = 1; k < n; k++) { re[k] = Math.sin(2 * Math.PI * k * duty) / (k * Math.PI); im[k] = (1 - Math.cos(2 * Math.PI * k * duty)) / (k * Math.PI); }
  return c.createPeriodicWave(re, im);
}
function lfsrBuffer(c, short, len) { // console-style noise: a 15-bit linear feedback shift register
  const buf = c.createBuffer(1, len, c.sampleRate), d = buf.getChannelData(0);
  let r = 1;
  for (let i = 0; i < len; i++) { const b = (r ^ (r >> (short ? 6 : 1))) & 1; r = (r >> 1) | (b << 14); d[i] = (r & 1) ? 0.7 : -0.7; }
  return buf;
}
function ensure() {
  if (ctx) { if (ctx.state === 'suspended') ctx.resume(); return ctx; }
  const AC = window.AudioContext || window.webkitAudioContext;
  ctx = window.__talaCtx || (window.__talaCtx = new AC());
  const comp = ctx.createDynamicsCompressor();
  comp.threshold.value = -15; comp.knee.value = 8; comp.ratio.value = 4; comp.attack.value = 0.003; comp.release.value = 0.15;
  const soften = ctx.createBiquadFilter(); soften.type = 'lowpass'; soften.frequency.value = 7200; // a touch darker than daytime: night air
  master = ctx.createGain(); sfxBus = ctx.createGain(); musicBus = ctx.createGain();
  analyser = ctx.createAnalyser(); analyser.fftSize = 1024;
  // Starlight echo: a dark feedback delay that voices send into. It is what makes TALA sound like night
  // rather than daylight, and each send is scaled by its bus volume so muting a bus also mutes its echo.
  const delay = ctx.createDelay(1); delay.delayTime.value = 0.28;
  const feedback = ctx.createGain(); feedback.gain.value = 0.36;
  const damp = ctx.createBiquadFilter(); damp.type = 'lowpass'; damp.frequency.value = 2600;
  echoWet = ctx.createGain(); sfxSend = ctx.createGain(); musicSend = ctx.createGain();
  sfxSend.connect(delay); musicSend.connect(delay);
  delay.connect(damp); damp.connect(feedback); feedback.connect(delay); damp.connect(echoWet); echoWet.connect(master);
  sfxBus.connect(master); musicBus.connect(master);
  master.connect(soften); soften.connect(comp); comp.connect(analyser); analyser.connect(ctx.destination);
  applyVolumes();
  W = { p12: pulseWave(ctx, 0.125), p25: pulseWave(ctx, 0.25), p50: pulseWave(ctx, 0.5) };
  NB = { long: lfsrBuffer(ctx, false, 32767), short: lfsrBuffer(ctx, true, 93 * 31 * 4) };
  return ctx;
}
function applyVolumes() {
  if (!ctx) return;
  const t = ctx.currentTime;
  master.gain.setTargetAtTime(vol.master ** 1.6, t, 0.02);
  sfxBus.gain.setTargetAtTime(vol.sfx ** 1.6, t, 0.02);
  musicBus.gain.setTargetAtTime(vol.music ** 1.6, t, 0.02);
  sfxSend.gain.setTargetAtTime(vol.sfx ** 1.6, t, 0.02);
  musicSend.gain.setTargetAtTime(vol.music ** 1.6, t, 0.02);
  echoWet.gain.setTargetAtTime(vol.echo, t, 0.02);
}
function track(node, bus) { const e = { node, bus }; live.add(e); node.onended = () => live.delete(e); }

function envelope(g, t0, d, v, a, shape) {
  const n = Math.max(2, Math.ceil(d / FR));
  g.gain.setValueAtTime(0, t0);
  for (let k = 1; k <= n; k++) {
    const tt = Math.min(d, k * FR);
    let lvl;
    if (a && tt <= a) lvl = tt / a;
    else {
      const p = (tt - (a || 0)) / Math.max(0.001, d - (a || 0));
      lvl = shape === 'flat' ? 1
        : shape === 'pluck' ? (1 - p) ** 2
        : shape === 'swell' ? Math.sin(Math.PI * p)
        : shape === 'lead' ? (p < 0.12 ? 1 - 2.5 * p : p < 0.85 ? 0.7 : 0.7 * (1 - p) / 0.15)
        : 1 - 0.8 * p; // 'decay'
    }
    lvl = Math.round(Math.max(0, Math.min(1, lvl)) * 15) / 15; // 16 volume steps, 4-bit
    g.gain.linearRampToValueAtTime(lvl * v, t0 + tt);
  }
  g.gain.linearRampToValueAtTime(0, t0 + d + 0.012);
}

function startTime(o) { return o.at != null ? o.at : ctx.currentTime + 0.012 + (o.t || 0); }
function sendEcho(c, g, amount, bus) {
  if (!amount) return;
  const s = c.createGain(); s.gain.value = amount;
  g.connect(s); s.connect(bus === musicBus ? musicSend : sfxSend);
}

function tone(o) {
  const c = ensure(), t0 = startTime(o), d = o.d || 0.1, f = o.f, f2 = o.f2 ?? f, bus = o.bus || sfxBus;
  const osc = c.createOscillator();
  if (o.wave === 'tri') osc.type = 'triangle'; else if (o.wave === 'sine') osc.type = 'sine'; else osc.setPeriodicWave(W[o.wave || 'p50']);
  const fq = osc.frequency;
  if (o.arp) {
    const r = o.arpRate || 1 / 30; let i = 0;
    for (let tt = 0; tt < d; tt += r, i++) fq.setValueAtTime(f * 2 ** (o.arp[i % o.arp.length] / 12), t0 + tt);
  } else if (f2 !== f) {
    if (o.step) { const n = Math.max(1, Math.round(d / FR)); for (let k = 0; k <= n; k++) fq.setValueAtTime(f * (f2 / f) ** (k / n), t0 + (k * d) / n); }
    else { fq.setValueAtTime(f, t0); fq.exponentialRampToValueAtTime(f2, t0 + d); }
  } else fq.setValueAtTime(f, t0);
  if (o.vib) {
    const lfo = c.createOscillator(), lg = c.createGain();
    lfo.frequency.value = o.vib[0]; lg.gain.setValueAtTime(0, t0); lg.gain.setValueAtTime(f * o.vib[1], t0 + (o.vibDelay || 0));
    lfo.connect(lg); lg.connect(fq); lfo.start(t0); lfo.stop(t0 + d + 0.05); track(lfo, bus);
  }
  const g = c.createGain();
  envelope(g, t0, d, o.v ?? 0.15, o.a || 0, o.env || 'decay');
  osc.connect(g); g.connect(bus); sendEcho(c, g, o.echo, bus);
  osc.start(t0); osc.stop(t0 + d + 0.03); track(osc, bus);
}

function noise(o) {
  const c = ensure(), t0 = startTime(o), d = o.d || 0.1, bus = o.bus || sfxBus;
  const src = c.createBufferSource(); src.buffer = o.mode === 'short' ? NB.short : NB.long; src.loop = true;
  const r = o.rate ?? 1, r2 = o.rate2 ?? r;
  src.playbackRate.setValueAtTime(r, t0); if (r2 !== r) src.playbackRate.exponentialRampToValueAtTime(r2, t0 + d);
  let last = src;
  if (o.filter) {
    const [type, fa, fb, q] = o.filter, bq = c.createBiquadFilter();
    bq.type = type; bq.frequency.setValueAtTime(fa, t0); if (fb) bq.frequency.exponentialRampToValueAtTime(fb, t0 + d); bq.Q.value = q ?? 0.8;
    src.connect(bq); last = bq;
  }
  const g = c.createGain(); envelope(g, t0, d, o.v ?? 0.15, o.a || 0, o.env || 'decay');
  last.connect(g); g.connect(bus); sendEcho(c, g, o.echo, bus);
  src.start(t0, o.mode === 'short' ? 0 : Math.random() * 0.5); src.stop(t0 + d + 0.03); track(src, bus);
}

const SEMI = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
function N(s) {
  const m = /^([A-G])([#b]?)(-?\d)$/.exec(s); if (!m) throw new Error('Bad note ' + s);
  const midi = 12 * (+m[3] + 1) + SEMI[m[1]] + (m[2] === '#' ? 1 : m[2] === 'b' ? -1 : 0);
  return 440 * 2 ** ((midi - 69) / 12);
}
const up = (f, semis) => f * 2 ** (semis / 12);

/* mel('p25', 'A5 C6 . E6*2 A5+C6+E6*4', {u: .08}) : one token per unit, '.' rest, '*n' longer, '+' chord */
function mel(wave, str, o = {}) {
  const u = o.u || 0.08; let t = o.t || 0;
  for (const tok of str.trim().split(/\s+/)) {
    const [body, mul] = tok.split('*'), len = u * (mul ? +mul : 1);
    if (body !== '.') for (const nn of body.split('+')) tone({ ...o, wave, f: up(N(nn), o.tr || 0), t, d: len * (o.legato ?? 0.92) });
    t += len;
  }
  return t;
}

/* TALA's instruments. The star bell is TALA's signature: a triangle with a glassy partial a twelfth up (3x),
   always sent into the starlight echo. (ARAW's kulintang gong uses a 2.76x partial and no echo.) */
function bell(f, o = {}) {
  const v = o.v ?? 0.25, d = o.d ?? 0.6, echo = o.echo ?? 0.35;
  tone({ ...o, wave: 'tri', f, d, v, env: 'pluck', echo });
  tone({ ...o, wave: 'sine', f: f * 3, d: Math.min(d, 0.25), v: v * 0.22, env: 'pluck', echo });
  tone({ ...o, wave: 'p12', f: f * 2, d: 0.03, v: v * 0.12, env: 'pluck' });
}
function kick(o = {}) { const v = o.v ?? 0.35; tone({ ...o, wave: 'tri', f: 120, f2: 42, d: 0.12, v, env: 'pluck' }); noise({ ...o, rate: 0.2, d: 0.02, v: v * 0.2 }); }
function hat(o = {}) { noise({ ...o, rate: 1, d: 0.02, v: o.v ?? 0.035, filter: ['highpass', 7500] }); }
function brush(o = {}) { noise({ ...o, rate: 0.5, d: 0.09, v: o.v ?? 0.06, env: 'swell', filter: ['bandpass', 3000, null, 0.9] }); }
function crash(o = {}) { noise({ ...o, rate: 0.8, d: 0.7, v: o.v ?? 0.06, filter: ['highpass', 3500], echo: 0.3 }); }
function chirp(o = {}) { // kuliglig: a cricket's three quick pulses near 4.3 kHz
  const base = o.at != null ? null : (o.t || 0);
  for (let i = 0; i < 3; i++) {
    const oo = { ...o, wave: 'p12', f: 4300, d: 0.016, v: o.v ?? 0.025, env: 'pluck', echo: 0.2 };
    if (o.at != null) oo.at = o.at + i * 0.032; else oo.t = base + i * 0.032;
    tone(oo);
  }
}
const TWINKLE = ['A5', 'C6', 'D6', 'E6', 'G6', 'A6', 'C7', 'D7', 'E7']; // A minor pentatonic, up high
function twinkleNote(o = {}) { bell(N(TWINKLE[Math.floor(Math.random() * TWINKLE.length)]), { ...o, d: 0.4, v: o.v ?? 0.08, echo: 0.5 }); }

/* ============================== SOUNDS ============================== */
const S = {
  // interface
  click() { tone({ wave: 'tri', f: N('A6'), d: 0.03, v: 0.2, env: 'pluck' }); tone({ wave: 'p12', f: N('E7'), d: 0.02, v: 0.05, env: 'pluck' }); },
  select() { tone({ wave: 'p25', f: N('E6'), d: 0.035, v: 0.12, env: 'pluck' }); tone({ wave: 'tri', f: N('A6'), t: 0.04, d: 0.07, v: 0.22, env: 'pluck', echo: 0.15 }); },
  toggleOn() { mel('tri', 'A5 C6 E6', { u: 0.035, v: 0.2, env: 'pluck' }); },
  toggleOff() { mel('tri', 'E6 C6 A5', { u: 0.035, v: 0.2, env: 'pluck' }); },
  nav() { noise({ rate: 0.5, rate2: 0.25, d: 0.16, v: 0.08, env: 'swell', filter: ['bandpass', 1800, 700, 0.9] }); bell(N('E6'), { t: 0.06, d: 0.3, v: 0.14, echo: 0.3 }); },
  learnOpen() { tone({ wave: 'p12', f: N('A5'), arp: [0, 3, 7, 12], arpRate: 1 / 40, d: 0.12, v: 0.09, echo: 0.25 }); },
  learnClose() { tone({ wave: 'p12', f: N('A5'), arp: [12, 7, 3, 0], arpRate: 1 / 40, d: 0.12, v: 0.09, echo: 0.2 }); },
  slider() { noise({ mode: 'short', rate: 1.4, d: 0.018, v: 0.1, filter: ['highpass', 2500] }); tone({ wave: 'tri', f: N('D6'), d: 0.03, v: 0.14, env: 'pluck' }); },
  copy() { [0, 0.06].forEach((t) => tone({ wave: 'p25', f: N('B6'), t, d: 0.025, v: 0.07, env: 'pluck' })); },
  upload() {
    mel('p12', 'E5 A5 C6 E6', { u: 0.045, v: 0.08, env: 'flat', legato: 0.7 });
    noise({ mode: 'short', rate: 0.8, d: 0.03, v: 0.08, t: 0.2 });
    bell(N('A6'), { t: 0.22, d: 0.3, v: 0.12, echo: 0.3 });
  },
  download() {
    tone({ wave: 'tri', f: N('E6'), f2: N('A4'), step: true, d: 0.16, v: 0.2 });
    tone({ wave: 'p12', f: N('E6'), f2: N('A4'), step: true, d: 0.14, v: 0.04 });
    S.thud(0.45, 0.17);
  },
  thud(k = 1, t = 0) { noise({ rate: 0.2, d: 0.05, v: 0.25 * k, t, filter: ['lowpass', 1800] }); tone({ wave: 'tri', f: 140, f2: 50, t, d: 0.11, v: 0.45 * k, env: 'pluck' }); },
  locked() { tone({ wave: 'tri', f: N('E4'), d: 0.12, v: 0.24, env: 'pluck', echo: 0.3 }); tone({ wave: 'tri', f: N('B3'), t: 0.16, d: 0.2, v: 0.22, env: 'pluck', echo: 0.3 }); },

  // analysis
  run() {
    noise({ rate: 0.15, rate2: 0.6, d: 0.4, v: 0.06, env: 'swell', filter: ['bandpass', 400, 2000, 1.4] });
    tone({ wave: 'p12', f: 220, f2: 880, step: true, d: 0.36, v: 0.05, env: 'swell' });
  },
  ready() { bell(N('A5'), { v: 0.3 }); bell(N('E6'), { t: 0.08, v: 0.26 }); bell(N('B6'), { t: 0.16, v: 0.22, d: 0.7 }); },
  cached() { tone({ wave: 'tri', f: N('E6'), arp: [0, 7, 12, 19, 24], arpRate: 1 / 60, d: 0.09, v: 0.2, echo: 0.25 }); },
  step() { bell(N('E6'), { v: 0.3, d: 0.5 }); tone({ wave: 'p12', f: N('B6'), arp: [0, 5, 7, 12], arpRate: 1 / 45, t: 0.08, d: 0.18, v: 0.04, echo: 0.3 }); },
  progress(i = 1) { const sc = [0, 3, 5, 7, 10, 12, 15, 17]; tone({ wave: 'p25', f: up(N('A4'), sc[Math.min(Math.max(i, 1), 8) - 1]), d: 0.05, v: 0.08, env: 'pluck' }); },
  warn() { tone({ wave: 'p25', f: N('F5'), d: 0.09, v: 0.09, env: 'flat' }); tone({ wave: 'p25', f: N('D5'), t: 0.13, d: 0.16, v: 0.09, echo: 0.2 }); },
  error() {
    tone({ wave: 'tri', f: N('E4'), f2: N('C4'), d: 0.4, v: 0.26, vib: [6, 0.02], vibDelay: 0.1, echo: 0.2 });
    tone({ wave: 'p12', f: N('G4'), f2: N('Eb4'), d: 0.3, v: 0.035 });
  },

  // celebrations
  twinkle() { for (let i = 0; i < 7; i++) twinkleNote({ t: i * 0.2 + Math.random() * 0.08, v: 0.12 + Math.random() * 0.08 }); },
  language() { bell(N('E6'), { v: 0.26 }); bell(N('A6'), { t: 0.09, v: 0.24 }); mel('p25', 'A5+C6+E6*3', { t: 0.09, u: 0.07, v: 0.05, env: 'lead', echo: 0.25 }); },
  start() { // bulalakaw: a shooting star streaks down, then lands on an A minor bell chord
    tone({ wave: 'p12', f: 2600, f2: 700, step: true, d: 0.42, v: 0.07, env: 'decay', echo: 0.3 });
    noise({ rate: 1, rate2: 0.4, d: 0.45, v: 0.05, env: 'swell', filter: ['highpass', 5000, 2500] });
    const t = 0.42;
    bell(N('A5'), { t, v: 0.3, d: 0.8 }); bell(N('E6'), { t: t + 0.06, v: 0.26, d: 0.8 }); bell(N('C7'), { t: t + 0.12, v: 0.2, d: 0.9 });
    tone({ wave: 'tri', f: N('A3'), t, d: 0.7, v: 0.25 });
  },
  bootReady() { // the constellation forms: stars light one by one, then a held note
    'A5 C6 D6 E6 G6 A6'.split(' ').forEach((n, i) => bell(N(n), { t: i * 0.13, v: 0.2, d: 0.5 }));
    ['A4', 'C5', 'E5'].forEach((n) => tone({ wave: 'p12', f: N(n), d: 1.6, v: 0.03, env: 'swell' }));
    tone({ wave: 'tri', f: N('A2'), d: 1.4, v: 0.28, env: 'swell' });
    mel('p25', 'E6+A6*6', { t: 0.8, u: 0.1, v: 0.05, env: 'lead', vib: [5, 0.006], vibDelay: 0.2, echo: 0.3 });
  },
  trackDone() { // A minor climbs to C major: first light after a night of work
    const u = 0.085;
    mel('p25', 'A4 C5 E5 A5*2 G5 A5 C6*8', { u, v: 0.11, env: 'lead', vib: [6, 0.007], vibDelay: 0.15, echo: 0.25 });
    mel('p12', 'E4 A4 C5 E5*2 D5 E5 G5*8', { u, v: 0.05, env: 'lead' });
    mel('tri', 'A2*4 . F2 G2 C3*8', { u, v: 0.26 });
    kick({ t: 0 }); kick({ t: u * 4 }); kick({ t: u * 7 }); crash({ t: u * 7 });
    ['G6', 'C7', 'E7'].forEach((n, i) => bell(N(n), { t: u * 8 + i * 0.09, v: 0.13 }));
  },
  fullSky() { // both tracks done: a short harana phrase under a cascade of stars
    const u = 0.12;
    tone({ wave: 'p12', f: 2400, f2: 800, step: true, d: 0.35, v: 0.04, echo: 0.3 });
    mel('p25', 'E5 A5 B5 C6*3 B5 A5 G5*3 E5 G5 C6*9', { u, v: 0.1, env: 'lead', vib: [5.5, 0.008], vibDelay: 0.15, legato: 0.9, echo: 0.3 });
    mel('p12', 'C5+E5*6 A4+C5*6 E5+G5*10', { u, v: 0.03, env: 'swell' });
    mel('tri', 'A2*6 F2*6 C3*10', { u, v: 0.24 });
    crash({ t: u * 12 });
    'C6 D6 E6 G6 A6 C7 D7 E7'.split(' ').forEach((n, i) => bell(N(n), { t: u * 12 + i * 0.08, v: 0.14 }));
  },

  // page signatures: Text track
  text1() { // Data & cleaning: a scrub, then the clean token
    noise({ rate: 0.6, rate2: 1.2, d: 0.18, v: 0.08, env: 'swell', filter: ['bandpass', 2500, 5000, 1] });
    noise({ rate: 0.6, rate2: 1.2, d: 0.14, v: 0.06, t: 0.2, env: 'swell', filter: ['bandpass', 3000, 5500, 1] });
    tone({ wave: 'tri', f: N('E6'), t: 0.38, d: 0.1, v: 0.18, env: 'pluck', echo: 0.2 });
  },
  text2() { ['A5', 'E6', 'C6', 'G6', 'D6', 'A6'].forEach((n, i) => tone({ wave: 'p25', f: N(n), f2: N(n) * 1.5, t: i * 0.065, d: 0.04, v: 0.08, env: 'pluck', echo: 0.15 })); },
  text3() { // sentiment: a meter needle swings, then settles
    tone({ wave: 'tri', f: N('A4'), f2: N('E5'), d: 0.18, v: 0.2, env: 'flat' });
    tone({ wave: 'tri', f: N('E5'), f2: N('C5'), t: 0.18, d: 0.14, v: 0.2, env: 'flat' });
    tone({ wave: 'tri', f: N('C5'), t: 0.32, d: 0.2, v: 0.2, env: 'pluck', echo: 0.2 });
    noise({ mode: 'short', rate: 1.3, d: 0.015, v: 0.07, t: 0.32 });
  },
  text4() { [['C6', 'E6'], ['D6', 'G6'], ['E6', 'A6']].forEach(([a, b], i) => { const t = i * 0.16;
    tone({ wave: 'p25', f: N(a), t, d: 0.05, v: 0.09, env: 'pluck' }); tone({ wave: 'p25', f: N(b), t: t + 0.05, d: 0.07, v: 0.09, env: 'pluck', echo: 0.2 }); }); },
  text5() { ['A4', 'E5', 'C6', 'G6', 'D7'].forEach((n, i) => bell(N(n), { t: i * 0.1, v: 0.18, d: 0.5 })); tone({ wave: 'tri', f: N('A2'), d: 0.8, v: 0.2, env: 'swell' }); },
  text6() { noise({ rate: 0.35, rate2: 0.7, d: 0.22, v: 0.09, env: 'flat', filter: ['bandpass', 1400, 2600, 1.6] }); bell(N('A6'), { t: 0.24, v: 0.2 }); },
  text7() {
    [0, 2, 3, 5, 7].forEach((s, i) => { tone({ wave: 'p50', f: up(N('A5'), s), t: i * 0.07, d: 0.03, v: 0.07, env: 'flat' }); noise({ mode: 'short', rate: 1.5, d: 0.012, v: 0.05, t: i * 0.07 }); });
    tone({ wave: 'tri', f: N('E6'), t: 0.36, d: 0.12, v: 0.18, env: 'pluck', echo: 0.2 });
  },
  text8() { // themes: two voices converge on one centroid
    tone({ wave: 'tri', f: N('A4'), f2: N('A5'), step: true, d: 0.3, v: 0.2 });
    tone({ wave: 'p25', f: N('A6'), f2: N('A5'), step: true, d: 0.3, v: 0.06 });
    bell(N('A5'), { t: 0.32, v: 0.26 });
  },

  // page signatures: Geo track
  geo1() { // points land on the map
    [[0, 'E6'], [0.07, 'A6'], [0.11, 'C6'], [0.2, 'G6'], [0.24, 'D6'], [0.33, 'A5']].forEach(([t, n]) =>
      tone({ wave: 'tri', f: N(n), f2: N(n) * 0.7, t, d: 0.05, v: 0.16, env: 'pluck', echo: 0.15 }));
  },
  geo2() { // DBSCAN: dots connect into two constellations
    [['E6', 'G6', 'A6'], ['C6', 'D6', 'E6']].forEach((grp, j) => { const t0 = j * 0.42;
      grp.forEach((n, i) => tone({ wave: 'p12', f: N(n), t: t0 + i * 0.06, d: 0.04, v: 0.06, env: 'pluck' }));
      bell(N(grp[2]), { t: t0 + 0.2, v: 0.22, d: 0.5 }); });
    tone({ wave: 'tri', f: N('A3'), t: 0.2, d: 0.8, v: 0.2 });
  },
  geo3() { tone({ wave: 'p50', f: N('A4'), arp: [0, 0, 5, 5, 7, 7, 12, 12], arpRate: 1 / 30, d: 0.27, v: 0.06, env: 'flat' }); noise({ mode: 'short', rate: 1, d: 0.02, v: 0.08, t: 0.27 }); },
  geo4() { // clip to land, then the map is revealed
    [0, 0.12].forEach((t) => { noise({ mode: 'short', rate: 1.2, d: 0.025, v: 0.14, t, filter: ['highpass', 3000] }); tone({ wave: 'p25', f: N('E7'), t, d: 0.02, v: 0.05, env: 'pluck' }); });
    tone({ wave: 'p12', f: N('A4'), f2: N('A5'), t: 0.25, d: 0.5, v: 0.05, env: 'swell', echo: 0.3 });
    bell(N('E6'), { t: 0.7, v: 0.2 });
  },
  geo5() { // text meets location: chatter, then a pin
    [0, 0.09].forEach((t) => tone({ wave: 'p25', f: N('C6'), arp: [0, 4], arpRate: 1 / 30, t, d: 0.07, v: 0.07 }));
    tone({ wave: 'tri', f: N('E6'), f2: N('A5'), t: 0.22, d: 0.08, v: 0.2, env: 'pluck' });
    bell(N('A6'), { t: 0.3, v: 0.15 });
  },
};

/* ============================== MUSIC ============================== */
const bars = (...b) => b.join(' ');
const rep = (s, n) => Array(n).fill(s).join(' ');
const SONGS = {
  gabi: {
    name: 'Gabi', where: 'Language gate, boot splash and Home', bpm: 80, key: 'A minor', prog: 'Am – F – C – E', meter: '4/4',
    tracks: [
      { inst: 'bell', v: 0.16, echo: 0.4, pat: bars('E5 - - - A5 - B5 C6', 'A5 - - - - - G5 F5', 'E5 - - - G5 - C6 -', 'B5 - - - G#5 - - .', 'C6 - B5 A5 E5 - - A5', 'C6 - - - D6 - C6 A5', 'G5 - E5 - C5 - E5 G5', 'B4 - - - - - - .') },
      { wave: 'p12', v: 0.03, env: 'pluck', echo: 0.2, pat: rep(bars('A3 E4 A4 C5 E5 C5 A4 E4', 'F3 C4 F4 A4 C5 A4 F4 C4', 'C4 G4 C5 E5 G5 E5 C5 G4', 'E3 B3 E4 G#4 B4 G#4 E4 B3'), 2) },
      { wave: 'tri', v: 0.22, env: 'lead', pat: rep(bars('A2 - - - - - E2 -', 'F2 - - - - - C3 -', 'C3 - - - - - G2 -', 'E2 - - - - - B2 -'), 2) },
    ],
    drums: rep('. . . . t . . . . . r . . . . .', 4), voices: 'music box, crickets',
  },
  buwan: {
    name: 'Buwan', where: 'Text track pages, while reading and tuning', bpm: 92, key: 'D Dorian', prog: 'Dm – G – Dm – C', meter: '4/4',
    tracks: [
      { wave: 'tri', v: 0.2, env: 'lead', echo: 0.25, pat: bars('D5 - - - F5 - - -', 'E5 - D5 - B4 - - -', 'A4 - - - D5 - F5 -', 'E5 - - - C5 - - -', 'F5 - - - A5 - G5 -', 'B5 - - - G5 - - -', 'A5 - F5 - D5 - E5 -', 'C5 - - - - - - .') },
      { wave: 'p12', v: 0.028, env: 'pluck', pat: rep(bars(rep('D4 A4 F5 A4', 2), rep('G3 D4 B4 D4', 2), rep('D4 A4 F5 A4', 2), rep('C4 G4 E5 G4', 2)), 2) },
      { wave: 'tri', v: 0.2, env: 'lead', pat: rep(bars('D3 - - - - - - -', 'G2 - - - - - - -', 'D3 - - - - - - -', 'C3 - - - - - - -'), 2) },
    ],
    drums: null, voices: '3 voices, no drums',
  },
  bituin: {
    name: 'Bituin', where: 'Geo track pages: ingest, cluster, map', bpm: 108, key: 'E minor', prog: 'Em – C – G – D', meter: '4/4',
    tracks: [
      { wave: 'p25', v: 0.085, env: 'lead', vib: [5.5, 0.006], echo: 0.3, pat: bars('E5 - G5 - B5 - - A5', 'G5 - E5 - C5 - - -', 'D5 - G5 - B5 - D6 -', 'C6 - B5 - A5 - - -', 'E5 - G5 - B5 - E6 -', 'D6 - C6 - G5 - E5 -', 'D5 - G5 - B5 - A5 G5', 'F#5 - - - - - - .') },
      { wave: 'p12', v: 0.035, env: 'pluck', pat: rep(bars(rep('E4 G4 B4 G4', 2), rep('C4 E4 G4 E4', 2), rep('G3 B3 D4 B3', 2), rep('D4 F#4 A4 F#4', 2)), 2) },
      { wave: 'tri', v: 0.26, env: 'pluck', pat: rep(bars('E2 - E3 - E2 - E3 -', 'C2 - C3 - C2 - C3 -', 'G2 - G3 - G2 - G3 -', 'D2 - D3 - D2 - D3 -'), 2) },
    ],
    drums: bars(rep('k . h . b . h .', 7), 'k . h . b . t t'), voices: '4 voices, soft drums',
  },
  harana: {
    name: 'Harana', where: 'After you finish a track', bpm: 88, key: 'G minor → B♭ major', prog: 'Gm – Cm – D – Gm | B♭ – E♭ – F – B♭', meter: '3/4',
    tracks: [
      { wave: 'p25', v: 0.1, env: 'lead', vib: [5.5, 0.008], echo: 0.3, pat: bars('D5 - - G5 A5 Bb5', 'C6 - - Bb5 A5 G5', 'F#5 - - A5 - D5', 'G5 - - - - .', 'F5 - - Bb5 C6 D6', 'Eb6 - - D6 C6 Bb5', 'A5 - - C6 - A5', 'Bb5 - - - - .') },
      { wave: 'tri', v: 0.24, env: 'pluck', pat: bars('G2 - . . . .', 'C3 - . . . .', 'D3 - . . . .', 'G2 - . . . .', 'Bb2 - . . . .', 'Eb3 - . . . .', 'F2 - . . . .', 'Bb2 - . . . .') },
      { wave: 'p12', v: 0.022, env: 'pluck', pat: bars('. . G4+Bb4+D5 . G4+Bb4+D5 .', '. . G4+C5+Eb5 . G4+C5+Eb5 .', '. . F#4+A4+D5 . F#4+A4+D5 .', '. . G4+Bb4+D5 . G4+Bb4+D5 .', '. . F4+Bb4+D5 . F4+Bb4+D5 .', '. . G4+Bb4+Eb5 . G4+Bb4+Eb5 .', '. . F4+A4+C5 . F4+A4+C5 .', '. . F4+Bb4+D5 . F4+Bb4+D5 .') },
    ],
    drums: null, voices: 'waltz, no drums',
  },
  kuliglig: {
    name: 'Kuliglig', where: 'Optional ambience: no melody, for deep focus', bpm: 70, key: 'A drone', prog: 'A – E', meter: 'free',
    tracks: [
      { wave: 'tri', v: 0.08, env: 'swell', pat: 'A2 ' + rep('-', 23) + ' E2 ' + rep('-', 23) },
    ],
    drums: rep('r . . r . . . . . . t . . . r . . . . . . . . .', 2), voices: 'crickets, stars, drone',
  },
};
function parseTrack(str) {
  const toks = str.trim().split(/\s+/), by = new Map(); let last = null;
  toks.forEach((tk, i) => {
    if (tk === '-') { if (last && last.end === i) { last.len++; last.end++; } }
    else if (tk === '.') last = null;
    else { last = { n: tk, len: 1, end: i + 1 }; by.set(i, last); }
  });
  return { total: toks.length, by };
}
const songSteps = (s) => s.tracks.length ? s.tracks[0].pat.trim().split(/\s+/).length : s.drums.trim().split(/\s+/).length;
let song = null;
function playSong(id) {
  stopSong();
  const c = ensure(), s = SONGS[id], stepDur = 60 / s.bpm / 2;
  const tracks = s.tracks.map((tr) => ({ ...tr, ev: parseTrack(tr.pat) }));
  const drums = s.drums ? s.drums.trim().split(/\s+/) : null;
  const st = { id, next: c.currentTime + 0.08, step: 0 };
  st.timer = setInterval(() => {
    while (st.next < c.currentTime + 0.2) {
      for (const tr of tracks) {
        const e = tr.ev.by.get(st.step % tr.ev.total);
        if (!e) continue;
        for (const nn of e.n.split('+')) {
          const o = { at: st.next, d: e.len * stepDur * 0.94, v: tr.v, bus: musicBus, echo: tr.echo };
          if (tr.inst === 'bell') bell(N(nn), o);
          else tone({ ...o, wave: tr.wave, f: N(nn), env: tr.env, vib: tr.vib, vibDelay: 0.12 });
        }
      }
      if (drums) {
        const dk = drums[st.step % drums.length], o = { at: st.next, bus: musicBus };
        if (dk === 'k') kick({ ...o, v: 0.3 }); else if (dk === 'h') hat(o); else if (dk === 'b') brush(o);
        else if (dk === 'c') crash(o); else if (dk === 'r') chirp(o); else if (dk === 't') twinkleNote(o);
      }
      st.next += stepDur; st.step++;
    }
  }, 25);
  song = st;
}
function stopSong() {
  if (!song) return;
  clearInterval(song.timer); song = null;
  for (const e of live) if (e.bus === musicBus) { try { e.node.stop(); } catch (_) { /* already stopped */ } }
}

/* ============================== TALA RUNTIME ============================== */
// Area -> song. The 'ambience' style replaces every song with the cricket drone.
const AREA_SONG = { gate: 'gabi', home: 'gabi', text: 'buwan', geo: 'bituin' };
const prefs = Object.assign({ musicOn: true, musicVol: 25, sfxOn: true, sfxVol: 65, style: 'melody' }, prev && prev.prefs);
let curArea = (prev && prev._area) || null;      // last area requested by the server
let override = (prev && prev._override) || null; // special() song, until the area changes
let hold = false;                                // music held back (boot splash)
let playing = null;                              // song id currently scheduled
let musicToken = 0;                              // invalidates stale crossfades
const disposers = [];

function wantedSong() {
  if (!prefs.musicOn || hold) return null;
  if (prefs.style === 'ambience') return 'kuliglig';
  return override || AREA_SONG[curArea] || null;
}
function syncVolumes() {
  vol.master = 0.8; vol.echo = 0.55;
  vol.sfx = prefs.sfxOn ? prefs.sfxVol / 100 : 0;
  vol.music = prefs.musicOn ? prefs.musicVol / 100 : 0;
  applyVolumes();
}
// Fade the music bus (and its echo send) to `to` (0..1 of the configured level).
function fadeMusic(to, tau) {
  if (!ctx) return;
  const t = ctx.currentTime, lvl = to * vol.music ** 1.6;
  for (const g of [musicBus.gain, musicSend.gain]) { g.cancelScheduledValues(t); g.setTargetAtTime(lvl, t, tau); }
}
// Crossfade (about 0.6 s) to whatever the current state wants. Safe to call at any time.
function updateMusic() {
  if (!ctx || ctx.state !== 'running') return;
  const want = wantedSong();
  if (want === playing) { if (want) fadeMusic(1, 0.15); return; }
  const token = ++musicToken;
  const swap = () => {
    if (token !== musicToken) return;
    stopSong(); playing = null;
    if (want) { playSong(want); playing = want; fadeMusic(1, 0.15); }
  };
  if (playing) { fadeMusic(0, 0.12); later(swap, 600); }
  else {
    const t = ctx.currentTime;
    for (const g of [musicBus.gain, musicSend.gain]) { g.cancelScheduledValues(t); g.setValueAtTime(0, t); }
    swap();
  }
}

const api = {
  unlocked: false,
  prefs,
  _area: curArea,
  _override: override,
  unlock() {
    try {
      const c = ensure();
      if (c.state === 'suspended' && !document.hidden) c.resume();
      api.unlocked = true;
      syncVolumes();
      c.onstatechange = () => { if (c.state === 'running') updateMusic(); };
      if (c.state === 'running') updateMusic();
    } catch (_) { /* sound is an enhancement; never break the app */ }
  },
  setPrefs(p) {
    Object.assign(prefs, p || {});
    syncVolumes();
    if (api.unlocked) updateMusic();
  },
  area(name) {
    if (name !== curArea) { curArea = name; override = null; api._area = name; api._override = null; }
    if (api.unlocked) updateMusic();
  },
  play(name, arg, delayMs = 0) {
    if (!api.unlocked || !prefs.sfxOn || document.hidden || typeof S[name] !== 'function') return;
    const run = () => { try { S[name](arg); } catch (_) { /* a bad cue must not stop the app */ } };
    if (delayMs > 0) later(run, delayMs); else run();
  },
  special(name) {
    if (!api.unlocked || document.hidden || typeof S[name] !== 'function') return;
    // Duck the music, play the fanfare, then settle on the harana until the area changes.
    musicToken++; fadeMusic(0, 0.08);
    if (prefs.sfxOn) S[name]();
    later(() => {
      override = 'harana'; api._override = override;
      if (playing) { stopSong(); playing = null; }
      updateMusic();
    }, name === 'fullSky' ? 3200 : 2400);
  },
  // Schedule one progress tick per bar segment filled in the splash tail, then bootReady.
  // `segments` is the list of CSS delays (seconds) of those segments, or just their count.
  bootTimeline(fromPct, seconds, segments) {
    hold = true; fadeMusic(0, 0.1);
    later(() => { if (hold) { hold = false; updateMusic(); } }, (seconds + 12.5) * 1000); // never trap the music
    const delays = Array.isArray(segments) ? segments
      : Array.from({ length: Math.max(0, segments | 0) }, (_, k) => seconds * k / Math.max(1, segments));
    delays.forEach((d, k) => {
      const i = 1 + Math.min(7, Math.floor(k * 8 / delays.length));
      api.play('progress', i, Math.max(0, d * 1000));
    });
    api.play('bootReady', undefined, Math.max(0, seconds * 1000));
    // Put keyboard focus on START once it shows, so Enter and Space work.
    later(() => { const b = document.getElementById('tala-start'); if (b) b.focus({ preventScroll: true }); }, seconds * 1000 + 150);
  },
  startPressed() {
    api.unlock();
    api.play('start');
    document.body.classList.add('tala-boot-complete');
    try { document.cookie = 'tala_booted=1; path=/; SameSite=Lax'; } catch (_) { /* cookies blocked */ }
    later(() => { hold = false; updateMusic(); }, 1300);
  },
  _dispose() {
    for (const f of disposers.splice(0)) { try { f(); } catch (_) { /* already gone */ } }
    stopSong();
    for (const id of timers) clearTimeout(id);
    timers.clear();
  },
};

/* ---------------- gestures and event sounds ---------------- */
const on = (target, type, fn, opt) => { target.addEventListener(type, fn, opt); disposers.push(() => target.removeEventListener(type, fn, opt)); };
const doc = document;
let lastKey = null, lastKeyAt = 0, lastSlider = 0, lastRun = 0;

// A label click is followed by a synthetic click on its input; play one sound for the pair.
function once(el) {
  const now = performance.now();
  if (el === lastKey && now - lastKeyAt < 80) return false;
  lastKey = el; lastKeyAt = now;
  return true;
}
function classify(ev) {
  const t = ev.target;
  if (!(t instanceof Element)) return;
  if (t.closest('[data-testid="stSidebarNav"] a, [data-testid="stPageLink"] a')) return api.play('nav');
  const summary = t.closest('details > summary');
  if (summary) return api.play(summary.parentElement.open ? 'learnClose' : 'learnOpen');
  const sw = t.closest('[role="switch"], [data-baseweb="checkbox"], label:has(input[type="checkbox"]), input[type="checkbox"]');
  if (sw) {
    if (!once(sw.closest('label') || sw)) return;
    const input = sw.matches('input') ? sw : sw.querySelector('input');
    let was;
    if (sw.hasAttribute('aria-checked')) was = sw.getAttribute('aria-checked') === 'true';
    else if (input) was = t === input ? !input.checked : input.checked; // a direct input click has already flipped
    else return;
    return api.play(was ? 'toggleOff' : 'toggleOn');
  }
  const sel = t.closest('[role="radio"], [data-baseweb="radio"], [role="option"], li[role="option"]');
  if (sel) { if (once(sel.closest('label') || sel)) api.play('select'); return; }
  if (t.closest('[data-testid="stDownloadButton"] button')) return api.play('download');
  if (t.closest('[data-testid="stCode"] button')) return api.play('copy');
  if (t.closest('.st-key-tala-gate-langs button')) { api.play('language'); updateMusic(); return; }
  if (t.closest('#tala-start')) return api.startPressed();
  if (t.closest('button, a[href], [role="button"], [role="tab"], [role="menuitem"]')) api.play('click');
}
const unlockOnGesture = () => api.unlock();
on(doc, 'pointerdown', unlockOnGesture, true);
on(doc, 'keydown', unlockOnGesture, true);
on(doc, 'click', (ev) => { try { classify(ev); } catch (_) { /* never break clicks */ } }, true);
const sliderUp = (ev) => {
  if (!(ev.target instanceof Element) || !ev.target.closest('[role="slider"]')) return;
  const now = performance.now();
  if (now - lastSlider < 150) return;
  lastSlider = now; api.play('slider');
};
on(doc, 'pointerup', sliderUp, true);
on(doc, 'keyup', sliderUp, true);

// Spinners only show on cache misses, so `run` means real compute (at most one per second).
const mo = new MutationObserver((muts) => {
  for (const m of muts) for (const n of m.addedNodes) {
    if (n.nodeType !== 1) continue;
    if ((n.matches && n.matches('[data-testid="stSpinner"]')) || (n.querySelector && n.querySelector('[data-testid="stSpinner"]'))) {
      const now = performance.now();
      if (now - lastRun > 1000) { lastRun = now; api.play('run'); }
      return;
    }
  }
});
mo.observe(doc.body, { childList: true, subtree: true });
disposers.push(() => mo.disconnect());

// Pause with the tab (ARAW does the same).
on(doc, 'visibilitychange', () => {
  if (!ctx || !api.unlocked) return;
  if (doc.hidden) ctx.suspend(); else ctx.resume();
});

// Stars twinkle on the language gate every 7-9 s while its sky is on screen.
(function twinkleLoop() {
  later(() => { if (doc.querySelector('.tala-gate-sky')) api.play('twinkle'); twinkleLoop(); }, 7000 + Math.random() * 2000);
})();

// Cue scripts render in an element container of their own; keep it from adding a gap.
if (!doc.getElementById('tala-cue-style')) {
  const st = doc.createElement('style');
  st.id = 'tala-cue-style';
  st.textContent = '[data-testid="stElementContainer"]:has(.tala-cue), .stElementContainer:has(.tala-cue) { display: none !important; }';
  doc.head.appendChild(st);
}

window.__talaSound = api;
if (prev && prev.unlocked) api.unlock();
})();
