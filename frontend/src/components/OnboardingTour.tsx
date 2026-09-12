import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Button, cn } from './ui';
import { CodyCharacter } from './CodyCharacter';
import { useElementRect } from '../hooks/useElementRect';
import { useMediaQuery } from '../hooks/useMediaQuery';

interface TourStep {
  title: string;
  description: string;
  /** CSS selector for the real chrome element this step points at. Every
   * selector here targets something rendered by Layout itself (nav links,
   * the XP bar, the profile menu, the Cody bubble) -- never page content --
   * so it exists identically for a brand-new account with zero courses/XP/
   * achievements and a returning one, and never unmounts on route change. */
  target?: string;
  /** Real route to navigate to when this step becomes active, so the app
   * behind the spotlight is the actual page, not a static backdrop. */
  route?: string;
}

//: Stable top-level array -- see the identical note in CodyCharacter.tsx.
//: Not itself animated with repeat:Infinity, but keeping the habit consistent
//: avoids ever having to relearn this the hard way in this specific file.
const TOUR_STEPS: TourStep[] = [
  {
    title: "Hey, I'm Cody!",
    description: "Your computer science companion, at your service. Let's take a quick spin around AtlasCode together.",
  },
  {
    title: 'Your learning roadmap',
    description: 'Courses live on a roadmap you work through step by step — finish one and the next lights up. No getting lost, I promise.',
    target: '[data-tour="tour-nav-courses"]',
    route: '/app/courses',
  },
  {
    title: 'XP and streaks',
    description: "Finish lessons, rack up XP, and level up. Show up daily and watch that streak grow — I'll be cheering you on from the top of every page.",
    target: '[data-tour="tour-xp"]',
  },
  {
    title: 'Make it yours',
    description: 'Swing by your profile anytime to build a custom avatar or upload a photo. Make this place feel like yours.',
    target: '[data-tour="tour-profile"]',
    route: '/app/profile',
  },
  {
    title: "I'm always nearby",
    description: "Stuck on something? Click my bubble in the corner — I can answer CS questions and point you toward what to learn next.",
    target: '[data-tour="tour-bubble"]',
  },
];

const SPOTLIGHT_PADDING = 8;
const CAPTION_WIDTH = 320;
const CAPTION_GAP = 16;
const VIEWPORT_MARGIN = 16;
const DIM_CLASS = 'fixed bg-black/60';

function SpotlightBackdrop({ rect }: { rect: DOMRect | null }) {
  if (!rect) {
    return <div className={cn(DIM_CLASS, 'inset-0')} aria-hidden="true" />;
  }

  const top = Math.max(0, rect.top - SPOTLIGHT_PADDING);
  const left = Math.max(0, rect.left - SPOTLIGHT_PADDING);
  const right = rect.right + SPOTLIGHT_PADDING;
  const bottom = rect.bottom + SPOTLIGHT_PADDING;

  return (
    <div aria-hidden="true">
      <div className={DIM_CLASS} style={{ top: 0, left: 0, right: 0, height: top }} />
      <div className={DIM_CLASS} style={{ top: bottom, left: 0, right: 0, bottom: 0 }} />
      <div className={DIM_CLASS} style={{ top, left: 0, width: left, height: bottom - top }} />
      <div className={DIM_CLASS} style={{ top, left: right, right: 0, height: bottom - top }} />
      <motion.div
        layout
        transition={{ type: 'spring', stiffness: 300, damping: 26 }}
        className="fixed rounded-xl ring-2 ring-primary-400 shadow-[0_0_0_4px_rgba(59,130,246,0.25)] pointer-events-none"
        style={{ top, left, width: right - left, height: bottom - top }}
      />
    </div>
  );
}

