import React, { type HTMLAttributes, type ReactNode, useRef, useEffect, useState } from 'react';
import { cn } from '../../lib/utils';

export interface DropdownProps {
  children: ReactNode;
  content?: ReactNode;
  position?: 'bottom' | 'top' | 'left' | 'right';
  align?: 'start' | 'center' | 'end';
  offset?: number;
}

export function Dropdown({ children, content, position = 'bottom', align = 'start', offset = 8 }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const triggerRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        triggerRef.current &&
        !triggerRef.current.contains(event.target as Node) &&
        contentRef.current &&
        !contentRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen]);

  const positionStyles = {
    bottom: 'top-full',
    top: 'bottom-full',
    left: 'right-full',
    right: 'left-full',
  };

  const alignStyles = {
    start: 'left-0',
    center: 'left-1/2 -translate-x-1/2',
    end: 'right-0',
  };

  return (
    <div className="relative inline-block" ref={triggerRef}>
      <div
        onClick={() => setIsOpen(!isOpen)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            setIsOpen(!isOpen);
          }
        }}
        tabIndex={0}
        role="button"
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        {children}
      </div>

      {isOpen && (
        <div
          ref={contentRef}
          className={cn(
            'fixed z-50 mt-1.5 min-w-[160px] bg-bg-primary border border-border-primary rounded-lg shadow-dropdown',
            'animate-fade-in',
            positionStyles[position],
            alignStyles[align],
          )}
          role="menu"
        >
          <div className="py-1" role="none">{content}</div>
        </div>
      )}
    </div>
  );
}

export interface DropdownItemProps extends HTMLAttributes<HTMLButtonElement> {
  icon?: ReactNode;
  shortcut?: string;
  destructive?: boolean;
  disabled?: boolean;
}

export function DropdownItem({
  className,
  icon,
  shortcut,
  destructive = false,
  disabled = false,
  children,
  onClick,
  ...props
}: DropdownItemProps) {
  return (
    <button
      type="button"
      className={cn(
        'w-full flex items-center gap-3 px-3 py-2 text-sm font-medium transition-colors',
        'rounded-none',
        'focus:outline-none focus:bg-bg-tertiary',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        destructive
          ? 'text-error-600 dark:text-error-400 hover:bg-error-50 dark:hover:bg-error-900/20'
          : 'text-text-primary hover:bg-bg-tertiary',
        className,
      )}
      disabled={disabled}
      onClick={(e) => {
        if (!disabled && onClick) onClick(e);
      }}
      role="menuitem"
      tabIndex={-1}
      {...props}
    >
      {icon && <span className="flex-shrink-0 h-4 w-4" aria-hidden="true">{icon}</span>}
      <span className="flex-1 text-left">{children}</span>
      {shortcut && (
        <span className="flex-shrink-0 text-xs text-text-tertiary font-normal">{shortcut}</span>
      )}
    </button>
  );
}

export function DropdownSeparator() {
  return (
    <hr className="my-1 border-border-primary" role="separator" />
  );
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  description?: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  showCloseButton?: boolean;
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
}

const modalSizes = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-xl',
  full: 'max-w-4xl',
};

export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  size = 'md',
  showCloseButton = true,
  closeOnOverlayClick = true,
  closeOnEscape = true,
}: ModalProps) {
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsMounted(true);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (closeOnOverlayClick && e.target === e.currentTarget) {
      onClose();
    }
  };

  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (closeOnEscape && event.key === 'Escape') {
        onClose();
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
    }
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeOnEscape, onClose]);

  if (!isOpen && !isMounted) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in"
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
      aria-describedby={description ? 'modal-description' : undefined}
    >
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm animate-fade-in"
        aria-hidden="true"
        onClick={handleOverlayClick}
      />
      <div
        className={cn(
          'glass-strong relative w-full rounded-xl shadow-modal',
          'animate-scale-in',
          'max-h-[90vh] flex flex-col',
          modalSizes[size],
        )}
        role="document"
      >
        {(title || showCloseButton) && (
          <div className="flex items-start justify-between p-4 border-b border-border-primary">
            <div className="flex-1 min-w-0">
              {title && (
                <h2 id="modal-title" className="text-lg font-semibold text-text-primary">
                  {title}
                </h2>
              )}
              {description && (
                <p id="modal-description" className="mt-1 text-sm text-text-secondary">
                  {description}
                </p>
              )}
            </div>
            {showCloseButton && (
              <button
                onClick={onClose}
                className="flex-shrink-0 p-1.5 rounded-lg text-text-tertiary hover:text-text-primary hover:bg-bg-tertiary transition-colors"
                aria-label="Close modal"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            )}
          </div>
        )}
        <div className="flex-1 overflow-y-auto p-4">
          {children}
        </div>
      </div>
    </div>
  );
}

