import { forwardRef, type HTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

export interface ProgressBarProps extends HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'accent' | 'success' | 'warning';
  showLabel?: boolean;
  label?: string;
  rounded?: boolean;
}

const sizeStyles = {
  xs: 'h-1',
  sm: 'h-2',
  md: 'h-3',
  lg: 'h-4',
};

const variantStyles = {
  primary: 'bg-primary-500',
  accent: 'bg-accent-500',
  success: 'bg-success-500',
  warning: 'bg-warning-500',
};

const trackStyles = {
  primary: 'bg-primary-900/30',
  accent: 'bg-accent-900/30',
  success: 'bg-success-900/30',
  warning: 'bg-warning-900/30',
};

export const ProgressBar = forwardRef<HTMLDivElement, ProgressBarProps>(
  (
    {
      className,
      value,
      max = 100,
      size = 'md',
      variant = 'primary',
      showLabel = false,
      label,
      rounded = true,
      ...props
    },
    ref,
  ) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

    return (
      <div ref={ref} className={cn('w-full', className)} {...props}>
        <div className={cn(
          'relative overflow-hidden bg-bg-tertiary',
          rounded && 'rounded-full',
          sizeStyles[size]
        )} role="progressbar" aria-valuenow={value} aria-valuemin={0} aria-valuemax={max} aria-label={label}>
          <div
            className={cn(
              'h-full transition-all duration-500 ease-out',
              variantStyles[variant],
              rounded && 'rounded-full'
            )}
            style={{ width: `${percentage}%` }}
          />
        </div>
        {(showLabel || label) && (
          <div className="flex items-center justify-between mt-1.5 text-xs text-text-tertiary">
            {label && <span>{label}</span>}
            {showLabel && <span className="font-mono tabular-nums">{Math.round(percentage)}%</span>}
          </div>
        )}
      </div>
    );
  },
);

ProgressBar.displayName = 'ProgressBar';

export interface CircularProgressProps extends HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  variant?: 'primary' | 'accent' | 'success' | 'warning';
  showValue?: boolean;
  label?: string;
}

const variantCircleStyles = {
  primary: 'text-primary-500',
  accent: 'text-accent-500',
  success: 'text-success-500',
  warning: 'text-warning-500',
};

const trackCircleStyles = {
  primary: 'text-primary-900/30',
  accent: 'text-accent-900/30',
  success: 'text-success-900/30',
  warning: 'text-warning-900/30',
};

export const CircularProgress = forwardRef<HTMLDivElement, CircularProgressProps>(
  (
    {
      className,
      value,
      max = 100,
      size = 48,
      strokeWidth = 4,
      variant = 'primary',
      showValue = true,
      label,
      ...props
    },
    ref,
  ) => {
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percentage / 100) * circumference;

    return (
      <div
        ref={ref}
        className={cn('inline-flex flex-col items-center gap-2', className)}
        {...props}
      >
        <div className="relative" style={{ width: size, height: size }}>
          <svg style={{ width: size, height: size, transform: 'rotate(-90deg)' }}>
            <circle
              className={cn(trackCircleStyles[variant])}
              strokeWidth={strokeWidth}
              stroke="currentColor"
              fill="none"
              r={radius}
              cx={size / 2}
              cy={size / 2}
            />
            <circle
              className={cn(variantCircleStyles[variant], 'transition-all duration-500 ease-out')}
              strokeWidth={strokeWidth}
              stroke="currentColor"
              fill="none"
              strokeLinecap="round"
              r={radius}
              cx={size / 2}
              cy={size / 2}
              style={{
                strokeDasharray: circumference,
                strokeDashoffset: offset,
              }}
            />
          </svg>
          {showValue && (
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="font-mono text-sm font-semibold text-text-primary">
                {Math.round(percentage)}%
              </span>
            </div>
          )}
        </div>
        {label && <span className="text-xs text-text-tertiary text-center">{label}</span>}
      </div>
    );
  },
);

CircularProgress.displayName = 'CircularProgress';