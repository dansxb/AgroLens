// Re-exported for convenience — not used by the root middleware.ts directly.
// The root middleware.ts handles session refresh and auth redirects inline
// using @supabase/ssr createServerClient.
export { createServerClient } from "@supabase/ssr";
