/**
 * HTTP details off a rejected API call.
 *
 * Structurally typed rather than `import type { AxiosError }`: axios lives
 * behind `src/api/client.ts`, and these two readers are the only thing the
 * pages need from a rejection. A non-HTTP failure (network down, aborted
 * request) has no `response`, so both return undefined and callers fall back
 * to their generic path.
 */
type HttpErrorShape = {
  response?: { status?: number; data?: { detail?: string } };
};

export function errorStatus(error: unknown): number | undefined {
  return (error as HttpErrorShape | null | undefined)?.response?.status;
}

export function errorDetail(error: unknown): string | undefined {
  return (error as HttpErrorShape | null | undefined)?.response?.data?.detail;
}

/** The backend's 403 for a lesson the sequence has not opened yet. */
export function isLockedError(error: unknown): boolean {
  return errorStatus(error) === 403;
}
