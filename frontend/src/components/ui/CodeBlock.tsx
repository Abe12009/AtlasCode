import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '../../lib/utils';

interface CodeBlockProps extends Omit<HTMLAttributes<HTMLPreElement>, 'dir' | 'children'> {
  children: ReactNode;
  className?: string;
}

/**
 * Static (non-editable) code display — a starter snippet, a fill-in-the-blank
 * template, a reading-block example.
 *
 * Source code always reads left-to-right, regardless of the surrounding
 * prose's direction: a Python snippet embedded in an Arabic RTL lesson must
 * still look the way it looks in any editor. `dir="ltr"` is what actually
 * fixes this — `text-align: left` alone still leaves the Unicode bidi
 * algorithm free to reorder lines, and a plain `<pre>` with no `dir` of its
 * own inherits `rtl` from `<html dir="rtl">` and visually right-aligns and
 * reverses the code.
 */
export function CodeBlock({ children, className, ...rest }: CodeBlockProps) {
  return (
    <pre
      dir="ltr"
      className={cn(
        'whitespace-pre-wrap overflow-x-auto rounded-xl bg-bg-code p-4 text-left font-mono text-sm text-gray-100',
        className,
      )}
      {...rest}
    >
      {children}
    </pre>
  );
}
