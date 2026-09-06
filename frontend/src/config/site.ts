/**
 * Central, environment-driven site configuration.
 *
 * Everything here is public information that ships in the client bundle. Never
 * put secrets in this file — read them from the backend instead.
 *
 * Each value falls back to a safe default so the app runs with no `.env` at
 * all; deployments override them through Vite env vars (see `.env.example`).
 */

function env(key: string): string | undefined {
  const value = (import.meta.env as Record<string, string | undefined>)[key];
  const trimmed = value?.trim();
  return trimmed ? trimmed : undefined;
}

/**
 * Social destinations shown in the landing footer.
 *
 * These are placeholders until the real AtlasCode accounts exist. Point them at
 * the real profiles either by editing this object or, preferably, by setting
 * `VITE_SOCIAL_INSTAGRAM` / `VITE_SOCIAL_X` / `VITE_SOCIAL_GITHUB` at build time.
 */
export const SOCIAL_LINKS = {
  instagram: env('VITE_SOCIAL_INSTAGRAM') ?? 'https://instagram.com/',
  x: env('VITE_SOCIAL_X') ?? 'https://x.com/',
  github: env('VITE_SOCIAL_GITHUB') ?? 'https://github.com/',
} as const;

export type SocialPlatform = keyof typeof SOCIAL_LINKS;

/** Where the contact form's fallback "email us" link points. */
export const CONTACT_EMAIL = env('VITE_CONTACT_EMAIL') ?? 'support@atlascode.example';

/**
 * Last review date of the legal documents, shown on the Privacy and Terms
 * pages. Bump it whenever the legal team replaces the text.
 */
export const LEGAL_LAST_UPDATED = env('VITE_LEGAL_LAST_UPDATED') ?? '2026-01-01';

/** Marketing/legal display name of the product. */
export const PRODUCT_NAME = 'AtlasCode';
