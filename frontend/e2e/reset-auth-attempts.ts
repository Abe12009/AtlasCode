import { execFileSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// package.json sets "type": "module", so there is no __dirname here.
const HERE = path.dirname(fileURLToPath(import.meta.url));
const DB_PATH = path.resolve(HERE, '../../backend/atlascode.db');

const RESET = `
import sqlite3, sys
con = sqlite3.connect(sys.argv[1])
try:
    removed = con.execute("delete from auth_attempts").rowcount
    con.commit()
    print(removed)
except sqlite3.OperationalError as exc:
    # A fresh checkout may not have migrated yet; not a failure.
    print(f"skipped ({exc})")
finally:
    con.close()
`;

/**
 * Clears the auth-attempt ledger `auth.py` counts to enforce its per-IP
 * registration cap.
 *
 * This resets harness state; it does not change the cap, which stays exactly
 * as production sets it. Done through python rather than a node sqlite driver
 * so e2e gains no dependency -- python already has to be present to run the
 * backend at all.
 *
 * Returns false when no interpreter could be found, so callers can decide
 * whether that is fatal.
 */
export function resetAuthAttempts(): boolean {
  if (!existsSync(DB_PATH)) return false;
  for (const binary of ['python', 'python3']) {
    try {
      execFileSync(binary, ['-c', RESET, DB_PATH], { encoding: 'utf8' });
      return true;
    } catch {
      // Try the next interpreter name before giving up.
    }
  }
  return false;
}
