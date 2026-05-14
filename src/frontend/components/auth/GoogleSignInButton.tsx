/**
 * GoogleSignInButton — OAuth sign-in button for Google.
 *
 * Triggers the Supabase OAuth flow with the Google provider.  On
 * success, Supabase redirects the browser to the configured OAuth
 * callback URL (which should redirect the user to /dashboard).
 *
 * @example
 * ```tsx
 * <GoogleSignInButton redirectTo="/dashboard" />
 * ```
 */

"use client";

import React, { useState } from "react";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";

/** Props for the {@link GoogleSignInButton} component. */
export interface GoogleSignInButtonProps {
  /**
   * URL to redirect to after a successful Google OAuth flow.
   * Defaults to {@code /dashboard}.
   */
  redirectTo?: string;
  /** Whether the button should be disabled (e.g. while a form is submitting). */
  disabled?: boolean;
}

/**
 * A button that initiates Supabase Google OAuth sign-in.
 *
 * Displays a loading spinner while the redirect is in progress.
 *
 * @param props - {@link GoogleSignInButtonProps}
 * @returns A React element for the Google sign-in button.
 */
export function GoogleSignInButton({
  redirectTo = "/dashboard",
  disabled = false,
}: GoogleSignInButtonProps): React.ReactElement {
  const [loading, setLoading] = useState<boolean>(false);

  const handleGoogleSignIn = async (): Promise<void> => {
    setLoading(true);
    const supabase = createSupabaseBrowserClient();

    const { error } = await supabase.auth.signInWithOAuth({
      provider: "google",
      options: {
        redirectTo: `${window.location.origin}/auth/callback?next=${encodeURIComponent(redirectTo)}`,
        queryParams: {
          access_type: "offline",
          prompt: "consent",
        },
      },
    });

    if (error) {
      // The redirect didn't happen — reset loading state so the user can retry.
      console.error("Google OAuth error:", error.message);
      setLoading(false);
    }
    // On success, Supabase redirects the browser — no further action needed here.
  };

  return (
    <button
      type="button"
      onClick={handleGoogleSignIn}
      disabled={disabled || loading}
      aria-label="Continue with Google"
      className="flex w-full items-center justify-center gap-3 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-agrolens-600 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {loading ? (
        /* Loading spinner */
        <svg
          className="h-4 w-4 animate-spin text-gray-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
      ) : (
        /* Google "G" logo SVG */
        <svg
          className="h-4 w-4"
          viewBox="0 0 24 24"
          aria-hidden="true"
          focusable="false"
        >
          <path
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            fill="#4285F4"
          />
          <path
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            fill="#34A853"
          />
          <path
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            fill="#FBBC05"
          />
          <path
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            fill="#EA4335"
          />
        </svg>
      )}
      <span>{loading ? "Redirecting…" : "Continue with Google"}</span>
    </button>
  );
}
