import type { SVGProps } from 'react';
import { motion } from 'framer-motion';

export type CodyState = 'idle' | 'talking';

//: Stable top-level objects, not inline literals in JSX -- passing a fresh
//: object/array reference to `animate`/`transition` on every render restarts
//: a `repeat: Infinity` loop instead of letting it progress, which can leave
//: it looking permanently frozen at its first keyframe whenever the parent
//: re-renders for unrelated reasons (see the same lesson already documented
//: in OnboardingWalkthrough.tsx).
const BOB_TALKING_ANIMATE = { y: [0, -4, 0] };
const BOB_IDLE_ANIMATE = { y: 0 };
const BOB_TRANSITION = { duration: 0.6, repeat: Infinity, ease: 'easeInOut' as const };

const MOUTH_TALKING_ANIMATE = { opacity: [0, 1, 0] };
const MOUTH_IDLE_ANIMATE = { opacity: 0 };
const MOUTH_TRANSITION = { duration: 0.6, repeat: Infinity, ease: 'easeInOut' as const };

export interface CodyCharacterProps extends Omit<SVGProps<SVGSVGElement>, 'width' | 'height'> {
  /** Rendered width/height in pixels. A `className` with Tailwind `h-*`/`w-*`
   * utilities (the convention every other icon in this app follows) overrides
   * this via CSS, same as lucide-react icons -- pass whichever fits the call site. */
  size?: number;
  /** 'idle' is the static design; 'talking' loops a small mouth-flap + bob.
   * New states (e.g. 'celebrating', 'thinking') slot in as additional
   * branches below without touching the markup or any call site. */
  state?: CodyState;
}

/** Cody, the AtlasCode mascot -- a chunky monitor character with a dark
 * screen face, cable arms (one waving), and an orange power-button badge.
 * Drop-in replacement for the generic `Bot` icon everywhere Cody appears
 * (nav, chat bubble, chat panel, onboarding): same size/className contract
 * as a lucide icon, but the body's colors are fixed (this is a full
 * character illustration, not a currentColor line icon), so callers should
 * render it directly rather than inside another colored badge/circle.
 */
export function CodyCharacter({ size = 48, state = 'idle', ...props }: CodyCharacterProps) {
  const talking = state === 'talking';

  return (
    <svg
      viewBox="0 0 680 530"
      width={size}
      height={size}
      role="img"
      aria-label="Cody"
      {...props}
    >
      <title>Cody</title>
      <ellipse cx="340" cy="445" rx="110" ry="16" fill="#000000" fillOpacity="0.12" />

      <motion.g
        animate={talking ? BOB_TALKING_ANIMATE : BOB_IDLE_ANIMATE}
        transition={talking ? BOB_TRANSITION : undefined}
      >
        <path d="M210 260 Q175 275 165 305" stroke="#2563EB" strokeWidth="16" strokeLinecap="round" fill="none" />
        <path d="M470 250 Q505 225 515 190" stroke="#2563EB" strokeWidth="16" strokeLinecap="round" fill="none" />
        <rect x="250" y="400" width="180" height="28" rx="14" fill="#2563EB" />
        <rect x="310" y="360" width="60" height="40" rx="8" fill="#2563EB" />
        <rect x="210" y="140" width="260" height="220" rx="36" fill="#3B82F6" />
        <rect x="210" y="140" width="260" height="220" rx="36" fill="url(#codyBodyGrad)" />
        <rect x="228" y="158" width="224" height="150" rx="22" fill="#101828" />

        <ellipse cx="290" cy="225" rx="24" ry="30" fill="#FFFFFF" />
        <circle cx="295" cy="232" r="14" fill="#101828" />
        <circle cx="286" cy="220" r="5" fill="#FFFFFF" fillOpacity="0.85" />
        <ellipse cx="390" cy="225" rx="24" ry="30" fill="#FFFFFF" />
        <circle cx="385" cy="232" r="14" fill="#101828" />
        <circle cx="394" cy="220" r="5" fill="#FFFFFF" fillOpacity="0.85" />

        <path d="M300 275 Q340 295 380 275" stroke="#BFE3FF" strokeWidth="5" strokeLinecap="round" fill="none" />
        <motion.ellipse
          cx="340"
          cy="282"
          rx="16"
          ry="10"
          fill="#0B1220"
          animate={talking ? MOUTH_TALKING_ANIMATE : MOUTH_IDLE_ANIMATE}
          transition={talking ? MOUTH_TRANSITION : undefined}
        />

        <circle cx="340" cy="330" r="16" fill="#F97316" />
        <line x1="340" y1="320" x2="340" y2="328" stroke="#FFFFFF" strokeWidth="3" strokeLinecap="round" />
        <path d="M330 328 A14 14 0 1 0 350 328" stroke="#FFFFFF" strokeWidth="3" fill="none" strokeLinecap="round" />
      </motion.g>

      <defs>
        <radialGradient id="codyBodyGrad" cx="32%" cy="22%" r="85%">
          <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.28" />
          <stop offset="55%" stopColor="#FFFFFF" stopOpacity="0" />
          <stop offset="100%" stopColor="#000000" stopOpacity="0.1" />
        </radialGradient>
      </defs>
    </svg>
  );
}
