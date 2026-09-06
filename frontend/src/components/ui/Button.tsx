import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react';
import { Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';

export type ButtonVariant =
  | 'primary'
  | 'accent'
  | 'secondary'
  | 'outline'
  | 'ghost'
  | 'destructive'
  | 'success';

export type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  /** Announced while `loading` — falls back to the button's own children. */
  loadingText?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
  fullWidth?: boolean;
}

/**
 * Variants are colour + elevation only; motion, focus and disabled behaviour
 * are shared below so every button in the product feels the same under the
 * hand: a 1px lift on hover, a real press at :active, a visible focus ring for
 * keyboard users, and no movement at all when the user prefers reduced motion.
 */
const variantStyles: Record<ButtonVariant, string> = {
  primary:
    'bg-primary-600 text-white shadow-sm hover:bg-primary-700 hover:shadow-md active:bg-primary-800 focus-visible:ring-primary-500',
  accent:
    'bg-accent-600 text-white shadow-sm hover:bg-accent-700 hover:shadow-md active:bg-accent-800 focus-visible:ring-accent-500',
  secondary:
    'bg-bg-tertiary text-text-primary border border-border-primary hover:bg-bg-quaternary hover:border-border-secondary active:bg-bg-tertiary focus-visible:ring-border-focus',
  outline:
    'border border-border-secondary bg-transparent text-text-primary hover:bg-bg-tertiary hover:border-border-tertiary active:bg-bg-quaternary focus-visible:ring-border-focus',
  ghost:
    'bg-transparent text-text-secondary hover:bg-bg-tertiary hover:text-text-primary active:bg-bg-quaternary focus-visible:ring-border-focus',
  destructive:
    'bg-error-600 text-white shadow-sm hover:bg-error-700 hover:shadow-md active:bg-error-800 focus-visible:ring-error-500',
  success:
    'bg-success-600 text-white shadow-sm hover:bg-success-700 hover:shadow-md active:bg-success-800 focus-visible:ring-success-500',
};

const sizeStyles: Record<ButtonSize, string> = {
  xs: 'h-7 px-2.5 text-xs gap-1.5 rounded-lg',
  sm: 'h-9 px-3 text-sm gap-2 rounded-lg',
  md: 'h-10 px-4 text-sm gap-2 rounded-xl',
  lg: 'h-12 px-5 text-base gap-2.5 rounded-xl',
  xl: 'h-14 px-7 text-base gap-3 rounded-2xl',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      loading = false,
      loadingText,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled,
      children,
      ...props
    },
    ref,
  ) => {
    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        className={cn(
          'relative inline-flex items-center justify-center whitespace-nowrap font-semibold',
          'transition-[background-color,border-color,box-shadow,transform,color] duration-fast',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary',
          'disabled:pointer-events-none disabled:opacity-55 disabled:shadow-none',
          'motion-safe:hover:-translate-y-px motion-safe:active:translate-y-0 motion-safe:active:scale-[0.985]',
          variantStyles[variant],
          sizeStyles[size],
          fullWidth && 'w-full',
          className,
        )}
        disabled={isDisabled}
        aria-busy={loading || undefined}
        {...props}
      >
        {loading ? (
          <>
            <Loader2 className="h-4 w-4 flex-shrink-0 animate-spin" aria-hidden="true" />
            <span>{loadingText ?? children}</span>
          </>
        ) : (
          <>
            {leftIcon && (
              <span className="flex flex-shrink-0 items-center" aria-hidden="true">
                {leftIcon}
              </span>
            )}
            {children != null && children !== false && <span>{children}</span>}
            {rightIcon && (
              <span className="flex flex-shrink-0 items-center" aria-hidden="true">
                {rightIcon}
              </span>
            )}
          </>
        )}
      </button>
    );
  },
);

Button.displayName = 'Button';

export interface IconButtonProps extends Omit<ButtonProps, 'leftIcon' | 'rightIcon' | 'children'> {
  icon: ReactNode;
  /** Required: an icon-only control needs an accessible name. */
  'aria-label': string;
}

const iconSizeStyles: Record<ButtonSize, string> = {
  xs: 'h-7 w-7 rounded-lg',
  sm: 'h-9 w-9 rounded-lg',
  md: 'h-10 w-10 rounded-xl',
  lg: 'h-12 w-12 rounded-xl',
  xl: 'h-14 w-14 rounded-2xl',
};

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ icon, className, size = 'md', variant = 'ghost', ...props }, ref) => (
    <Button
      ref={ref}
      variant={variant}
      size={size}
      className={cn('p-0', iconSizeStyles[size], className)}
      {...props}
    >
      <span className="flex items-center justify-center" aria-hidden="true">
        {icon}
      </span>
    </Button>
  ),
);

IconButton.displayName = 'IconButton';
