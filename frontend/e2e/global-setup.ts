import { resetAuthAttempts } from './reset-auth-attempts';

/**
 * Start each run with an empty auth-attempt ledger.
 *
 * This alone is not sufficient: `auth.py` caps registrations per IP per hour,
 * and a full suite creates ~110 accounts, so the cap is reached partway
 * through no matter how clean the start. `registerNewUser` therefore clears
 * the ledger again whenever it actually hits a 429. Clearing here simply means
 * a run never inherits the previous run's attempts.
 */
export default function globalSetup() {
  if (!resetAuthAttempts()) {
    console.warn('[e2e] could not reset auth_attempts (no usable python or database)');
    return;
  }
  console.log('[e2e] auth_attempts cleared');
}
