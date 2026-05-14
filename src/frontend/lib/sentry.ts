"use client";

import * as Sentry from "@sentry/nextjs";

const SENTRY_DSN = process.env.NEXT_PUBLIC_SENTRY_DSN;

if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    tracesSampleRate: 0.1,
    environment: process.env.NODE_ENV ?? "production",
    ignoreErrors: [
      // Ignore Supabase auth state noise
      "AuthSessionMissingError",
    ],
  });
}

export { Sentry };

/**
 * Capture an exception in Sentry (no-op when SENTRY_DSN is not set).
 *
 * @param err - Any caught error value.
 * @param context - Optional extra context tags.
 */
export function captureException(
  err: unknown,
  context?: Record<string, string>
): void {
  if (!SENTRY_DSN) return;
  Sentry.withScope((scope) => {
    if (context) {
      Object.entries(context).forEach(([k, v]) => scope.setTag(k, v));
    }
    Sentry.captureException(err);
  });
}
