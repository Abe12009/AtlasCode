import { useId } from 'react';
import {
  ACCESSORIES,
  FACE_STYLES,
  HAIR_COLORS,
  HAIR_STYLES,
  OUTFITS,
  SKIN_TONES,
  type AvatarConfig,
} from '../lib/avatar';

/** Original, simplified geometric illustration — not a copy of any existing
 * character system's artwork. Every shape below is a basic circle/path.
 *
 * Fidelity pass (in progress): skin/neck/shoulders now shade with a soft
 * gradient instead of a flat fill, and eyebrows are a shared layer across
 * every face style. Both apply to every avatar already, since they're
 * structural rather than per-option art. Per-hairstyle detail (more paths,
 * a highlight, texture strokes) is being rolled out style by style --
 * `short` (the default) has it now; the other seven still render their
 * original flat-path form pending the same treatment. Head/body geometry
 * (circle radius, neck bounding box) is deliberately UNCHANGED so the
 * not-yet-upgraded hair styles and every accessory -- both hand-tuned to
 * the old coordinates -- still align correctly. */
export function AvatarFace({ config, className }: { config: AvatarConfig; className?: string }) {
  const skin = SKIN_TONES.find((s) => s.id === config.skinTone)?.color ?? SKIN_TONES[2].color;
  const hairColor = HAIR_COLORS.find((c) => c.id === config.hairColor)?.color ?? HAIR_COLORS[1].color;
  const outfitColor = OUTFITS.find((o) => o.id === config.outfit)?.color ?? OUTFITS[0].color;
  // Unique per rendered instance -- several avatars (builder preview, swatch
  // list, other students' cards) can be on screen at once, and SVG resolves
  // gradient url() refs against the whole document, not per-<svg>, so a
  // fixed id would make every instance render the first one's gradient.
  const uid = useId();
  const skinGradId = `${uid}-skin`;

  return (
    <svg viewBox="0 0 100 100" className={className} role="img" aria-label="Avatar">
      <defs>
        <radialGradient id={skinGradId} cx="38%" cy="32%" r="75%">
          <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.22" />
          <stop offset="55%" stopColor="#FFFFFF" stopOpacity="0" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.1" />
        </radialGradient>
      </defs>

      {/* Outfit / shoulders -- smoother shoulder curve than a plain V */}
      <path d="M18 100 Q20 76 50 74 Q80 76 82 100 Z" fill={outfitColor} />
      {config.outfit === 'buttonup' && <path d="M50 82 L46 100 L54 100 Z" fill="#CBD5E1" />}
      {config.outfit === 'sweater' && (
        <path d="M40 78 Q50 84 60 78" stroke="#00000022" strokeWidth="2" fill="none" strokeLinecap="round" />
      )}
      {config.outfit === 'jacket' && (
        <>
          <path d="M50 78 L50 100" stroke="#00000030" strokeWidth="1.5" />
          <path d="M40 78 L46 90 L50 82 Z" fill="#00000020" />
          <path d="M60 78 L54 90 L50 82 Z" fill="#00000020" />
        </>
      )}

      {/* Neck -- a soft trapezoid instead of a hard-edged rectangle */}
      <path d="M42 60 L58 60 L60 78 Q50 82 40 78 Z" fill={skin} />
      <path d="M42 60 L58 60 L60 78 Q50 82 40 78 Z" fill={`url(#${skinGradId})`} />

      {/* Head */}
      <circle cx="50" cy="42" r="26" fill={skin} />
      <circle cx="50" cy="42" r="26" fill={`url(#${skinGradId})`} />

      {/* Hair */}
      <HairLayer style={config.hair} color={hairColor} />

      {/* Face features */}
      <FaceLayer style={config.face} />

      {/* Accessory */}
      <AccessoryLayer style={config.accessory} hair={config.hair} hairColor={hairColor} />
    </svg>
  );
}

