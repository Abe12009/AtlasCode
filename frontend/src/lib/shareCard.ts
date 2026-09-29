import codyIconUrl from '../assets/cody-icon.svg';

/* ---------------------------------------------------------------------------
 * Shareable achievement cards.
 *
 * Drawn with canvas 2D rather than a DOM-to-image library: the card is a
 * gradient, a glyph and three lines of text, which is a few dozen lines here
 * against ~200kB of html2canvas that renders modern CSS unreliably anyway.
 *
 * Only ever renders the viewer's own achievement -- see the `onShare` prop on
 * AchievementBadge, which Profile and the Dashboard pass and PublicProfile
 * does not. Nothing here reads anything the owner cannot already see on their
 * own achievement.
 * ------------------------------------------------------------------------ */

export type ShareFormat = 'post' | 'story';

/** Square for a feed post, 9:16 for a story. Both 1080 wide, which is what
 * every one of these platforms downscales to anyway. */
export const SHARE_FORMATS: Record<ShareFormat, { width: number; height: number }> = {
  post: { width: 1080, height: 1080 },
  story: { width: 1080, height: 1920 },
};

export interface ShareCardData {
  /** The achievement's emoji. Canvas draws it as text, so no icon asset needed. */
  icon: string;
  title: string;
  username: string;
}

const FONT = '"Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';

/**
 * Greedy word wrap against a caller-supplied measure function.
 *
 * Pulled out of `drawCard` because the line count decides the whole stack
 * height -- get it wrong and the layout silently re-centres around the wrong
 * figure. Taking `measure` as an argument keeps it checkable without a canvas.
 */
export function wrapLines(text: string, maxWidth: number, measure: (s: string) => number): string[] {
  const lines: string[] = [];
  let line = '';
  for (const word of text.split(' ')) {
    const candidate = line ? `${line} ${word}` : word;
    if (measure(candidate) > maxWidth && line) {
      lines.push(line);
      line = word;
    } else {
      line = candidate;
    }
  }
  lines.push(line);
  return lines;
}

let markPromise: Promise<HTMLImageElement> | null = null;

/** The Cody mark, loaded once and reused. Same-origin, so it never taints the
 * canvas and `toBlob` keeps working. */
function loadMark(): Promise<HTMLImageElement> {
  markPromise ??= new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error('share card: could not load the Cody mark'));
    img.src = codyIconUrl;
  });
  return markPromise;
}

/**
 * Paints the card onto whatever canvas it is given.
 *
 * Every size derives from `U = min(W, H)` so the card reads identically at 1:1
 * and 9:16 instead of the type growing with the taller canvas, and the content
 * stack is measured before it is centred -- laying out against the height
 * alone put the wordmark straight through the title on the square.
 */
