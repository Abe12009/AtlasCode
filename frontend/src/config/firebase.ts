/**
 * Firebase Web SDK configuration.
 *
 * All of these values are public by design (Firebase's web config is embedded
 * in every client). The *private* half of the trust model lives on the backend,
 * which verifies every Firebase ID token's signature before it will issue an
 * AtlasCode session — see `backend/app/services/firebase_auth.py`.
 *
 * When the variables are absent the app still works: email/password auth falls
 * back to AtlasCode's own endpoints and the OAuth buttons explain that they are
 * not configured, instead of failing silently.
 */

function env(key: string): string | undefined {
  const value = (import.meta.env as Record<string, string | undefined>)[key];
  const trimmed = value?.trim();
  return trimmed ? trimmed : undefined;
}

export const firebaseConfig = {
  apiKey: env('VITE_FIREBASE_API_KEY'),
  authDomain: env('VITE_FIREBASE_AUTH_DOMAIN'),
  projectId: env('VITE_FIREBASE_PROJECT_ID'),
  storageBucket: env('VITE_FIREBASE_STORAGE_BUCKET'),
  messagingSenderId: env('VITE_FIREBASE_MESSAGING_SENDER_ID'),
  appId: env('VITE_FIREBASE_APP_ID'),
};

/**
 * True when enough configuration is present to initialise Firebase Auth.
 * `apiKey`, `authDomain` and `projectId` are the three the Auth SDK requires.
 */
export const isFirebaseConfigured: boolean = Boolean(
  firebaseConfig.apiKey && firebaseConfig.authDomain && firebaseConfig.projectId,
);
