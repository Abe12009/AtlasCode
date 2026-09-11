import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { Bot, Map, Zap, Palette, MessageCircle } from 'lucide-react';
import { Button, Modal, cn } from './ui';

interface Step {
  icon: typeof Bot;
  title: string;
  description: string;
  //: A small looping personality animation for this step's icon -- keyframe
  //: arrays for the transform properties that change, tailored to what the
  //: step is about (a wave hello, an energetic XP pulse, ...). Baked as a
  //: single stable object (rather than spread inline in JSX) so its
  //: reference never changes across re-renders -- passing a fresh object to
  //: `transition` on every render stops Framer Motion from ever completing
  //: a `repeat: Infinity` loop.
  iconAnimate: Record<string, number[]>;
  iconTransition: { duration: number; ease: 'easeInOut'; repeat: number };
}

const STEPS: Step[] = [
  {
    icon: Bot,
    title: "Hey, I'm Cody!",
    description: "Your computer science companion, at your service. Let's take a quick spin around AtlasCode together.",
    iconAnimate: { rotate: [0, -8, 8, -8, 0] },
    iconTransition: { duration: 2.2, ease: 'easeInOut', repeat: Infinity },
  },
  {
    icon: Map,
    title: 'Your learning roadmap',
    description: "Courses live on a roadmap you work through step by step — finish one and the next lights up. No getting lost, I promise.",
    iconAnimate: { y: [0, -5, 0] },
    iconTransition: { duration: 1.8, ease: 'easeInOut', repeat: Infinity },
  },
  {
    icon: Zap,
    title: 'XP and streaks',
    description: "Finish lessons, rack up XP, and level up. Show up daily and watch that streak grow — I'll be cheering you on from the top of every page.",
    iconAnimate: { scale: [1, 1.12, 1], rotate: [0, -4, 4, 0] },
    iconTransition: { duration: 1.2, ease: 'easeInOut', repeat: Infinity },
  },
  {
    icon: Palette,
    title: 'Make it yours',
    description: 'Swing by your profile anytime to build a custom avatar or upload a photo. Make this place feel like yours.',
    iconAnimate: { rotate: [0, 6, -6, 0] },
    iconTransition: { duration: 2.5, ease: 'easeInOut', repeat: Infinity },
  },
  {
    icon: MessageCircle,
    title: "I'm always nearby",
    description: "Stuck on something? Click my bubble in the corner — I can answer CS questions and point you toward what to learn next.",
    iconAnimate: { scale: [1, 1.08, 1], y: [0, -3, 0] },
    iconTransition: { duration: 1.6, ease: 'easeInOut', repeat: Infinity },
  },
];

interface OnboardingWalkthroughProps {
  onDone: () => void;
}

export function OnboardingWalkthrough({ onDone }: OnboardingWalkthroughProps) {
  const [stepIndex, setStepIndex] = useState(0);
  const step = STEPS[stepIndex];
  const isLast = stepIndex === STEPS.length - 1;
  const Icon = step.icon;

  return (
    <Modal
      isOpen
      onClose={onDone}
      closeOnOverlayClick={false}
      size="sm"
    >
      <div className="flex flex-col items-center text-center gap-4 py-2">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={stepIndex}
            initial={{ opacity: 0, scale: 0.75, x: 24 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            exit={{ opacity: 0, scale: 0.75, x: -24 }}
            transition={{ type: 'spring', stiffness: 300, damping: 22 }}
            className="flex flex-col items-center text-center gap-4"
          >
            <motion.div
              animate={step.iconAnimate}
              transition={step.iconTransition}
              className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500"
            >
              <Icon className="h-8 w-8 text-white" aria-hidden="true" />
            </motion.div>

            <div>
              <h2 className="text-lg font-bold text-text-primary">{step.title}</h2>
              <p className="mt-2 text-sm text-text-secondary leading-relaxed">{step.description}</p>
            </div>
          </motion.div>
        </AnimatePresence>

        <div className="flex items-center gap-1.5" role="progressbar" aria-valuenow={stepIndex + 1} aria-valuemin={1} aria-valuemax={STEPS.length}>
          {STEPS.map((_, i) => (
            <motion.span
              key={i}
              animate={{ width: i === stepIndex ? 24 : 6 }}
              transition={{ type: 'spring', stiffness: 500, damping: 20 }}
              className={cn(
                'h-1.5 rounded-full',
                i === stepIndex ? 'bg-primary-500' : 'bg-border-primary'
              )}
            />
          ))}
        </div>

        <div className="flex items-center justify-between w-full gap-3 mt-2">
          <button
            onClick={onDone}
            className="text-sm text-text-tertiary hover:text-text-primary transition-colors"
          >
            Skip
          </button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => (isLast ? onDone() : setStepIndex((i) => i + 1))}
          >
            {isLast ? 'Get started' : 'Next'}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
