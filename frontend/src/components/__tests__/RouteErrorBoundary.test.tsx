import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../../test/setup.tsx';
import { RouteErrorBoundary } from '../RouteErrorBoundary';

function Boom(): React.ReactElement {
  throw new Error('render exploded');
}

// The shared helper so the boundary sees the real i18n catalogue and a
// router -- the fallback renders a translated string and a <Link>.
function renderBoundary(children: React.ReactNode, backTo?: string) {
  return renderWithProviders(<RouteErrorBoundary backTo={backTo}>{children}</RouteErrorBoundary>);
}

describe('RouteErrorBoundary', () => {
  let consoleError: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    // React logs the caught error itself; silence it so a passing run is not
    // full of expected stack traces. componentDidCatch's own console.error is
    // asserted below rather than suppressed blindly.
    consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleError.mockRestore();
  });

  it('renders its children when nothing throws', async () => {
    await renderBoundary(<p>all good</p>);
    expect(screen.getByText('all good')).toBeInTheDocument();
    expect(screen.queryByTestId('route-error')).not.toBeInTheDocument();
  });

  it('shows the message and a back link when a child throws', async () => {
    await renderBoundary(<Boom />);

    const fallback = screen.getByTestId('route-error');
    expect(fallback).toBeInTheDocument();
    // role=alert so a screen reader is told, not just sighted users.
    expect(fallback).toHaveAttribute('role', 'alert');
    expect(screen.getByText('This page could not be loaded.')).toBeInTheDocument();

    const back = screen.getByRole('link');
    expect(back).toHaveAttribute('href', '/app/dashboard');
    expect(back).toHaveTextContent(/back/i);
  });

  it('honours a custom back destination', async () => {
    await renderBoundary(<Boom />, '/app/courses');
    expect(screen.getByRole('link')).toHaveAttribute('href', '/app/courses');
  });

  it('keeps the real error reachable in the console', async () => {
    // The fallback deliberately does not show a stack to the user, so without
    // this log the cause would be lost entirely.
    await renderBoundary(<Boom />);
    const logged = consoleError.mock.calls.some((args) =>
      args.some((a) => typeof a === 'string' && a.includes('[RouteErrorBoundary]')),
    );
    expect(logged, 'componentDidCatch should log the error').toBe(true);
  });

  it('a remount clears the error, which is what key={pathname} relies on', async () => {
    // An error boundary holds its error state until it unmounts. Parameterised
    // routes reuse one element instance across param changes, so App.tsx keys
    // the boundary on pathname to force a remount -- without that, one bad
    // lesson would leave every later lesson showing this page.
    const { unmount } = await renderBoundary(<Boom />);
    expect(screen.getByTestId('route-error')).toBeInTheDocument();
    unmount();

    await renderBoundary(<p>next page</p>);
    expect(screen.getByText('next page')).toBeInTheDocument();
    expect(screen.queryByTestId('route-error')).not.toBeInTheDocument();
  });
});