export function drawCard(
  ctx: CanvasRenderingContext2D,
  W: number,
  H: number,
  mark: CanvasImageSource,
  data: ShareCardData,
): void {
  const cx = W / 2;
  const U = Math.min(W, H);

  const R = U * 0.165;
  const eyebrowSize = U * 0.03;
  const titleSize = U * 0.072;
  const userSize = U * 0.036;
  const gapBadge = U * 0.085;
  const gapTitle = U * 0.055;
  const gapUser = U * 0.05;

  ctx.fillStyle = '#0B1120';
  ctx.fillRect(0, 0, W, H);
  let g = ctx.createRadialGradient(cx, H * 0.38, 0, cx, H * 0.38, U * 0.85);
  g.addColorStop(0, 'rgba(37,99,235,0.42)');
  g.addColorStop(0.55, 'rgba(37,99,235,0.10)');
  g.addColorStop(1, 'rgba(11,17,32,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  g = ctx.createRadialGradient(cx, H * 0.8, 0, cx, H * 0.8, U * 0.7);
  g.addColorStop(0, 'rgba(249,115,22,0.24)');
  g.addColorStop(1, 'rgba(11,17,32,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);

  ctx.textAlign = 'center';

  // Wrap first: the line count decides the stack height, which decides where
  // the stack starts.
  ctx.font = `700 ${titleSize}px ${FONT}`;
  const lines = wrapLines(data.title, W * 0.8, (t) => ctx.measureText(t).width);

  const stackHeight =
    R * 2 + gapBadge + eyebrowSize + gapTitle + lines.length * titleSize * 1.16 + gapUser + userSize;
  let y = (H - stackHeight) / 2 - H * 0.035;

  const badgeY = y + R;
  ctx.save();
  ctx.shadowBlur = U * 0.065;
  ctx.shadowColor = 'rgba(249,115,22,0.55)';
  ctx.fillStyle = 'rgba(255,255,255,0.06)';
  ctx.beginPath();
  ctx.arc(cx, badgeY, R, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
  ctx.lineWidth = U * 0.011;
  ctx.strokeStyle = '#F97316';
  ctx.beginPath();
  ctx.arc(cx, badgeY, R, 0, Math.PI * 2);
  ctx.stroke();
  ctx.textBaseline = 'middle';
  ctx.font = `${R * 1.05}px ${FONT}`;
  ctx.fillText(data.icon, cx, badgeY + R * 0.06);
  y += R * 2 + gapBadge;

  ctx.textBaseline = 'alphabetic';
  ctx.font = `600 ${eyebrowSize}px ${FONT}`;
  ctx.fillStyle = '#F97316';
  ctx.letterSpacing = `${U * 0.008}px`;
  ctx.fillText('ACHIEVEMENT UNLOCKED', cx, y + eyebrowSize);
  ctx.letterSpacing = '0px';
  y += eyebrowSize + gapTitle;

  ctx.fillStyle = '#F8FAFC';
  ctx.font = `700 ${titleSize}px ${FONT}`;
  for (const text of lines) {
    y += titleSize;
    ctx.fillText(text, cx, y);
    y += titleSize * 0.16;
  }

  y += gapUser;
  ctx.font = `500 ${userSize}px ${FONT}`;
  ctx.fillStyle = '#A6B4C8';
  ctx.fillText(`@${data.username}`, cx, y + userSize);

  // Mark plus wordmark set in the app's own font -- not assets/cody-lockup.svg,
  // whose baked #101828 "Atlas" would vanish against this ground.
  const markSize = U * 0.095;
  const footerY = H - U * 0.075;
  ctx.font = `700 ${U * 0.05}px ${FONT}`;
  const atlasWidth = ctx.measureText('Atlas').width;
  const codeWidth = ctx.measureText('Code').width;
  let x = cx - (markSize + U * 0.026 + atlasWidth + codeWidth) / 2;
  ctx.drawImage(mark, x, footerY - markSize * 0.8, markSize, markSize);
  x += markSize + U * 0.026;
  ctx.textAlign = 'left';
  ctx.fillStyle = '#F8FAFC';
  ctx.fillText('Atlas', x, footerY);
  ctx.fillStyle = '#F97316';
  ctx.fillText('Code', x + atlasWidth, footerY);
}

/** Renders one card to a PNG blob. */
export async function renderShareCard(data: ShareCardData, format: ShareFormat): Promise<Blob> {
  const { width, height } = SHARE_FORMATS[format];
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('share card: no 2D context');

  const mark = await loadMark();
  // Without this the first card can be drawn in a fallback face and ship with
  // the wrong wordmark, since the webfont may still be loading.
  await document.fonts?.ready;

  drawCard(ctx, width, height, mark, data);

  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => (blob ? resolve(blob) : reject(new Error('share card: toBlob returned null'))),
      'image/png',
    );
  });
}

export type ShareOutcome = 'shared' | 'downloaded' | 'cancelled';

/**
 * Hands the card to the device's share sheet where that exists, and falls back
 * to a download everywhere else.
 *
 * There is no way to post directly into an Instagram or Snapchat story from
 * the web; `navigator.share` opens the native sheet and the student picks the
 * app themselves, exactly as they would sharing any photo.
 */
export async function shareOrDownloadCard(
  data: ShareCardData,
  format: ShareFormat,
): Promise<ShareOutcome> {
  const blob = await renderShareCard(data, format);
  const filename = `atlascode-${slug(data.title)}-${format}.png`;
  const file = new File([blob], filename, { type: 'image/png' });

  if (navigator.canShare?.({ files: [file] })) {
    try {
      await navigator.share({ files: [file] });
      return 'shared';
    } catch (error) {
      // Dismissing the sheet rejects with AbortError -- not a failure, and it
      // must not fall through to a surprise download.
      if (error instanceof DOMException && error.name === 'AbortError') return 'cancelled';
      // Anything else (an unsupported target, a transient platform error) is
      // still better served by handing over the file than by failing.
    }
  }

  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  return 'downloaded';
}

function slug(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 40) || 'achievement';
}
