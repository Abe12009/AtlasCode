import {
  forwardRef,
  useId,
  useState,
  type InputHTMLAttributes,
  type ReactNode,
  type SelectHTMLAttributes,
  type TextareaHTMLAttributes,
} from 'react';
import { AlertCircle, Eye, EyeOff } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useTranslation } from '../../hooks/useTranslation';

/**
 * Shared field chrome. Every control below renders the same label / hint /
 * error scaffolding so forms stay consistent and every message is wired to its
 * input through `aria-describedby`.
 */
function FieldLabel({
  htmlFor,
  children,
  required,
}: {
  htmlFor: string;
  children: ReactNode;
  required?: boolean;
}) {
  return (
    <label htmlFor={htmlFor} className="mb-1.5 block text-sm font-medium text-text-primary">
      {children}
      {required && (
        <span className="ms-0.5 text-error-500" aria-hidden="true">
          *
        </span>
      )}
    </label>
  );
}

function FieldMessages({
  error,
  hint,
  errorId,
  hintId,
}: {
  error?: string;
  hint?: string;
  errorId: string;
  hintId: string;
}) {
  if (error) {
    return (
      <p
        id={errorId}
        className="mt-1.5 flex items-start gap-1.5 text-sm text-error-600 dark:text-error-400"
        role="alert"
      >
        <AlertCircle className="mt-0.5 h-3.5 w-3.5 flex-shrink-0" aria-hidden="true" />
        <span>{error}</span>
      </p>
    );
  }
  if (hint) {
    return (
      <p id={hintId} className="mt-1.5 text-sm text-text-tertiary">
        {hint}
      </p>
    );
  }
  return null;
}

/** The control styling shared by input / textarea / select. */
const controlBase = [
  'w-full rounded-xl border bg-bg-primary text-text-primary placeholder:text-text-tertiary',
  'transition-[border-color,box-shadow,background-color] duration-fast',
  'focus:outline-none focus:ring-2 focus:ring-offset-0',
  'disabled:bg-bg-tertiary disabled:text-text-tertiary disabled:cursor-not-allowed disabled:opacity-70',
  'text-sm',
].join(' ');

function controlState(hasError: boolean) {
  return hasError
    ? 'border-error-500 focus:border-error-500 focus:ring-error-500/25'
    : 'border-border-primary hover:border-border-secondary focus:border-border-focus focus:ring-border-focus/25';
}

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
  /** Decorative icon rendered at the start of the field. */
  leftIcon?: ReactNode;
  /** Decorative icon rendered at the end of the field. */
  rightIcon?: ReactNode;
  /**
   * Interactive control rendered at the end of the field (a visibility toggle,
   * a clear button…). Unlike `rightIcon` it receives pointer and keyboard
   * events and is exposed to assistive technology.
   */
  rightAddon?: ReactNode;
  fullWidth?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      className,
      label,
      hint,
      error,
      leftIcon,
      rightIcon,
      rightAddon,
      fullWidth = true,
      id: providedId,
      disabled,
      required,
      type = 'text',
      ...props
    },
    ref,
  ) => {
    const generatedId = useId();
    const id = providedId || generatedId;
    const hintId = `${id}-hint`;
    const errorId = `${id}-error`;
    const hasEndSlot = Boolean(rightIcon || rightAddon);

    return (
      <div className={cn(fullWidth ? 'w-full' : 'w-auto')}>
        {label && (
          <FieldLabel htmlFor={id} required={required}>
            {label}
          </FieldLabel>
        )}
        <div className="relative">
          {leftIcon && (
            <div
              className="pointer-events-none absolute inset-y-0 start-0 flex items-center ps-3 text-text-tertiary"
              aria-hidden="true"
            >
              {leftIcon}
            </div>
          )}
          <input
            ref={ref}
            id={id}
            type={type}
            disabled={disabled}
            required={required}
            className={cn(
              controlBase,
              controlState(Boolean(error)),
              'py-3',
              leftIcon ? 'ps-10' : 'ps-4',
              hasEndSlot ? 'pe-11' : 'pe-4',
              className,
            )}
            aria-invalid={error ? 'true' : undefined}
            aria-describedby={error ? errorId : hint ? hintId : undefined}
            {...props}
          />
          {rightAddon && (
            <div className="absolute inset-y-0 end-0 flex items-center pe-2">{rightAddon}</div>
          )}
          {!rightAddon && rightIcon && (
            <div
              className="pointer-events-none absolute inset-y-0 end-0 flex items-center pe-3 text-text-tertiary"
              aria-hidden="true"
            >
              {rightIcon}
            </div>
          )}
        </div>
        <FieldMessages error={error} hint={hint} errorId={errorId} hintId={hintId} />
      </div>
    );
  },
);

Input.displayName = 'Input';

export type PasswordInputProps = Omit<InputProps, 'type' | 'rightAddon' | 'rightIcon'>;

/**
 * Password field with a working reveal toggle.
 *
 * Every auth form uses this rather than hand-rolling a toggle, so the
 * behaviour — hidden by default, real `<button>` that is reachable by keyboard,
 * icon and `aria-pressed` both reflecting the state — is identical everywhere.
 */