function HairLayer({ style, color }: { style: string; color: string }) {
  switch (style) {
    case 'bald':
      return null;
    case 'buzz':
      return (
        <g>
          <path d="M24 34 Q50 12 76 34 Q76 24 50 22 Q24 24 24 34 Z" fill={color} />
          <path d="M30 22 Q40 15 48 15 Q42 18 36 24 Q32 23 30 22 Z" fill="#FFFFFF" fillOpacity="0.14" />
          <path d="M35 20 L36 24" stroke="#000000" strokeOpacity="0.15" strokeWidth="0.8" strokeLinecap="round" />
          <path d="M50 18 L50 23" stroke="#000000" strokeOpacity="0.15" strokeWidth="0.8" strokeLinecap="round" />
          <path d="M65 20 L64 24" stroke="#000000" strokeOpacity="0.15" strokeWidth="0.8" strokeLinecap="round" />
        </g>
      );
    case 'curly':
      return (
        <g>
          <g fill={color}>
            <circle cx="28" cy="26" r="7" />
            <circle cx="38" cy="18" r="8" />
            <circle cx="50" cy="15" r="8" />
            <circle cx="62" cy="18" r="8" />
            <circle cx="72" cy="26" r="7" />
          </g>
          <g fill="#FFFFFF" fillOpacity="0.16">
            <circle cx="36" cy="15" r="2.4" />
            <circle cx="48" cy="12" r="2.4" />
          </g>
          <g stroke="#000000" strokeOpacity="0.1" strokeWidth="1" fill="none">
            <path d="M28 22 Q26 26 28 30" />
            <path d="M72 22 Q74 26 72 30" />
          </g>
        </g>
      );
    case 'long':
      return (
        <g>
          <path
            d="M22 40 Q20 14 50 12 Q80 14 78 40 L78 60 L70 60 L70 34 Q70 22 50 20 Q30 22 30 34 L30 60 L22 60 Z"
            fill={color}
          />
          <path d="M28 20 Q38 12 48 12 Q40 16 33 26 Q29 22 28 20 Z" fill="#FFFFFF" fillOpacity="0.15" />
          <path d="M34 26 Q32 40 34 56" stroke="#000000" strokeOpacity="0.1" strokeWidth="1" fill="none" strokeLinecap="round" />
          <path d="M66 26 Q68 40 66 56" stroke="#000000" strokeOpacity="0.1" strokeWidth="1" fill="none" strokeLinecap="round" />
        </g>
      );
    case 'bun':
      return (
        <g>
          <g fill={color}>
            <path d="M24 32 Q50 10 76 32 Q76 22 50 20 Q24 22 24 32 Z" />
            <circle cx="50" cy="12" r="7" />
          </g>
          <path d="M30 21 Q39 13 48 13 Q42 16 36 23 Q32 21 30 21 Z" fill="#FFFFFF" fillOpacity="0.15" />
          <circle cx="47" cy="9" r="2" fill="#FFFFFF" fillOpacity="0.18" />
          <path d="M36 17 Q38 22 36 27" stroke="#000000" strokeOpacity="0.1" strokeWidth="1" fill="none" strokeLinecap="round" />
        </g>
      );
    case 'afro':
      return (
        <g>
          <circle cx="50" cy="28" r="24" fill={color} />
          <circle cx="42" cy="20" r="10" fill="#FFFFFF" fillOpacity="0.12" />
          <g fill="#000000" fillOpacity="0.08">
            <circle cx="35" cy="30" r="1.6" />
            <circle cx="50" cy="14" r="1.6" />
            <circle cx="63" cy="28" r="1.6" />
            <circle cx="45" cy="38" r="1.6" />
          </g>
        </g>
      );
    case 'spiky':
      return (
        <g>
          <path
            d="M22 32 L28 14 L34 30 L42 10 L48 28 L54 8 L60 28 L68 12 L74 30 L78 34 Q50 14 22 32 Z"
            fill={color}
          />
          <path d="M30 20 Q40 12 48 14 Q42 18 36 26 Q32 23 30 20 Z" fill="#FFFFFF" fillOpacity="0.15" />
          <g fill="#FFFFFF" fillOpacity="0.25">
            <circle cx="28" cy="15" r="1.2" />
            <circle cx="42" cy="11" r="1.2" />
            <circle cx="54" cy="9" r="1.2" />
            <circle cx="68" cy="13" r="1.2" />
          </g>
        </g>
      );
    case 'ponytail':
      return (
        <g>
          <path
            d="M23 36 Q23 13 50 11 Q77 13 77 36 Q77 23 67 19 Q58 14 50 14 Q42 14 33 19 Q23 23 23 36 Z"
            fill={color}
          />
          <path d="M74 30 Q86 34 84 52 Q82 60 76 58 Q80 46 72 34 Z" fill={color} />
          <path d="M30 21 Q39 13 49 13 Q43 16 37 23 Q33 21 30 21 Z" fill="#FFFFFF" fillOpacity="0.16" />
        </g>
      );
    case 'mohawk':
      return (
        <g fill={color}>
          <path d="M44 10 Q50 6 56 10 L58 34 Q50 30 42 34 Z" />
          <path d="M46 12 Q50 10 54 12 L55 20 Q50 18 45 20 Z" fill="#FFFFFF" fillOpacity="0.18" />
        </g>
      );
    case 'short':
    default:
      // The fidelity-pass style: a less-perfectly-domed silhouette (subtle
      // asymmetry at the crown), a soft top-light sheen, and a few texture
      // strokes for part lines -- now the shared treatment across every
      // style above too.
      return (
        <g>
          <path
            d="M23 36 Q23 13 50 11 Q77 13 77 36 Q77 23 67 19 Q58 14 50 14 Q42 14 33 19 Q23 23 23 36 Z"
            fill={color}
          />
          <path
            d="M30 21 Q39 13 49 13 Q43 16 37 23 Q33 21 30 21 Z"
            fill="#FFFFFF"
            fillOpacity="0.16"
          />
          <path d="M36 17 Q38 23 35 29" stroke="#000000" strokeOpacity="0.12" strokeWidth="1" fill="none" strokeLinecap="round" />
          <path d="M50 14 Q51 20 49 26" stroke="#000000" strokeOpacity="0.12" strokeWidth="1" fill="none" strokeLinecap="round" />
          <path d="M64 17 Q62 23 65 29" stroke="#000000" strokeOpacity="0.12" strokeWidth="1" fill="none" strokeLinecap="round" />
        </g>
      );
  }
}

