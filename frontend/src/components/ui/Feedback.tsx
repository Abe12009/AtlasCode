import React, { type HTMLAttributes, type ReactNode, useRef } from 'react';
import { cn } from '../../lib/utils';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'error' | 'neutral' | 'outline';
  size?: 'xs' | 'sm' | 'md' | 'lg';
  dot?: boolean;
  dotColor?: 'primary' | 'success' | 'warning' | 'error' | 'neutral';
}

const variantStyles = {
  default: 'bg-accent-primary-light text-accent-primary dark:bg-accent-primary/20 dark:text-accent-primary-light',
  primary: 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-300',
  success: 'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-300',
  warning: 'bg-warning-100 text-warning-700 dark:bg-warning-900/30 dark:text-warning-300',
  error: 'bg-error-100 text-error-700 dark:bg-error-900/30 dark:text-error-300',
  neutral: 'bg-neutral-100 text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300',
  outline: 'bg-transparent border border-border-primary text-text-secondary',
};

const sizeStyles = {
  xs: 'px-1.5 py-0.5 text-xs',
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
  lg: 'px-3 py-1 text-sm',
};

const dotColors = {
  primary: 'bg-primary-500',
  success: 'bg-success-500',
  warning: 'bg-warning-500',
  error: 'bg-error-500',
  neutral: 'bg-neutral-500',
};

export function Badge({
  className,
  variant = 'default',
  size = 'md',
  dot = false,
  dotColor = 'primary',
  children,
  ...props
}: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 font-medium rounded-full',
        variantStyles[variant],
        sizeStyles[size],
        className,
      )}
      {...props}
    >
      {dot && (
        <span
          className={cn(
            'w-1.5 h-1.5 rounded-full flex-shrink-0',
            dotColors[dotColor],
          )}
          aria-hidden="true"
        />
      )}
      {children}
    </span>
  );
}

export interface AvatarProps extends HTMLAttributes<HTMLDivElement> {
  src?: string;
  alt?: string;
  name?: string;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  shape?: 'circle' | 'square';
}

const avatarSizes = {
  xs: 'h-5 w-5 text-xs',
  sm: 'h-8 w-8 text-sm',
  md: 'h-10 w-10 text-base',
  lg: 'h-12 w-12 text-lg',
  xl: 'h-16 w-16 text-xl',
  '2xl': 'h-20 w-20 text-2xl',
};

export function Avatar({
  className,
  src,
  alt,
  name,
  size = 'md',
  shape = 'circle',
  ...props
}: AvatarProps) {
  const initials = name
    ?.split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  const shapeClass = shape === 'circle' ? 'rounded-full' : 'rounded-xl';

  return (
    <div
      className={cn(
        'inline-flex items-center justify-center font-medium bg-accent-primary-light text-accent-primary',
        'dark:bg-accent-primary/20 dark:text-accent-primary-light',
        avatarSizes[size],
        shapeClass,
        'overflow-hidden bg-neutral-100 dark:bg-neutral-800',
        className,
      )}
      {...props}
    >
      {src ? (
        <img
          src={src}
          alt={alt || name || 'Avatar'}
          className="h-full w-full object-cover"
        />
      ) : (
        <span aria-hidden="true">{initials}</span>
      )}
    </div>
  );
}

export interface ProgressProps extends HTMLAttributes<HTMLDivElement> {
  value: number;
  max?: number;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  variant?: 'default' | 'primary' | 'accent' | 'success' | 'warning' | 'error';
  showLabel?: boolean;
  label?: string;
  animated?: boolean;
}

const progressSizes = {
  xs: 'h-1',
  sm: 'h-1.5',
  md: 'h-2',
  lg: 'h-3',
};

const progressVariants = {
  default: 'bg-accent-primary',
  primary: 'bg-primary-500',
  accent: 'bg-accent-500',
  success: 'bg-success-500',
  warning: 'bg-warning-500',
  error: 'bg-error-500',
};

