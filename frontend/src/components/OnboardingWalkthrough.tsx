import { useState } from 'react';
import { Bot, Map, Zap, Palette, MessageCircle } from 'lucide-react';
import { Button, Modal, cn } from './ui';

interface Step {
  icon: typeof Bot;
  title: string;
  description: string;
}

const STEPS: Step[] = [
  {
    icon: Bot,
    title: "Hey, I'm Cody!",
    description: "I'm your computer science companion here on AtlasCode. Let me show you around in a few quick steps.",
  },
  {
    icon: Map,
    title: 'Your learning roadmap',
    description: 'Courses are organized into a roadmap you work through step by step — each one unlocks the next as you go.',
  },
  {
    icon: Zap,
    title: 'XP and streaks',
    description: "Finish lessons to earn XP and level up. Show up daily to build a streak — you'll see both at the top of every page.",
  },
  {
    icon: Palette,
    title: 'Make it yours',
    description: 'Head to your profile anytime to build a custom avatar or upload your own photo.',
  },
  {
    icon: MessageCircle,
    title: "I'm always nearby",
    description: "Click my bubble in the corner whenever you're stuck on something — I can answer CS questions and suggest what to learn next.",
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
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-500 to-accent-500">
          <Icon className="h-8 w-8 text-white" aria-hidden="true" />
        </div>

        <div>
          <h2 className="text-lg font-bold text-text-primary">{step.title}</h2>
          <p className="mt-2 text-sm text-text-secondary leading-relaxed">{step.description}</p>
        </div>

        <div className="flex items-center gap-1.5" role="progressbar" aria-valuenow={stepIndex + 1} aria-valuemin={1} aria-valuemax={STEPS.length}>
          {STEPS.map((_, i) => (
            <span
              key={i}
              className={cn(
                'h-1.5 rounded-full transition-all duration-normal',
                i === stepIndex ? 'w-6 bg-primary-500' : 'w-1.5 bg-border-primary'
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
