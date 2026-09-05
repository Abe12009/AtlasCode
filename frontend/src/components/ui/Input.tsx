import { forwardRef, type InputHTMLAttributes, type TextareaHTMLAttributes, type SelectHTMLAttributes, type ReactNode, useId } from 'react';
import { cn } from '../../lib/utils';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  hint?: string;
  error?: string;
  leftIcon?: ReactNode;
  rightIcon?: ReactNode;
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

    return (
      <div className={cn('w-full', fullWidth && 'w-full')}>
        {label && (
          <label
            htmlFor={id}
            className="block text-sm font-medium text-text-primary mb-1.5"
          >
            {label}
            {required && (
              <span className="text-error-500 ml-0.5" aria-hidden="true">*</span>
            )}
          </label>
        )}
        <div className="relative">
          {leftIcon && (
            <div
              className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-text-tertiary"
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
              'w-full rounded-xl border bg-bg-primary text-text-primary placeholder:text-text-tertiary',
              'transition-all duration-fast',
              'focus:outline-none focus:ring-2 focus:ring-offset-0',
              'disabled:bg-bg-tertiary disabled:text-text-tertiary disabled:cursor-not-allowed',
              'text-sm',
              leftIcon ? 'pl-10' : 'pl-4',
              rightIcon ? 'pr-10' : 'pr-4',
              'py-3',
              error
                ? 'border-error-500 focus:border-error-500 focus:ring-2 focus:ring-error-500/20'
                : 'border-border-primary focus:border-border-focus focus:ring-2 focus:ring-border-focus/20',
              className,
            )}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={
              error ? errorId : hint ? hintId : undefined
            }
            aria-disabled={disabled}
            {...props}
          />
          {rightIcon && (
            <div
              className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none text-text-tertiary"
              aria-hidden="true"
            >
              {rightIcon}
            </div>
          )}
        </div>
        {error && (
          <p
            id={errorId}
            className="mt-1.5 text-sm text-error-600 dark:text-error-400 flex items-center gap-1"
            role="alert"
          >
            <svg className="h-3.5 w-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM8.707 7.293a1 1 0 00-1.414 1.414L10.586 10l-2.879 2.879a1 1 0 101.414 1.414L12 11.414l2.879 2.879a1 1 0 001.414-1.414L13.414 10l2.879-2.879a1 1 0 001.414-1.414L12 8.586 9.121 5.707a1 1 0 00-1.414 0L8 9.586 5.121 6.707a1 1 0 000 1.414L10.586 12l-2.879 2.879a1 1 0 001.414 1.414z" clipRule="evenodd" />
            </svg>
            {error}
          </p>
        )}
        {hint && !error && (
          <p
            id={hintId}
            className="mt-1.5 text-sm text-text-tertiary"
          >
            {hint}
          </p>
        )}
      </div>
    );
  },
);

Input.displayName = 'Input';

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
      <div className={cn('w-full', fullWidth && 'w-full')}>
        {label && (
          <label
            htmlFor={id}
            className="block text-sm font-medium text-text-primary mb-1.5"
          >
            {label}
            {required && (
              <span className="text-error-500 ml-0.5" aria-hidden="true">*</span>
            )}
          </label>
        )}
        <textarea
          ref={ref}
          id={id}
          disabled={disabled}
          required={required}
          rows={rows}
          className={cn(
            'w-full rounded-xl border bg-bg-primary text-text-primary placeholder:text-text-tertiary resize-y',
            'transition-all duration-fast',
            'focus:outline-none focus:ring-2 focus:ring-offset-0',
            'disabled:bg-bg-tertiary disabled:text-text-tertiary disabled:cursor-not-allowed',
            'text-sm p-4',
            error
              ? 'border-error-500 focus:border-error-500 focus:ring-2 focus:ring-error-500/20'
              : 'border-border-primary focus:border-border-focus focus:ring-2 focus:ring-border-focus/20',
            className,
          )}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={
            error ? errorId : hint ? hintId : undefined
          }
          aria-disabled={disabled}
          {...props}
        />
        {error && (
          <p
            id={errorId}
            className="mt-1.5 text-sm text-error-600 dark:text-error-400 flex items-center gap-1"
            role="alert"
          >
            <svg className="h-3.5 w-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM8.707 7.293a1 1 0 00-1.414 1.414L10.586 10l-2.879 2.879a1 1 0 101.414 1.414L12 11.414l2.879 2.879a1 1 0 001.414-1.414L13.414 10l2.879-2.879a1 1 0 001.414-1.414L12 8.586 9.121 5.707a1 1 0 00-1.414 0L8 9.586 5.121 6.707a1 1 0 000 1.414L10.586 12l-2.879 2.879a1 1 0 001.414 1.414z" clipRule="evenodd" />
            </svg>
            {error}
          </p>
        )}
        {hint && !error && (
          <p
            id={hintId}
            className="mt-1.5 text-sm text-text-tertiary"
          >
            {hint}
          </p>
        )}
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
      <div className={cn('w-full', fullWidth && 'w-full')}>
        {label && (
          <label
            htmlFor={id}
            className="block text-sm font-medium text-text-primary mb-1.5"
          >
            {label}
            {required && (
              <span className="text-error-500 ml-0.5" aria-hidden="true">*</span>
            )}
          </label>
        )}
        <div className="relative">
          <select
            ref={ref}
            id={id}
            disabled={disabled}
            required={required}
            className={cn(
              'w-full rounded-xl border bg-bg-primary text-text-primary',
              'transition-all duration-fast appearance-none',
              'focus:outline-none focus:ring-2 focus:ring-offset-0',
              'disabled:bg-bg-tertiary disabled:text-text-tertiary disabled:cursor-not-allowed',
              'text-sm pl-4 pr-10 py-3',
              error
                ? 'border-error-500 focus:border-error-500 focus:ring-2 focus:ring-error-500/20'
                : 'border-border-primary focus:border-border-focus focus:ring-2 focus:ring-border-focus/20',
              className,
            )}
            aria-invalid={error ? 'true' : 'false'}
            aria-describedby={
              error ? errorId : hint ? hintId : undefined
            }
            aria-disabled={disabled}
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
          <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none text-text-tertiary" aria-hidden="true">
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
        {error && (
          <p
            id={errorId}
            className="mt-1.5 text-sm text-error-600 dark:text-error-400 flex items-center gap-1"
            role="alert"
          >
            <svg className="h-3.5 w-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM8.707 7.293a1 1 0 00-1.414 1.414L10.586 10l-2.879 2.879a1 1 0 101.414 1.414L12 11.414l2.879 2.879a1 1 0 001.414-1.414L13.414 10l2.879-2.879a1 1 0 001.414-1.414L12 8.586 9.121 5.707a1 1 0 00-1.414 0L8 9.586 5.121 6.707a1 1 0 000 1.414L10.586 12l-2.879 2.879a1 1 0 001.414 1.414z" clipRule="evenodd" />
            </svg>
            {error}
          </p>
        )}
        {hint && !error && (
          <p
            id={hintId}
            className="mt-1.5 text-sm text-text-tertiary"
          >
            {hint}
          </p>
        )}
      </div>
    );
  },
);

Select.displayName = 'Select';