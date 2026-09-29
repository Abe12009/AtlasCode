import { useEffect, useRef } from 'react';

/* ---------------------------------------------------------------------------
 * The Atlas Graph -- the landing hero's 3D centerpiece.
 *
 * A rotating sphere of lesson nodes wired to their nearest neighbours: the
 * product's own roadmap metaphor seen from orbit. Genuinely 3D (rotation
 * matrix + perspective divide, below), but projected to a plain 2D canvas
 * rather than WebGL -- a glowing wireframe has no lit surfaces, materials or
 * shadows, which is the only thing a WebGL dependency would have bought.
 *
 * Purely decorative. Every piece of real content (headline, CTAs, trust row,
 * XP card) stays as HTML around and over this canvas, never inside it.
 * ------------------------------------------------------------------------ */

const NODE_COUNT = 54;
/** Edges per node. 2 keeps the shell readable; 3+ reads as a solid ball. */
const NEIGHBOURS = 2;
/** Camera distance in sphere radii. Smaller = stronger perspective. */
const CAMERA_Z = 2.6;
/** Median frame time above which we stop animating and hold a static frame.
 * ~31fps. Deliberately below 60/2 so a merely-busy moment does not trip it. */
const SLOW_FRAME_MS = 32;
/** Frames discarded before sampling (first paints include layout + shader warmup). */
const WARMUP_FRAMES = 10;
const SAMPLE_COUNT = 60;
/** A single spike (GC, tab switch, breakpoint) is not a slow device. */
const SPIKE_MS = 200;
/** Angle the static frame freezes at -- picked for a legible, non-polar view. */
const STATIC_T = 2600;

type Node = { x: number; y: number; z: number; done: boolean };

/** Golden-angle spiral: evenly distributed points on a unit sphere, with no
 * clustering at the poles that a naive lat/long grid would give. */
export const NODES: Node[] = Array.from({ length: NODE_COUNT }, (_, i) => {
  const y = 1 - (i / (NODE_COUNT - 1)) * 2;
  const r = Math.sqrt(Math.max(0, 1 - y * y));
  const theta = Math.PI * (1 + Math.sqrt(5)) * i;
  return { x: Math.cos(theta) * r, y, z: Math.sin(theta) * r, done: i % 7 === 0 };
});

