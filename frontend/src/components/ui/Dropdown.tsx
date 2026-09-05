import React, { forwardRef, type HTMLAttributes, type ReactNode, useRef, useEffect, useState, createContext, useContext, type MouseEvent } from 'react';
import { cn } from '../../lib/utils';
import { useTranslation } from '../../hooks/useTranslation';

export interface DropdownProps {
  children: ReactNode;
  position?: 'bottom' | 'top' | 'left' | 'right';
  align?: 'start' | 'center' | 'end';
  offset?: number;
}

export interface DropdownItemProps extends HTMLAttributes<HTMLButtonElement> {
  icon?: ReactNode;
  destructive?: boolean;
  close?: () => void;
}

export interface DropdownSeparatorProps extends HTMLAttributes<HTMLHRElement> {}

function getPlacementClasses(position: string, align: string, isRTL: boolean) {
  const positions = {
    bottom: 'top-full mt-2',
    top: 'bottom-full mb-2',
    left: 'right-full mr-2',
    right: 'left-full ml-2',
  };

  const alignments = {
    start: isRTL ? 'right-0' : 'left-0',
    center: 'left-1/2 -translate-x-1/2',
    end: isRTL ? 'left-0' : 'right-0',
  };

  return {
    position: positions[position as keyof typeof positions] || positions.bottom,
    align: alignments[align as keyof typeof alignments] || alignments.start,
  };
}

interface DropdownContextValue {
  close: () => void;
  isOpen: boolean;
}

const DropdownContext = createContext<DropdownContextValue | null>(null);

function DropdownRoot({
  children,
  position = 'bottom',
  align = 'start',
  offset = 8,
}: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [fixedPos, setFixedPos] = useState<{ top: number; left: number } | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const { isRTL } = useTranslation();

  const close = () => setIsOpen(false);
  const open = () => setIsOpen(true);
  const toggle = () => setIsOpen((prev) => !prev);

  // Position the panel with fixed, viewport-relative coordinates computed from the
  // trigger's real position, clamped to stay fully on-screen. The trigger isn't always
  // near the edge it's meant to align to (e.g. a header icon with other icons further
  // out), so a pure CSS right:0/left:0 relative to the trigger can push the panel off
  // either edge of a narrow viewport.
  useEffect(() => {
    if (!isOpen) {
      setFixedPos(null);
      return;
    }
    const trigger = triggerRef.current;
    const panel = panelRef.current;
    if (!trigger || !panel) return;

    const margin = 8;
    const triggerRect = trigger.getBoundingClientRect();
    const panelWidth = panel.offsetWidth;
    const panelHeight = panel.offsetHeight;

    let left = position === 'left' ? triggerRect.left - panelWidth - offset
      : position === 'right' ? triggerRect.right + offset
      : align === 'center' ? triggerRect.left + triggerRect.width / 2 - panelWidth / 2
      : (align === 'end') !== isRTL ? triggerRect.right - panelWidth
      : triggerRect.left;

    let top = position === 'top' ? triggerRect.top - panelHeight - offset
      : position === 'left' || position === 'right' ? triggerRect.top
      : triggerRect.bottom + offset;

    const maxLeft = window.innerWidth - panelWidth - margin;
    left = Math.min(Math.max(left, margin), Math.max(maxLeft, margin));
    const maxTop = window.innerHeight - panelHeight - margin;
    top = Math.min(Math.max(top, margin), Math.max(maxTop, margin));

    setFixedPos({ top, left });
  }, [isOpen, position, align, offset, isRTL]);

  useEffect(() => {
    function handleClickOutside(event: Event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        if (triggerRef.current && !triggerRef.current.contains(event.target as Node)) {
          close();
        }
      }
    }

    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        close();
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen]);

  const placement = getPlacementClasses(position, align, isRTL);

  let triggerFound = false;
  const trigger = React.Children.toArray(children).find((child) => {
    if (!React.isValidElement(child)) return false;
    if (child.type === DropdownItem || child.type === DropdownSeparator) return false;
    return true;
  });

  return (
    <DropdownContext.Provider value={{ close, isOpen }}>
      <div className="relative inline-block" ref={dropdownRef}>
        {React.isValidElement(trigger) && React.cloneElement(trigger as React.ReactElement<any>, {
          ref: triggerRef,
          onClick: (e: MouseEvent<HTMLButtonElement>) => {
            e.stopPropagation();
            toggle();
            (trigger.props as any).onClick?.(e);
          },
          'aria-expanded': isOpen,
          'aria-haspopup': 'true',
        })}

        {isOpen && (
          <div
            ref={panelRef}
            className={cn(
              'z-50 animate-scale-in max-w-[calc(100vw-1rem)]',
              fixedPos ? 'fixed' : cn('absolute invisible', placement.position, placement.align),
            )}
            style={fixedPos ? { top: fixedPos.top, left: fixedPos.left } : undefined}
            role="menu"
          >
            <div className="bg-bg-elevated border border-border-primary rounded-xl shadow-floating py-1 min-w-[160px] max-w-full overflow-hidden overflow-x-auto">
              {React.Children.map(children, (child) => {
                if (!React.isValidElement(child)) return child;
                // Skip the trigger element (rendered separately above) — only the
                // first non-item element is treated as the trigger.
                if (!triggerFound && child.type !== DropdownItem && child.type !== DropdownSeparator) {
                  triggerFound = true;
                  return null;
                }
                if (child.type === DropdownItem || child.type === DropdownSeparator) {
                  return React.cloneElement(child as React.ReactElement<any>, {
                    close,
                  });
                }
                return child;
              })}
            </div>
          </div>
        )}
      </div>
    </DropdownContext.Provider>
  );
}

function useDropdownContext() {
  const context = useContext(DropdownContext);
  if (!context) {
    throw new Error('DropdownItem must be used within a Dropdown');
  }
  return context;
}

export function DropdownItem({
  children,
  icon,
  destructive = false,
  close,
  className,
  onClick,
  ...props
}: DropdownItemProps) {
  const { close: contextClose } = useDropdownContext();
  const handleClose = close || contextClose;

  const handleClick = (e: MouseEvent<HTMLButtonElement>) => {
    onClick?.(e);
    if (!e.defaultPrevented) {
      handleClose();
    }
  };

  return (
    <button
      className={cn(
        'w-full flex items-center gap-3 px-3 py-2 text-sm font-medium text-left transition-colors',
        'hover:bg-bg-tertiary focus:outline-none focus:bg-bg-tertiary',
        destructive
          ? 'text-error-600 dark:text-error-400 hover:bg-error-50 dark:hover:bg-error-900/20'
          : 'text-text-primary',
        className,
      )}
      onClick={handleClick}
      role="menuitem"
      {...props}
    >
      {icon && <span className="flex-shrink-0 h-4 w-4" aria-hidden="true">{icon}</span>}
      <span className="flex-1">{children}</span>
    </button>
  );
}

DropdownItem.displayName = 'DropdownItem';

export function DropdownSeparator({ className, ...props }: DropdownSeparatorProps) {
  return (
    <hr
      className={cn('my-1 border-border-primary', className)}
      role="separator"
      {...props}
    />
  );
}

DropdownSeparator.displayName = 'DropdownSeparator';

export const Dropdown = Object.assign(DropdownRoot, {
  Item: DropdownItem,
  Separator: DropdownSeparator,
});