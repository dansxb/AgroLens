"use client";

/**
 * Supabase browser client factory.
 *
 * Creates a Supabase client configured for use in Client Components
 * (browser context).  Uses the public anon key — Row Level Security
 * policies on the Supabase side enforce access control.
 *
 * Usage in a Client Component:
 * ```tsx
 * "use client";
 * import { createSupabaseBrowserClient } from "@/lib/supabase/client";
 *
 * const supabase = createSupabaseBrowserClient();
 * const { data, error } = await supabase.auth.getSession();
 * ```
 */

import { createClientComponentClient } from "@supabase/auth-helpers-nextjs";
import type { SupabaseClient } from "@supabase/supabase-js";

/**
 * Create a Supabase client for use in browser (Client Component) context.
 *
 * The client is configured from ``NEXT_PUBLIC_SUPABASE_URL`` and
 * ``NEXT_PUBLIC_SUPABASE_ANON_KEY`` environment variables, which are
 * validated at build time by Next.js.
 *
 * @returns A configured {@link SupabaseClient} instance.
 * @throws If the required environment variables are not defined.
 */
export function createSupabaseBrowserClient(): SupabaseClient {
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

  return createClientComponentClient({
    supabaseUrl,
    supabaseKey: supabaseAnonKey,
  });
}