const EDGES: [number, number][] = NODES.flatMap((a, i) =>
  NODES.map((b, j) => ({ j, d: (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2 }))
    .filter((o) => o.j !== i)
    .sort((p, q) => p.d - q.d)
    .slice(0, NEIGHBOURS)
    .map((o): [number, number] => [i, o.j]),
);

export type Projected = { X: number; Y: number; k: number; z: number; done: boolean };

/** Rotate a node around Y then X, then divide by depth. `k` is the
 * perspective scale: >1 nearer than the sphere centre, <1 further. */
export function project(node: Node, w: number, h: number, s: number, ay: number, ax: number): Projected {
  const cy = Math.cos(ay);
  const sy = Math.sin(ay);
  const cx = Math.cos(ax);
  const sx = Math.sin(ax);
  const x = node.x * cy - node.z * sy;
  const zy = node.x * sy + node.z * cy;
  const y = node.y * cx - zy * sx;
  const z = node.y * sx + zy * cx;
  const k = CAMERA_Z / (CAMERA_Z + z);
  return { X: w / 2 + x * s * k, Y: h / 2 + y * s * k, k, z, done: node.done };
}

type Palette = {
  node: string;
  done: string;
  edge: string;
  /** Glow reads as depth on a dark ground and as smudge on a light one. */
  glow: boolean;
  /** One tuning knob for how hard the whole thing sits against its ground. */
  intensity: number;
};

const FALLBACK = { node: '147,197,253', done: '249,115,22', edge: '96,165,250' };

/** `#3B82F6` -> `59,130,246`, ready to drop into an `rgba()` string. */
function hexToRgb(hex: string, fallback: string): string {
  const m = /^#?([0-9a-f]{6})$/i.exec(hex.trim());
  if (!m) return fallback;
  const n = parseInt(m[1], 16);
  return `${(n >> 16) & 255},${(n >> 8) & 255},${n & 255}`;
}

/** Colours come from the same `index.css` custom properties every component
 * uses, so retuning the brand ramp retunes the graph -- no second source of
 * truth. Light mode picks darker steps and drops the glow, because a bright
 * node that reads as luminous on #0B1120 is invisible on #F7F9FC. */
function readPalette(el: HTMLElement): Palette {
  const css = getComputedStyle(el);
  const dark = document.documentElement.getAttribute('data-theme') === 'dark';
  const token = (name: string, fallback: string) => hexToRgb(css.getPropertyValue(name), fallback);
  return dark
    ? {
        node: token('--color-primary-300', FALLBACK.node),
        done: token('--color-accent-500', FALLBACK.done),
        edge: token('--color-primary-400', FALLBACK.edge),
        glow: true,
        intensity: 1,
      }
    : {
        node: token('--color-primary-600', FALLBACK.node),
        done: token('--color-accent-600', FALLBACK.done),
        edge: token('--color-primary-500', FALLBACK.edge),
        glow: false,
        intensity: 1.35,
      };
}

function draw(ctx: CanvasRenderingContext2D, w: number, h: number, t: number, p: Palette) {
  const s = Math.min(w, h) * 0.34;
  const points = NODES.map((n) =>
    project(n, w, h, s, t / 6000, 0.42 + Math.sin(t / 9000) * 0.12),
  );

  ctx.clearRect(0, 0, w, h);

  ctx.lineWidth = 1;
  for (const [i, j] of EDGES) {
    const a = points[i];
    const b = points[j];
    const alpha = ((a.k + b.k) / 2 - 0.62) * 0.55 * p.intensity;
    if (alpha <= 0) continue;
    ctx.strokeStyle = `rgba(${p.edge},${alpha})`;
    ctx.beginPath();
    ctx.moveTo(a.X, a.Y);
    ctx.lineTo(b.X, b.Y);
    ctx.stroke();
  }

  // Far nodes first, so near ones overlap them rather than the reverse.
  for (const n of [...points].sort((a, b) => b.z - a.z)) {
    const alpha = Math.min(1, (n.k - 0.55) * 1.9 * p.intensity);
    if (alpha <= 0) continue;
    const r = 3.4 * n.k * (n.done ? 1.5 : 1);
    ctx.shadowBlur = p.glow ? 14 * n.k : 0;
    ctx.shadowColor = `rgb(${n.done ? p.done : p.node})`;
    ctx.fillStyle = `rgba(${n.done ? p.done : p.node},${alpha})`;
    ctx.beginPath();
    ctx.arc(n.X, n.Y, r, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.shadowBlur = 0;
}

export interface HeroGraphProps {
  className?: string;
}

export function HeroGraph({ className }: HeroGraphProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let palette = readPalette(canvas);
    let raf = 0;
    let onScreen = true;
    let elapsed = 0;
    let last = 0;
    let warmup = 0;
    const samples: number[] = [];

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let animating = !reducedMotion.matches;

    const resize = () => {
      // Capping DPR at 1.5 halves the fill cost on 3x phones for no visible loss.
      const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      canvas.width = Math.round(canvas.clientWidth * dpr);
      canvas.height = Math.round(canvas.clientHeight * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };

    const paint = (t: number) => draw(ctx, canvas.clientWidth, canvas.clientHeight, t, palette);
    const paintStatic = () => paint(STATIC_T);

    const stopAnimating = () => {
      animating = false;
      if (raf) cancelAnimationFrame(raf);
      raf = 0;
      paintStatic();
    };

    const frame = (t: number) => {
      const dt = last ? t - last : 0;
      last = t;
      // Clamping keeps a resumed pause from lurching the rotation forward.
      elapsed += Math.min(dt, 100);
      paint(elapsed);

      // Measure what this device actually achieves rather than guessing from
      // core count -- a 4-core student laptop renders this fine.
      if (dt > 0 && samples.length < SAMPLE_COUNT) {
        if (warmup < WARMUP_FRAMES) warmup++;
        else if (dt < SPIKE_MS) samples.push(dt);
        if (samples.length === SAMPLE_COUNT) {
          const median = [...samples].sort((a, b) => a - b)[SAMPLE_COUNT >> 1];
          if (median > SLOW_FRAME_MS) {
            stopAnimating();
            return;
          }
        }
      }
      raf = requestAnimationFrame(frame);
    };

    /** Single gate for every reason to run or not run: reduced motion, a
     * backgrounded tab, and a canvas scrolled out of view all land here. */
    const sync = () => {
      const shouldRun = animating && onScreen && !document.hidden;
      if (shouldRun && !raf) {
        last = 0;
        raf = requestAnimationFrame(frame);
      } else if (!shouldRun && raf) {
        cancelAnimationFrame(raf);
        raf = 0;
      }
    };

    const onMotionChange = () => {
      animating = !reducedMotion.matches;
      if (animating) sync();
      else stopAnimating();
    };

    const onThemeChange = () => {
      palette = readPalette(canvas);
      if (!raf) paintStatic();
    };

    resize();
    paintStatic();

    const resizeObserver = new ResizeObserver(() => {
      resize();
      if (!raf) paintStatic();
    });
    resizeObserver.observe(canvas);

    const intersectionObserver = new IntersectionObserver((entries) => {
      onScreen = entries[entries.length - 1].isIntersecting;
      sync();
    });
    intersectionObserver.observe(canvas);

    const themeObserver = new MutationObserver(onThemeChange);
    themeObserver.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme'],
    });

    document.addEventListener('visibilitychange', sync);
    reducedMotion.addEventListener('change', onMotionChange);
    sync();

    return () => {
      if (raf) cancelAnimationFrame(raf);
      resizeObserver.disconnect();
      intersectionObserver.disconnect();
      themeObserver.disconnect();
      document.removeEventListener('visibilitychange', sync);
      reducedMotion.removeEventListener('change', onMotionChange);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className={className}
      aria-hidden="true"
      // Decorative only: never take a click away from the CTA underneath.
      style={{ pointerEvents: 'none' }}
    />
  );
}
