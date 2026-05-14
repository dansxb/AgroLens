/**
 * Next.js Edge Middleware — Authentication guard for protected routes.
 *
 * Runs on every request matching the {@link config.matcher} pattern.
 * Refreshes the Supabase session cookie on every request (so JWTs do
 * not expire between page navigations), and redirects unauthenticated
 * users to {@code /login} when they attempt to access any route under
 * {@code /dashboard}.
 *
 * This middleware runs on the Next.js Edge Runtime — no Node.js APIs.
 */

import { createMiddlewareClient } from "@supabase/auth-helpers-nextjs";
import { NextResponse, type NextRequest } from "next/server";

/**
 * Middleware handler executed for every matched request.
 *
 * @param request - The incoming Next.js edge request.
 * @returns A {@link NextResponse}: either a redirect to /login (for
 *   unauthenticated dashboard access) or the original response with
 *   refreshed session cookies.
 */
export async function middleware(request: NextRequest): Promise<NextResponse> {
  const response = NextResponse.next({ request });

  // Create a Supabase client bound to the request/response cookie jar.
  // This client is used both for session refresh and auth state reads.
  const supabase = createMiddlewareClient({ req: request, res: response });

  // Refresh session — ensures tokens are renewed on every navigation.
  const {
    data: { session },
  } = await supabase.auth.getSession();

  const { pathname } = request.nextUrl;

  // Redirect unauthenticated users away from /dashboard/* routes.
  const isDashboardRoute = pathname.startsWith("/dashboard");
  if (isDashboardRoute && !session) {
    const loginUrl = new URL("/login", request.url);
    // Preserve the intended destination so the login page can redirect back.
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Redirect already-authenticated users away from auth pages.
  const isAuthRoute =
    pathname.startsWith("/login") ||
    pathname.startsWith("/signup") ||
    pathname.startsWith("/reset-password");
  if (isAuthRoute && session) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return response;
}

/**
 * Middleware matcher configuration.
 *
 * Runs on all routes except:
 * - Next.js internal routes (_next/static, _next/image)
 * - API routes (/api/*)
 * - Static file requests (favicon.ico, images, etc.)
 */
export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};
