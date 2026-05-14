/**
 * Supabase server-side client factory for Next.js App Router.
 *
 * Creates a Supabase client for use in Server Components, Server Actions,
 * and Route Handlers.  Reads and writes cookies via the Next.js
 * ``cookies()`` API so that the user session persists across requests.
 *
 * Usage in a Server Component:
 * ```tsx
 * import { createSupabaseServerClient } from "@/lib/supabase/server";
 *
 * export default async function Page() {
 *   const supabase = createSupabaseServerClient();
 *   const { data: { session } } = await supabase.auth.getSession();
 *   ...
 * }
 * ```
 *
 * NOTE: Do NOT use this client in Client Components — use
 * {@link createSupabaseBrowserClient} from `./client.ts` instead.
 */

import { createServerComponentClient } from "@supabase/auth-helpers-nextjs";
import { cookies } from "next/headers";
import type { SupabaseClient } from "@supabase/supabase-js";

/**
 * Create a Supabase client for Server Component / Route Handler context.
 *
 * Reads the session from HTTP-only cookies managed by the
 * ``@supabase/auth-helpers-nextjs`` package.
 *
 * @returns A configured {@link SupabaseClient} instance.
 * @throws If ``NEXT_PUBLIC_SUPABASE_URL`` or ``NEXT_PUBLIC_SUPABASE_ANON_KEY``
 *   are not defined.
 */
export function createSupabaseServerClient(): SupabaseClient {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

  if (!supabaseUrl) {
    throw new Error(
      "NEXT_PUBLIC_SUPABASE_URL is not defined. " +
        "Add it to your .env.local file."
    );
  }
  if (!supabaseAnonKey) {
    throw new Error(
      "NEXT_PUBLIC_SUPABASE_ANON_KEY is not defined. " +
        "Add it to your .env.local file."
    );
  }

  return createServerComponentClient(
    { cookies },
    {
      supabaseUrl,
      supabaseKey: supabaseAnonKey,
    }
  );
}