function FaceLayer({ style }: { style: string }) {
  const eyes = (
    <>
      <circle cx="41" cy="42" r="2.6" fill="#1F2937" />
      <circle cx="59" cy="42" r="2.6" fill="#1F2937" />
    </>
  );
  const wink = (
    <>
      <circle cx="41" cy="42" r="2.6" fill="#1F2937" />
      <path d="M56 42 Q59 39 62 42" stroke="#1F2937" strokeWidth="1.6" fill="none" strokeLinecap="round" />
    </>
  );
  const laughEyes = (
    <>
      <path d="M37 42 Q41 38 45 42" stroke="#1F2937" strokeWidth="1.6" fill="none" strokeLinecap="round" />
      <path d="M55 42 Q59 38 63 42" stroke="#1F2937" strokeWidth="1.6" fill="none" strokeLinecap="round" />
    </>
  );
  const surprisedEyes = (
    <>
      <circle cx="41" cy="42" r="3.4" fill="#1F2937" />
      <circle cx="59" cy="42" r="3.4" fill="#1F2937" />
    </>
  );

  let mouth = <path d="M41 53 Q50 59 59 53" stroke="#7A3B2E" strokeWidth="2.4" fill="none" strokeLinecap="round" />;
  if (style === 'grin') {
    mouth = <path d="M40 52 Q50 62 60 52 Z" fill="#7A3B2E" />;
  } else if (style === 'calm') {
    mouth = <path d="M43 55 L57 55" stroke="#7A3B2E" strokeWidth="2.2" strokeLinecap="round" />;
  } else if (style === 'surprised') {
    mouth = <ellipse cx="50" cy="55" rx="4" ry="5.5" fill="#7A3B2E" />;
  } else if (style === 'laugh') {
    mouth = (
      <>
        <path d="M38 51 Q50 64 62 51 Z" fill="#7A3B2E" />
        <path d="M42 53 L58 53" stroke="#FFFFFF" strokeWidth="1.6" strokeLinecap="round" />
      </>
    );
  }

  // Shared across every face style -- a face with no eyebrows at all read as
  // flat/expressionless; a raised arc on the winking side (or both, for
  // "surprised") sells the expression more than the eye/mouth shape alone.
  const eyebrows =
    style === 'wink' ? (
      <>
        <path d="M37 36 Q41 34 45 36" stroke="#4A3728" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <path d="M55 34 Q59 31 63 34" stroke="#4A3728" strokeWidth="1.8" fill="none" strokeLinecap="round" />
      </>
    ) : style === 'surprised' ? (
      <>
        <path d="M36 33 Q41 29 46 33" stroke="#4A3728" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <path d="M54 33 Q59 29 64 33" stroke="#4A3728" strokeWidth="1.8" fill="none" strokeLinecap="round" />
      </>
    ) : (
      <>
        <path d="M37 36 Q41 34 45 36" stroke="#4A3728" strokeWidth="1.8" fill="none" strokeLinecap="round" />
        <path d="M55 36 Q59 34 63 36" stroke="#4A3728" strokeWidth="1.8" fill="none" strokeLinecap="round" />
      </>
    );

  return (
    <g>
      {eyebrows}
      {style === 'shades' ? (
        <>
          <rect x="35" y="38" width="12" height="8" rx="3" fill="#111827" />
          <rect x="53" y="38" width="12" height="8" rx="3" fill="#111827" />
          <rect x="47" y="40" width="6" height="2" fill="#111827" />
        </>
      ) : style === 'wink' ? (
        wink
      ) : style === 'laugh' ? (
        laughEyes
      ) : style === 'surprised' ? (
        surprisedEyes
      ) : (
        eyes
      )}
      {style === 'glasses' && (
        <g stroke="#374151" strokeWidth="1.6" fill="none">
          <circle cx="41" cy="42" r="6.5" />
          <circle cx="59" cy="42" r="6.5" />
          <path d="M47.5 42 L52.5 42" />
        </g>
      )}
      {mouth}
    </g>
  );
}

