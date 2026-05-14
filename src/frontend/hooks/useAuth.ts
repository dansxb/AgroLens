/**
 * useAuth — Authentication state hook.
 *
 * Subscribes to Supabase Auth state changes and exposes the current
 * {@link User}, {@link Session}, a loading flag, and a {@code signOut}
 * function.
 *
 * Usage:
 * ```tsx
 * "use client";
 * import { useAuth } from "@/hooks/useAuth";
 *
 * function MyComponent() {
 *   const { user, session, loading, signOut } = useAuth();
 *   if (loading) return <Spinner />;
 *   if (!user) return <Redirect to="/login" />;
 *   return <div>Hello, {user.email}</div>;
 * }
 * ```
 */

"use client";

import { useEffect, useState } from "react";
import type { Session, User } from "@supabase/supabase-js";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";

/** Return type of the {@link useAuth} hook. */
export interface UseAuthReturn {
  /** The current Supabase {@link User}, or {@code null} if unauthenticated. */
  user: User | null;
  /** The current Supabase {@link Session}, or {@code null} if unauthenticated. */
  session: Session | null;
  /** True while the initial auth state is being determined. */
  loading: boolean;
  /**
   * Sign the current user out and redirect to /login.
   *
   * @returns A promise that resolves when the sign-out is complete.
   */
  signOut: () => Promise<void>;
}

/**
 * React hook that provides authentication state from Supabase.
 *
 * Subscribes to {@code onAuthStateChange} so the state is always in sync
 * with the current Supabase session, including after OAuth redirects and
 * token refreshes.
 *
 * @returns {@link UseAuthReturn} containing user, session, loading, signOut.
 */
export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const supabase = createSupabaseBrowserClient();

    // Fetch initial session (handles page refresh without waiting for the
    // auth state change event).
    supabase.auth
      .getSession()
      .then(({ data: { session: currentSession } }) => {
        setSession(currentSession);
        setUser(currentSession?.user ?? null);
        setLoading(false);
      })
      .catch(() => {
        // Auth service unreachable — surface unauthenticated state so the UI
        // can redirect to /login rather than hanging on the loading spinner.
        setLoading(false);
      });

    // Subscribe to auth state changes (sign in, sign out, token refresh).
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, updatedSession) => {
      setSession(updatedSession);
      setUser(updatedSession?.user ?? null);
      setLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const signOut = async (): Promise<void> => {
    const supabase = createSupabaseBrowserClient();
    await supabase.auth.signOut();
    // The onAuthStateChange listener will update state automatically.
    // Redirect to login — use window.location for a hard navigation so
    // the session cookie is cleared from the middleware's perspective.
    window.location.href = "/login";
  };

  return { user, session, loading, signOut };
}