function captionPosition(rect: DOMRect | null) {
  if (!rect) {
    return {
      left: window.innerWidth / 2 - CAPTION_WIDTH / 2,
      top: window.innerHeight / 2 - 100,
    };
  }
  const centerX = rect.left + rect.width / 2;
  const left = Math.min(
    Math.max(centerX - CAPTION_WIDTH / 2, VIEWPORT_MARGIN),
    window.innerWidth - CAPTION_WIDTH - VIEWPORT_MARGIN
  );
  // Flip above the target when there isn't room below (e.g. a short viewport).
  const estimatedCaptionHeight = 220;
  const top =
    rect.bottom + CAPTION_GAP + estimatedCaptionHeight <= window.innerHeight
      ? rect.bottom + CAPTION_GAP
      : Math.max(VIEWPORT_MARGIN, rect.top - CAPTION_GAP - estimatedCaptionHeight);
  return { left, top };
}

interface OnboardingTourProps {
  onDone: () => void;
}

/** A live guided tour: Cody walks the actual app chrome (nav, XP bar, profile
 * menu, his own bubble) with real route changes underneath, replacing the
 * old static 5-screen modal. Every target lives in Layout itself, so it's
 * present and stable across every step and every route change -- nothing
 * here ever points at page content that could be empty for a new account.
 */
export function OnboardingTour({ onDone }: OnboardingTourProps) {
  const [stepIndex, setStepIndex] = useState(0);
  const navigate = useNavigate();
  const location = useLocation();
  const isDesktop = useMediaQuery('(min-width: 1024px)');

  const step = TOUR_STEPS[stepIndex];
  const isLast = stepIndex === TOUR_STEPS.length - 1;

  useEffect(() => {
    if (step.route && location.pathname !== step.route) {
      navigate(step.route);
    }
    // Only re-run when the step itself changes -- not on every location
    // change, which would fight a user-triggered navigation mid-step.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stepIndex]);

  // Mobile/narrow viewports have no visible desktop nav to spotlight (it's
  // collapsed into a hamburger menu) -- fall back to a centered Cody with no
  // cutout rather than pointing at a hidden element. Route navigation still
  // happens above; only the spotlight itself is skipped.
  const targetSelector = isDesktop ? step.target ?? null : null;
  const rect = useElementRect(targetSelector);
  const position = captionPosition(rect);

  const goNext = () => (isLast ? onDone() : setStepIndex((i) => i + 1));

  return (
    <div className="fixed inset-0 z-[80]" role="dialog" aria-modal="true" aria-label="Onboarding tour">
      <SpotlightBackdrop rect={rect} />

      <motion.div
        initial={false}
        animate={{ left: position.left, top: position.top }}
        transition={{ type: 'spring', stiffness: 260, damping: 24 }}
        className="fixed z-[81] flex flex-col items-center gap-3"
        style={{ width: CAPTION_WIDTH }}
      >
        <CodyCharacter size={64} state="talking" />

        <div className="w-full glass-strong rounded-xl shadow-modal border border-border-primary/50 p-4 text-center">
          <h2 className="text-base font-bold text-text-primary">{step.title}</h2>
          <p className="mt-1.5 text-sm text-text-secondary leading-relaxed">{step.description}</p>

          <div
            className="flex items-center justify-center gap-1.5 mt-3"
            role="progressbar"
            aria-valuenow={stepIndex + 1}
            aria-valuemin={1}
            aria-valuemax={TOUR_STEPS.length}
          >
            {TOUR_STEPS.map((_, i) => (
              <motion.span
                key={i}
                animate={{ width: i === stepIndex ? 24 : 6 }}
                transition={{ type: 'spring', stiffness: 500, damping: 20 }}
                className={cn('h-1.5 rounded-full', i === stepIndex ? 'bg-primary-500' : 'bg-border-primary')}
              />
            ))}
          </div>

          <div className="flex items-center justify-between w-full gap-3 mt-3">
            <button onClick={onDone} className="text-sm text-text-tertiary hover:text-text-primary transition-colors">
              Skip
            </button>
            <Button variant="primary" size="sm" onClick={goNext}>
              {isLast ? 'Get started' : 'Next'}
            </Button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