export interface TabsProps {
  defaultValue: string;
  value?: string;
  onValueChange?: (value: string) => void;
  children: ReactNode;
  orientation?: 'horizontal' | 'vertical';
  variant?: 'default' | 'pills' | 'underline';
}

export function Tabs({
  defaultValue,
  value,
  onValueChange,
  children,
  orientation = 'horizontal',
  variant = 'default',
}: TabsProps) {
  const [activeValue, setActiveValue] = useState(value || defaultValue);

  const handleValueChange = (newValue: string) => {
    setActiveValue(newValue);
    onValueChange?.(newValue);
  };

  const controlled = value !== undefined;
  const currentValue = controlled ? value : activeValue;

  const variantStyles = {
    default: '',
    pills: 'bg-bg-tertiary p-1 rounded-lg',
    underline: 'border-b border-border-primary',
  };

  const isTabTrigger = (child: ReactNode): child is React.ReactElement<TabTriggerProps> => {
    return React.isValidElement(child) && child.type === TabTrigger;
  };

  const isTabContent = (child: ReactNode): child is React.ReactElement<TabContentProps> => {
    return React.isValidElement(child) && child.type === TabContent;
  };

  return (
    <div className="w-full" data-orientation={orientation}>
      <div
        className={cn(
          'flex gap-1',
          variantStyles[variant],
          orientation === 'vertical' && 'flex-col',
        )}
        role="tablist"
        aria-orientation={orientation}
      >
        {React.Children.map(children, (child) => {
          if (!isTabTrigger(child)) {
            return child;
          }
          return React.cloneElement(child, {
            value: child.props.value,
            isActive: child.props.value === currentValue,
            onClick: () => handleValueChange(child.props.value),
          });
        })}
      </div>
      <div className="mt-4" role="tabpanel">
        {React.Children.map(children, (child) => {
          if (!isTabContent(child)) {
            return child;
          }
          return React.cloneElement(child, {
            value: child.props.value,
            isActive: child.props.value === currentValue,
          });
        })}
      </div>
    </div>
  );
}

export interface TabTriggerProps extends HTMLAttributes<HTMLButtonElement> {
  value: string;
  isActive?: boolean;
  disabled?: boolean;
}

export function TabTrigger({
  className,
  value,
  isActive = false,
  disabled = false,
  children,
  onClick,
  ...props
}: TabTriggerProps) {
  return (
    <button
      type="button"
      role="tab"
      aria-selected={isActive}
      aria-controls={`panel-${value}`}
      id={`tab-${value}`}
      disabled={disabled}
      onClick={(e) => {
        if (!disabled && onClick) onClick(e);
      }}
      className={cn(
        'inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-lg transition-colors',
        'focus:outline-none focus:ring-2 focus:ring-border-focus/20',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        isActive
          ? 'bg-bg-primary text-text-primary shadow-sm'
          : 'text-text-secondary hover:text-text-primary hover:bg-bg-tertiary',
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}

export interface TabContentProps extends HTMLAttributes<HTMLDivElement> {
  value: string;
  isActive?: boolean;
}

export function TabContent({
  className,
  value,
  isActive = false,
  children,
  ...props
}: TabContentProps) {
  if (!isActive) return null;

  return (
    <div
      role="tabpanel"
      id={`panel-${value}`}
      aria-labelledby={`tab-${value}`}
      className={cn('animate-fade-in', className)}
      {...props}
    >
      {children}
    </div>
  );
}