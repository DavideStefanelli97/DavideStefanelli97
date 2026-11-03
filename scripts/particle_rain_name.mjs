/* Adapted from the supplied particle-rain-word piece for the profile name. */
import { fileURLToPath } from "node:url";
import { resolve } from "node:path";
import { readFileSync } from "node:fs";

class Grid {
  constructor(cols, rows) {
    this.cols = cols;
    this.rows = rows;
    this.ch = new Array(cols * rows).fill(" ");
    this.co = new Array(cols * rows).fill(" ");
  }
  clear() { this.ch.fill(" "); this.co.fill(" "); }
  set(x, y, ch, co = " ") {
    x = Math.floor(x); y = Math.floor(y);
    if (x < 0 || y < 0 || x >= this.cols || y >= this.rows) return;
    const i = x + y * this.cols;
    this.ch[i] = ch;
    this.co[i] = co;
  }
  hline(x0, x1, y, ch, co) {
    for (let x = x0; x <= x1; x++) this.set(x, y, ch, co);
  }
  text(x, y, value, co) {
    for (let i = 0; i < value.length; i++) this.set(x + i, y, value[i], co);
  }
  frame() {
    const text = [], color = [];
    for (let y = 0; y < this.rows; y++) {
      const a = y * this.cols, b = a + this.cols;
      text.push(this.ch.slice(a, b).join(""));
      color.push(this.co.slice(a, b).join(""));
    }
    return { text: text.join("\n"), color: color.join("\n") };
  }
}

const palette = (colors) => Object.fromEntries(colors.map((color, i) => ["0123456789abcdefghijklmnopqrstuvwxyz"[i], color]));
function gradient(stops, n) {
  const rgb = stops.map((s) => [1, 3, 5].map((i) => parseInt(s.slice(i, i + 2), 16)));
  return Array.from({ length: n }, (_, i) => {
    const p = (i / (n - 1)) * (rgb.length - 1), j = Math.min(rgb.length - 2, Math.floor(p)), f = p - j;
    return "#" + rgb[j].map((v, c) => Math.round(v + (rgb[j + 1][c] - v) * f).toString(16).padStart(2, "0")).join("");
  });
}
function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const LINES = ["DAVIDE", "STEFANELLI"];
const HIGH_RES_MASKS = JSON.parse(readFileSync(new URL("./particle_rain_mask.json", import.meta.url), "utf8"));
function fineMask(line) {
  const { w, h, rows } = HIGH_RES_MASKS[line];
  return { w, h, at: (x, y) => (x >= 0 && y >= 0 && x < w && y < h ? Number(rows[y][x]) : 0) };
}
const PER = 8, G = 70;
// Sampled from brain-turntable-ascii-blue.gif, which uses the original cortical colors.
const BRAIN_COLORS = ["#3966a5", "#54a9d9", "#69d7f9", "#86f9f9"];
const HUES = gradient(BRAIN_COLORS, 10);
const DEPTH = [0.55, 0.78, 1.0];
const KEYS = "0123456789abcdefghijklmnopqrstuvwxyz";
const scaleColor = (hex, shade) => "#" + [1, 3, 5]
  .map((i) => Math.round(parseInt(hex.slice(i, i + 2), 16) * shade).toString(16).padStart(2, "0"))
  .join("");
const RAMP = HUES.flatMap((hue) => DEPTH.map((shade) => scaleColor(hue, shade)));
const DRIZZLE = KEYS[RAMP.length], FLOOR = KEYS[RAMP.length + 1];
const CHROME = KEYS[RAMP.length + 2], TITLE = KEYS[RAMP.length + 3];

export const meta = {
  slug: "particle-rain-name",
  name: "DAVIDE STEFANELLI - Particle Rain",
  category: "lettering",
  note: "Dense ASCII grains rain into a two-line name, hold, then pour off the bottom.",
  tags: ["particles", "title", "hero", "intro", "letters"],
  cols: 190, rows: 60, fps: 20,
  palette: palette([...RAMP, "#1c3150", "#18253a", "#526574", "#a5bfcb"]),
};