export const PasswordInput = forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ disabled, ...props }, ref) => {
    const [visible, setVisible] = useState(false);
    const { t } = useTranslation();
    const label = visible ? t('accessibility.hide_password') : t('accessibility.show_password');

    return (
      <Input
        ref={ref}
        type={visible ? 'text' : 'password'}
        disabled={disabled}
        rightAddon={
          <button
            type="button"
            onClick={() => setVisible((current) => !current)}
            disabled={disabled}
            aria-label={label}
            aria-pressed={visible}
            title={label}
            className={cn(
              'inline-flex h-8 w-8 items-center justify-center rounded-lg text-text-tertiary',
              'transition-colors duration-fast hover:bg-bg-tertiary hover:text-text-primary',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus',
              'disabled:cursor-not-allowed disabled:opacity-50',
            )}
          >
            {visible ? (
              <EyeOff className="h-4 w-4" aria-hidden="true" />
            ) : (
              <Eye className="h-4 w-4" aria-hidden="true" />
            )}
          </button>
        }
        {...props}
      />
    );
  },
);

PasswordInput.displayName = 'PasswordInput';

export interface TextareaProps extends Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'type'> {
  label?: string;
  hint?: string;
  error?: string;
  fullWidth?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  (
    {
      className,
      label,
      hint,
      error,
      fullWidth = true,
      id: providedId,
      disabled,
      required,
      rows = 4,
      ...props
    },
    ref,
  ) => {
    const generatedId = useId();
    const id = providedId || generatedId;
    const hintId = `${id}-hint`;
    const errorId = `${id}-error`;

    return (
      <div className={cn(fullWidth ? 'w-full' : 'w-auto')}>
        {label && (
          <FieldLabel htmlFor={id} required={required}>
            {label}
          </FieldLabel>
        )}
        <textarea
          ref={ref}
          id={id}
          disabled={disabled}
          required={required}
          rows={rows}
          className={cn(controlBase, controlState(Boolean(error)), 'resize-y p-4', className)}
          aria-invalid={error ? 'true' : undefined}
          aria-describedby={error ? errorId : hint ? hintId : undefined}
          {...props}
        />
        <FieldMessages error={error} hint={hint} errorId={errorId} hintId={hintId} />
      </div>
    );
  },
);

Textarea.displayName = 'Textarea';

export interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'children'> {
  label?: string;
  hint?: string;
  error?: string;
  options: { value: string; label: string }[];
  placeholder?: string;
  fullWidth?: boolean;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  (
    {
      className,
      label,
      hint,
      error,
      options,
      placeholder,
      fullWidth = true,
      id: providedId,
      disabled,
      required,
      ...props
    },
    ref,
  ) => {
    const generatedId = useId();
    const id = providedId || generatedId;
    const hintId = `${id}-hint`;
    const errorId = `${id}-error`;

    return (
      <div className={cn(fullWidth ? 'w-full' : 'w-auto')}>
        {label && (
          <FieldLabel htmlFor={id} required={required}>
            {label}
          </FieldLabel>
        )}
        <div className="relative">
          <select
            ref={ref}
            id={id}
            disabled={disabled}
            required={required}
            className={cn(
              controlBase,
              controlState(Boolean(error)),
              'appearance-none py-3 ps-4 pe-10',
              className,
            )}
            aria-invalid={error ? 'true' : undefined}
            aria-describedby={error ? errorId : hint ? hintId : undefined}
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <div
            className="pointer-events-none absolute inset-y-0 end-0 flex items-center pe-3 text-text-tertiary"
            aria-hidden="true"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
        <FieldMessages error={error} hint={hint} errorId={errorId} hintId={hintId} />
      </div>
    );
  },
);

Select.displayName = 'Select';

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label: ReactNode;
  hint?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, hint, id: providedId, disabled, ...props }, ref) => {
    const generatedId = useId();
    const id = providedId || generatedId;
    const hintId = `${id}-hint`;

    return (
      <div className="flex items-start gap-2.5">
        <input
          ref={ref}
          id={id}
          type="checkbox"
          disabled={disabled}
          aria-describedby={hint ? hintId : undefined}
          className={cn(
            'mt-0.5 h-4 w-4 flex-shrink-0 rounded border-border-secondary bg-bg-primary',
            'accent-primary-600 cursor-pointer',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus focus-visible:ring-offset-2 focus-visible:ring-offset-bg-primary',
            'disabled:cursor-not-allowed disabled:opacity-60',
            className,
          )}
          {...props}
        />
        <div className="min-w-0">
          <label
            htmlFor={id}
            className={cn(
              'text-sm text-text-secondary',
              disabled ? 'cursor-not-allowed opacity-70' : 'cursor-pointer',
            )}
          >
            {label}
          </label>
          {hint && (
            <p id={hintId} className="mt-0.5 text-xs text-text-tertiary">
              {hint}
            </p>
          )}
        </div>
      </div>
    );
  },
);

Checkbox.displayName = 'Checkbox';