export function Progress({
  className,
  value,
  max = 100,
  size = 'md',
  variant = 'default',
  showLabel = false,
  label,
  animated = false,
  ...props
}: ProgressProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  return (
    <div className={cn('w-full', className)} {...props}>
      {(showLabel || label) && (
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-sm font-medium text-text-primary">
            {label || `${Math.round(percentage)}%`}
          </span>
          {showLabel && (
            <span className="text-sm text-text-tertiary tabular-nums">
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}
      <div
        className={cn(
          'relative w-full overflow-hidden bg-bg-tertiary rounded-full',
          progressSizes[size],
        )}
        role="progressbar"
        aria-valuenow={Math.round(percentage)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={label || 'Progress'}
      >
        <div
          className={cn(
            'h-full rounded-full transition-all duration-500 ease-out',
            progressVariants[variant],
            animated && 'animate-pulse',
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export interface DividerProps extends HTMLAttributes<HTMLHRElement> {
  orientation?: 'horizontal' | 'vertical';
  variant?: 'default' | 'dashed' | 'dotted';
  label?: ReactNode;
}

const dividerVariants = {
  default: 'border-border-primary',
  dashed: 'border-border-primary border-dashed',
  dotted: 'border-border-primary border-dotted',
};

export function Divider({
  className,
  orientation = 'horizontal',
  variant = 'default',
  label,
  ...props
}: DividerProps) {
  if (orientation === 'vertical') {
    return (
      <hr
        className={cn(
          'h-full w-px',
          dividerVariants[variant],
          className,
        )}
        aria-orientation="vertical"
        {...props}
      />
    );
  }

  if (label) {
    return (
      <div className={cn('flex items-center gap-4', className)} role="separator" {...props}>
        <hr className={cn('flex-1 border-0', dividerVariants[variant])} />
        <span className="text-sm font-medium text-text-tertiary whitespace-nowrap flex-shrink-0">
          {label}
        </span>
        <hr className={cn('flex-1 border-0', dividerVariants[variant])} />
      </div>
    );
  }

  return (
    <hr
      className={cn('border-0', dividerVariants[variant], className)}
      role="separator"
      {...props}
    />
  );
}

export interface LabelProps extends HTMLAttributes<HTMLLabelElement> {
  required?: boolean;
  htmlFor?: string;
}

export function Label({
  className,
  required,
  children,
  ...props
}: LabelProps) {
  return (
    <label
      className={cn(
        'block text-sm font-medium text-text-primary',
        className,
      )}
      {...props}
    >
      {children}
      {required && (
        <span className="text-error-500 ml-0.5" aria-hidden="true">*</span>
      )}
    </label>
  );
}

export interface TooltipProps {
  content: ReactNode;
  children: ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  delay?: number;
}

export function Tooltip({
  content,
  children,
  position = 'top',
  delay = 200,
}: TooltipProps) {
  const [isVisible, setIsVisible] = React.useState<boolean>(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const showTooltip = () => {
    timeoutRef.current = setTimeout(() => setIsVisible(true), delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    setIsVisible(false);
  };

  const positionStyles = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  const arrowStyles = {
    top: 'top-full left-1/2 -translate-x-1/2 border-t-[5px] border-transparent border-t-bg-inverse',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-[5px] border-transparent border-b-bg-inverse',
    left: 'left-full top-1/2 -translate-y-1/2 border-l-[5px] border-transparent border-l-bg-inverse',
    right: 'right-full top-1/2 -translate-y-1/2 border-r-[5px] border-transparent border-r-bg-inverse',
  };

  return (
    <div
      className="relative inline-flex"
      onMouseEnter={showTooltip}
      onMouseLeave={hideTooltip}
      onFocus={showTooltip}
      onBlur={hideTooltip}
    >
      {children}
      {isVisible && (
        <div
          className={cn(
            'fixed z-50 px-3 py-2 text-xs font-medium text-bg-inverse bg-text-primary rounded-lg shadow-lg',
            'animate-fade-in',
            'whitespace-nowrap',
            positionStyles[position],
          )}
          role="tooltip"
        >
          {content}
          <div
            className={cn(
              'absolute w-0 h-0 border-2.5 border-solid',
              arrowStyles[position],
            )}
            aria-hidden="true"
          />
        </div>
      )}
    </div>
  );
}

export interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

const emptyStateSizes = {
  sm: 'py-8 px-4',
  md: 'py-12 px-6',
  lg: 'py-16 px-8',
};

export function EmptyState({
  icon,
  title,
  description,
  action,
  size = 'md',
}: EmptyStateProps) {
  return (
    <div className={cn('text-center', emptyStateSizes[size])}>
      {icon && (
        <div className="mx-auto mb-4 text-text-tertiary">
          {icon}
        </div>
      )}
      <h3 className="text-lg font-semibold text-text-primary mb-2">{title}</h3>
      {description && (
        <p className="text-text-secondary mb-6 max-w-sm mx-auto">{description}</p>
      )}
      {action && (
        <div className="flex items-center justify-center gap-3">{action}</div>
      )}
    </div>
  );
}

export interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  dismissible?: boolean;
  onDismiss?: () => void;
}

const alertVariants = {
  info: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200',
  success: 'bg-success-50 dark:bg-success-900/20 border-success-200 dark:border-success-800 text-success-800 dark:text-success-200',
  warning: 'bg-warning-50 dark:bg-warning-900/20 border-warning-200 dark:border-warning-800 text-warning-800 dark:text-warning-200',
  error: 'bg-error-50 dark:bg-error-900/20 border-error-200 dark:border-error-800 text-error-800 dark:text-error-200',
};

export function Alert({
  className,
  variant = 'info',
  title,
  dismissible = false,
  onDismiss,
  children,
  ...props
}: AlertProps) {
  return (
    <div
      className={cn(
        'flex items-start gap-3 p-4 rounded-xl border',
        alertVariants[variant],
        className,
      )}
      role="alert"
      {...props}
    >
      <div className="flex-1 min-w-0">
        {title && (
          <h4 className="font-semibold text-text-primary mb-1">{title}</h4>
        )}
        <div className="text-sm text-text-secondary">{children}</div>
      </div>
      {dismissible && onDismiss && (
        <button
          onClick={onDismiss}
          className="flex-shrink-0 p-1 rounded hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
          aria-label="Dismiss"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  );
}