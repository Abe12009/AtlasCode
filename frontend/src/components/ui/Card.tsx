import React, { forwardRef, type HTMLAttributes, type ReactNode } from 'react';
import { cn } from '../../lib/utils';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'outlined' | 'elevated' | 'interactive' | 'filled';
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const variantStyles = {
  // The two inset layers make a surface read as raised without implying it is
  // clickable -- that is `interactive` below, which adds the lift and press.
  default:
    'bg-bg-elevated border border-border-primary shadow-[var(--depth-raise-top),var(--depth-raise-bottom),var(--shadow-card)]',
  outlined: 'bg-bg-elevated border-2 border-border-primary',
  elevated:
    'bg-bg-elevated border border-border-primary shadow-[var(--depth-raise-top),var(--depth-raise-bottom),var(--shadow-elevated)]',
  interactive: cn(
    // `interactive-lift` (index.css) owns the raised-surface shadows, the
    // hover lift and the tap press, so this variant no longer sets its own.
    'bg-bg-elevated border border-border-primary interactive-lift interactive-tilt cursor-pointer',
    // No-op unless a focusable ancestor (e.g. the <Link> a card is wrapped in)
    // carries `group` -- lets a keyboard user see which whole-card link is
    // focused, matching Button's ring treatment.
    'group-focus-visible:outline-none group-focus-visible:ring-2 group-focus-visible:ring-primary-500 group-focus-visible:ring-offset-2 group-focus-visible:ring-offset-bg-primary',
  ),
  filled: 'bg-bg-secondary border border-transparent',
};

const paddingStyles = {
  none: '',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

export const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', padding = 'md', children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'rounded-2xl transition-all duration-normal',
          variantStyles[variant],
          paddingStyles[padding],
          className,
        )}
        {...props}
      >
        {children}
      </div>
    );
  },
);

Card.displayName = 'Card';

export const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('mb-4', className)}
        {...props}
      >
        {children}
      </div>
    );
  },
);

CardHeader.displayName = 'CardHeader';

export const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
  ({ className, children, ...props }, ref) => {
    return (
      <h3
        ref={ref}
        className={cn('text-xl font-semibold text-text-primary tracking-tight', className)}
        {...props}
      >
        {children}
      </h3>
    );
  },
);

CardTitle.displayName = 'CardTitle';

export const CardDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
  ({ className, children, ...props }, ref) => {
    return (
      <p
        ref={ref}
        className={cn('mt-1 text-sm text-text-secondary leading-relaxed', className)}
        {...props}
      >
        {children}
      </p>
    );
  },
);

CardDescription.displayName = 'CardDescription';

export const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('', className)}
        {...props}
      >
        {children}
      </div>
    );
  },
);

CardContent.displayName = 'CardContent';

export const CardFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn('mt-4 flex items-center gap-3', className)}
        {...props}
      >
        {children}
      </div>
    );
  },
);

CardFooter.displayName = 'CardFooter';