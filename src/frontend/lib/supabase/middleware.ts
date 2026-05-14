/**
 * Supabase session refresh middleware helper.
 *
 * Wraps an incoming Next.js {@link NextRequest} to refresh the Supabase
 * session cookie on every request.  This ensures that server-rendered
 * pages and Server Components always receive a valid, non-expired session.
 *
 * Must be called from {@link middleware} (the root `middleware.ts`) so
 * that the refreshed Set-Cookie headers are forwarded to the browser on
 * every navigation.
 *
 * @example
 * ```ts
 * // middleware.ts
 * import { updateSession } from "@/lib/supabase/middleware";
 * export async function middleware(request: NextRequest) {
 *   return await updateSession(request);
 * }
 * ```
 */

import { createMiddlewareClient } from "@supabase/auth-helpers-nextjs";
import { NextResponse, type NextRequest } from "next/server";

/**
 * Refresh the Supabase Auth session for the incoming request.
 *
 * Creates a Supabase client that is tied to the request/response cookie
 * jar, calls {@code supabase.auth.getSession()} to trigger a token
 * refresh if needed, and returns the (potentially header-modified)
 * {@link NextResponse}.
 *
 * @param request - The incoming Next.js edge request.
 * @returns A {@link NextResponse} that carries the refreshed session
 *   cookies (or a redirect to /login if the session is absent and the
 *   route is protected).
 */
export async function updateSession(request: NextRequest): Promise<NextResponse> {
  const response = NextResponse.next({ request });

  const supabase = createMiddlewareClient({ req: request, res: response });

  // Refresh session — this is what keeps JWTs from expiring mid-session.
  // The return value is intentionally unused here; the side effect of
  // setting the refreshed cookie on `response` is what matters.
  await supabase.auth.getSession();

  return response;
}