function AccessoryLayer({
  style,
  hair,
  hairColor,
}: {
  style: string;
  hair: string;
  hairColor: string;
}) {
  switch (style) {
    case 'earrings':
      return (
        <g fill="#D4AF37">
          <circle cx="24" cy="46" r="2" />
          <circle cx="76" cy="46" r="2" />
        </g>
      );
    case 'headphones':
      return (
        <g fill="none" stroke="#1F2937" strokeWidth="3">
          <path d="M22 40 Q50 8 78 40" />
          <rect x="17" y="38" width="8" height="14" rx="3" fill="#1F2937" />
          <rect x="75" y="38" width="8" height="14" rx="3" fill="#1F2937" />
        </g>
      );
    case 'cap':
      return (
        <g>
          <path d="M22 32 Q50 8 78 32 L78 26 Q50 4 22 26 Z" fill="#DC2626" />
          <path d="M50 22 Q66 22 76 30 L84 28 Q68 16 50 16 Z" fill="#B91C1C" />
        </g>
      );
    case 'beanie':
      return (
        <path
          d={hair === 'bald' ? 'M22 34 Q50 8 78 34 L78 26 Q50 6 22 26 Z' : 'M20 32 Q50 4 80 32 L80 24 Q50 0 20 24 Z'}
          fill={hairColor === '#2B2118' ? '#4B5563' : '#374151'}
        />
      );
    case 'scarf':
      return <path d="M36 74 Q50 82 64 74 L64 84 Q50 90 36 84 Z" fill="#DC2626" />;
    case 'bowtie':
      return (
        <g fill="#1F2937">
          <path d="M42 76 L50 80 L42 84 Z" />
          <path d="M58 76 L50 80 L58 84 Z" />
          <circle cx="50" cy="80" r="2" fill="#374151" />
        </g>
      );
    case 'none':
    default:
      return null;
  }
}
