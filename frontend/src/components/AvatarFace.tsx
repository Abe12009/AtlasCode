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
 * character system's artwork. Every shape below is a basic circle/path. */
export function AvatarFace({ config, className }: { config: AvatarConfig; className?: string }) {
  const skin = SKIN_TONES.find((s) => s.id === config.skinTone)?.color ?? SKIN_TONES[2].color;
  const hairColor = HAIR_COLORS.find((c) => c.id === config.hairColor)?.color ?? HAIR_COLORS[1].color;
  const outfitColor = OUTFITS.find((o) => o.id === config.outfit)?.color ?? OUTFITS[0].color;

  return (
    <svg viewBox="0 0 100 100" className={className} role="img" aria-label="Avatar">
      {/* Outfit / shoulders */}
      <path d="M20 100 Q50 78 80 100 L80 100 L20 100 Z" fill={outfitColor} />
      {config.outfit === 'buttonup' && <path d="M50 82 L46 100 L54 100 Z" fill="#CBD5E1" />}

      {/* Neck */}
      <rect x="42" y="62" width="16" height="16" fill={skin} />

      {/* Head */}
      <circle cx="50" cy="42" r="26" fill={skin} />

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
      return <path d="M24 34 Q50 12 76 34 Q76 24 50 22 Q24 24 24 34 Z" fill={color} />;
    case 'curly':
      return (
        <g fill={color}>
          <circle cx="28" cy="26" r="7" />
          <circle cx="38" cy="18" r="8" />
          <circle cx="50" cy="15" r="8" />
          <circle cx="62" cy="18" r="8" />
          <circle cx="72" cy="26" r="7" />
        </g>
      );
    case 'long':
      return (
        <path
          d="M22 40 Q20 14 50 12 Q80 14 78 40 L78 60 L70 60 L70 34 Q70 22 50 20 Q30 22 30 34 L30 60 L22 60 Z"
          fill={color}
        />
      );
    case 'bun':
      return (
        <g fill={color}>
          <path d="M24 32 Q50 10 76 32 Q76 22 50 20 Q24 22 24 32 Z" />
          <circle cx="50" cy="12" r="7" />
        </g>
      );
    case 'afro':
      return <circle cx="50" cy="28" r="24" fill={color} />;
    case 'spiky':
      return (
        <path
          d="M22 32 L28 14 L34 30 L42 10 L48 28 L54 8 L60 28 L68 12 L74 30 L78 34 Q50 14 22 32 Z"
          fill={color}
        />
      );
    case 'short':
    default:
      return <path d="M23 34 Q50 8 77 34 Q77 20 50 18 Q23 20 23 34 Z" fill={color} />;
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

  let mouth = <path d="M41 53 Q50 59 59 53" stroke="#7A3B2E" strokeWidth="2.4" fill="none" strokeLinecap="round" />;
  if (style === 'grin') {
    mouth = <path d="M40 52 Q50 62 60 52 Z" fill="#7A3B2E" />;
  } else if (style === 'calm') {
    mouth = <path d="M43 55 L57 55" stroke="#7A3B2E" strokeWidth="2.2" strokeLinecap="round" />;
  }

  return (
    <g>
      {style === 'shades' ? (
        <>
          <rect x="35" y="38" width="12" height="8" rx="3" fill="#111827" />
          <rect x="53" y="38" width="12" height="8" rx="3" fill="#111827" />
          <rect x="47" y="40" width="6" height="2" fill="#111827" />
        </>
      ) : style === 'wink' ? (
        wink
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
    case 'none':
    default:
      return null;
  }
}
