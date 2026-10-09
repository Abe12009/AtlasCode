import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle } from 'lucide-react';
import { useTranslation } from '../hooks/useTranslation';
import { Button } from './ui';

/**
 * Catches a render throw inside a route and shows a message instead of a
 * blank page.
 *
 * Routes are wrapped in `<Suspense>`, which handles the *loading* half of a
 * lazy import and nothing else -- a component that throws while rendering
 * unmounts the whole tree and leaves a white screen with a 200 status, which
 * is both the worst failure mode for a user and the hardest for a test to
 * notice. Visual Programming hit exactly this: seeded exercises carrying
 * nodes without a `position` threw inside the edge layer.
 *
 * Error boundaries have to be class components; there is no hook equivalent.
 */
interface Props {
  children: ReactNode;
  /** Where "back" goes. Defaults to the dashboard. */
  backTo?: string;
}

interface State {
  error: Error | null;
}

export class RouteErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // Keep the real stack reachable: the fallback deliberately does not show
    // it to the user, so without this the cause would be lost entirely.
    console.error('[RouteErrorBoundary]', error, info.componentStack);
  }

  render() {
    if (this.state.error) {
      return <RouteErrorFallback backTo={this.props.backTo ?? '/app/dashboard'} />;
    }
    return this.props.children;
  }
}

/** Split out so the message can use hooks -- the boundary itself cannot. */
function RouteErrorFallback({ backTo }: { backTo: string }) {
  const { t } = useTranslation();
  return (
    <div
      className="flex min-h-[60vh] flex-col items-center justify-center gap-4 px-4 text-center"
      role="alert"
      data-testid="route-error"
    >
      <div className="rounded-xl bg-error-500/10 p-3 text-error-400">
        <AlertTriangle className="h-7 w-7" aria-hidden="true" />
      </div>
      <p className="text-lg font-semibold text-text-primary">{t('errors.route_failed')}</p>
      <Link to={backTo}>
        <Button variant="secondary">{t('common.back')}</Button>
      </Link>
    </div>
  );
}
