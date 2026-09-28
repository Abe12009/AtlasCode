import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  // Clears the auth-attempt ledger so the register rate limit does not stop the
  // run at its 11th account. See e2e/global-setup.ts -- harness state, not config.
  globalSetup: './e2e/global-setup.ts',
  // Registering a user costs ~4s on its own (sha256_crypt hashing is ~2s per
  // call), so the longest journeys sat right on a 30s budget and failed under
  // load rather than on any real defect.
  timeout: 60000,
  expect: { timeout: 8000 },
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [['list'], ['html', { open: 'never', outputFolder: 'playwright-report' }]],
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
    timeout: 60000,
  },
});
