import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';

/** The three settings a user can pick. `system` follows the OS/device theme. */
export type ThemePreference = 'light' | 'dark' | 'system';

/** What is actually painted — `system` is always resolved to one of these. */
export type ResolvedTheme = 'light' | 'dark';

export const THEME_STORAGE_KEY = 'atlascode.theme';

const THEME_PREFERENCES: readonly ThemePreference[] = ['light', 'dark', 'system'];

export function isThemePreference(value: unknown): value is ThemePreference {
  return typeof value === 'string' && (THEME_PREFERENCES as readonly string[]).includes(value);
}

interface ThemeContextValue {
  /** What the user chose: light, dark, or system. */
  preference: ThemePreference;
  /** What that resolves to right now. */
  theme: ResolvedTheme;
  setPreference: (preference: ThemePreference) => void;
  /** Cycles light → dark → system, for a single-button toggle. */
  cyclePreference: () => void;
  preferences: readonly ThemePreference[];
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

function prefersDark(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return true;
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function readStoredPreference(): ThemePreference {
  if (typeof window === 'undefined') return 'system';
  try {
    const stored = window.localStorage.getItem(THEME_STORAGE_KEY);
    if (isThemePreference(stored)) return stored;
  } catch {
    // Private mode / blocked storage: fall through to the default.
  }
  return 'system';
}

export function resolveTheme(preference: ThemePreference, systemIsDark: boolean): ResolvedTheme {
  if (preference === 'system') return systemIsDark ? 'dark' : 'light';
  return preference;
}

/**
 * Writes the resolved theme onto `<html>`.
 *
 * `data-theme` drives every design token (see `index.css`) and the `dark:`
 * Tailwind variant; `color-scheme` makes the browser paint native widgets —
 * scrollbars, form controls, the autofill sheet — in the matching mode.
 */
function applyTheme(theme: ResolvedTheme) {
  if (typeof document === 'undefined') return;
  const root = document.documentElement;
  root.dataset.theme = theme;
  root.style.colorScheme = theme;
}

export function ThemeProvider({
  children,
  /** Test seam: forces a starting preference instead of reading localStorage. */
  initialPreference,
}: {
  children: ReactNode;
  initialPreference?: ThemePreference;
}) {
  const [preference, setPreferenceState] = useState<ThemePreference>(
    () => initialPreference ?? readStoredPreference(),
  );
  const [systemIsDark, setSystemIsDark] = useState<boolean>(prefersDark);

  // Keep following the OS while the preference is `system`. The listener stays
  // attached in every mode so switching back to `system` is already in sync.
  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return;
    const query = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (event: MediaQueryListEvent) => setSystemIsDark(event.matches);

    setSystemIsDark(query.matches);
    // Safari < 14 only has the deprecated addListener/removeListener pair.
    if (typeof query.addEventListener === 'function') {
      query.addEventListener('change', handleChange);
      return () => query.removeEventListener('change', handleChange);
    }
    query.addListener(handleChange);
    return () => query.removeListener(handleChange);
  }, []);

  const theme = resolveTheme(preference, systemIsDark);

  useEffect(() => {
    applyTheme(theme);

    // Some environments (browser extensions and similar page-external
    // scripts) rewrite `data-theme`/`color-scheme` on <html> shortly after
    // load, out from under whatever set it — including our own initial
    // paint. React's state is the source of truth, so if the DOM drifts
    // from the theme this render actually resolved to, put it back rather
    // than silently leaving the page stuck showing the wrong theme.
    if (typeof MutationObserver === 'undefined') return;
    const root = document.documentElement;
    const observer = new MutationObserver(() => {
      if (root.getAttribute('data-theme') !== theme) {
        applyTheme(theme);
      }
    });
    observer.observe(root, { attributes: true, attributeFilter: ['data-theme'] });
    return () => observer.disconnect();
  }, [theme]);

  const setPreference = useCallback((next: ThemePreference) => {
    setPreferenceState(next);
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, next);
    } catch {
      // Persisting is a convenience; the session still switches correctly.
    }
  }, []);

  const cyclePreference = useCallback(() => {
    setPreferenceState((current) => {
      const next =
        THEME_PREFERENCES[(THEME_PREFERENCES.indexOf(current) + 1) % THEME_PREFERENCES.length];
      try {
        window.localStorage.setItem(THEME_STORAGE_KEY, next);
      } catch {
        // See above.
      }
      return next;
    });
  }, []);

  const value = useMemo<ThemeContextValue>(
    () => ({
      preference,
      theme,
      setPreference,
      cyclePreference,
      preferences: THEME_PREFERENCES,
    }),
    [preference, theme, setPreference, cyclePreference],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