export default function create() {
  const { cols, rows } = meta;
  const g = new Grid(cols, rows);
  const parts = [];
  LINES.forEach((line, lineIndex) => {
    const M = fineMask(line);
    const x0 = Math.floor((cols - M.w) / 2), y0 = 5 + lineIndex * 26;
    const R = rng(11 + lineIndex * 7);
    for (let y = 0; y < M.h; y++) for (let x = 0; x < M.w; x++) if (M.at(x, y)) {
      const density = M.at(x, y);
      const ty = y0 + y, from = -1 - R() * 14;
      const land = 0.8 + ((M.h - 1 - y) / M.h) * 2.5 + R() * 0.65 + (x / M.w) * 0.35 + lineIndex * 0.25;
      const fall = Math.sqrt((2 * (ty - from)) / G);
      const position = Math.floor(((x0 + x - 10 + ty * 0.07) / (cols - 20)) * HUES.length);
      const relief = 0.48 + 0.22 * (1 - y / M.h) + 0.1 * (1 - x / M.w)
        + (M.at(x, y - 1) ? 0 : 0.19) - (M.at(x, y + 1) ? 0 : 0.08)
        + ((((x * 37 + y * 61 + lineIndex * 17) % 17) / 16) - 0.5) * 0.12;
      const shade = relief > 0.78 ? 2 : relief > 0.56 ? 1 : 0;
      const hue = Math.min(HUES.length - 1, Math.max(0, position + shade - 1));
      const glyphs = density === 1 ? ".:+" : density === 2 ? "*#o" : "@@##%%&&WWMM88";
      parts.push({ x: x0 + x, ty, from, t0: land - fall, land,
        out: 5.5 + R() * 0.6 + ((M.h - y) / M.h) * 0.35 + lineIndex * 0.1,
        co: KEYS[hue * DEPTH.length + (density === 1 ? Math.min(shade, 1) : shade)],
        bright: KEYS[hue * DEPTH.length + 2],
        glyph: glyphs[Math.floor(R() * glyphs.length)] });
    }
  });
  const flood = rng(5), drift = [];
  for (let i = 0; i < 120; i++) drift.push([flood() * cols, flood() * 65, 7 + flood() * 12]);
  return (t) => {
    g.clear();
    const lt = ((t % PER) + PER) % PER;
    // faint background drizzle of stray grains
    for (const [x, o, v] of drift) {
      const y = ((o + t * v) % (rows + 6)) - 3;
      g.set(x, y, ".", DRIZZLE);
    }
    // The same ASCII terminal chrome used by the profile panels.
    g.hline(1, cols - 2, 0, "-", CHROME);
    g.hline(1, cols - 2, 2, "-", CHROME);
    g.hline(1, cols - 2, rows - 1, "-", CHROME);
    for (let y = 0; y < rows; y++) {
      g.set(0, y, "|", CHROME);
      g.set(cols - 1, y, "|", CHROME);
    }
    for (const y of [0, 2, rows - 1]) {
      g.set(0, y, "+", CHROME);
      g.set(cols - 1, y, "+", CHROME);
    }
    g.set(3, 1, ">", TITLE);
    if (Math.floor(lt * 2) % 2 === 0) g.set(4, 1, "_", TITLE);
    g.text(6, 1, "terminal - identity.txt", TITLE);
    g.text(cols - 16, 1, "[_] [ ] [X]", CHROME);
    g.hline(1, cols - 2, rows - 2, "_", FLOOR);
    for (const p of parts) {
      if (lt < p.t0) continue;
      if (lt < p.land) {
        const dt = lt - p.t0, y = p.from + 0.5 * G * dt * dt;
        g.set(p.x, y, ":", p.bright);
        if (dt > 0.12) g.set(p.x, y - 1, "|", p.co);
      } else if (lt < p.out) {
        const age = lt - p.land;
        g.set(p.x, p.ty, age < 0.12 ? "*" : p.glyph, age < 0.12 ? p.bright : p.co);
      } else {
        const dt = lt - p.out, y = p.ty + 0.5 * G * dt * dt;
        if (y < rows - 2) { g.set(p.x, y, p.glyph, p.co); if (dt > 0.1) g.set(p.x, y - 1, ":", p.co); }
        else if (y < rows + 3) g.set(p.x + ((p.ty * 7 + p.x) % 3) - 1, rows - 2, "#", p.co);
      }
    }
    return g.frame();
  };
}
// The same deterministic frames feed the GIF exporter and the browser preview.
if (process.argv[1] && fileURLToPath(import.meta.url) === resolve(process.argv[1])) {
  const draw = create();
  for (let i = 0; i < PER * meta.fps; i++) {
    process.stdout.write(JSON.stringify({ ...draw(i / meta.fps), palette: meta.palette }) + "\n");
  }
}
