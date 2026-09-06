import { firebaseConfig, isFirebaseConfigured } from '../config/firebase';

/**
 * Firebase Auth is only initialised when the deployment actually configured
 * it (see `config/firebase.ts`), and the SDK itself is dynamically imported
 * on first use rather than bundled into the main chunk — most visitors never
 * touch Google/GitHub sign-in or password reset, so there is no reason to
 * ship ~110KB of Firebase to every landing-page load.
 *
 * Everything here is a thin wrapper so callers never touch the SDK directly
 * and never need to null-check anything themselves — they just get a
 * rejected promise with a clear message when the feature isn't available.
 */

export class FirebaseNotConfiguredError extends Error {
  constructor() {
    super('Firebase authentication is not configured for this deployment.');
    this.name = 'FirebaseNotConfiguredError';
  }
}

async function getAuthInstance() {
  if (!isFirebaseConfigured) throw new FirebaseNotConfiguredError();
  const [{ initializeApp, getApps }, authModule] = await Promise.all([
    import('firebase/app'),
    import('firebase/auth'),
  ]);
  const app = getApps()[0] ?? initializeApp(firebaseConfig);
  return { auth: authModule.getAuth(app), authModule };
}

export async function signInWithGoogle() {
  const { auth, authModule } = await getAuthInstance();
  return authModule.signInWithPopup(auth, new authModule.GoogleAuthProvider());
}

export async function signInWithGithub() {
  const { auth, authModule } = await getAuthInstance();
  return authModule.signInWithPopup(auth, new authModule.GithubAuthProvider());
}

/**
 * Always resolves, even for an email with no account — Firebase (with Email
 * Enumeration Protection enabled in the console, which we document as
 * required) does the same, so the UI never reveals whether an address is
 * registered.
 */
export async function sendPasswordResetEmail(email: string): Promise<void> {
  const { auth, authModule } = await getAuthInstance();
  await authModule.sendPasswordResetEmail(auth, email);
}

/** Maps a firebase-auth error code to a short, user-facing message. */
export function describeFirebaseAuthError(error: unknown): string {
  const code = (error as { code?: string })?.code;
  switch (code) {
    case 'auth/popup-closed-by-user':
    case 'auth/cancelled-popup-request':
      return 'Sign-in was cancelled.';
    case 'auth/account-exists-with-different-credential':
      return 'An account already exists with a different sign-in method for this email.';
    case 'auth/popup-blocked':
      return 'Your browser blocked the sign-in popup. Please allow popups and try again.';
    case 'auth/network-request-failed':
      return 'Network error. Please check your connection and try again.';
    default:
      return error instanceof FirebaseNotConfiguredError
        ? error.message
        : 'Sign-in failed. Please try again.';
  }
}

export { isFirebaseConfigured };
