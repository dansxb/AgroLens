"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";
import { LogOut } from "lucide-react";

/** Map route segments to human-readable German page titles. */
const PAGE_LABELS: Record<string, string> = {
  dashboard: "Dashboard",
  fields: "Felder",
  settings: "Einstellungen",
  billing: "Abrechnung",
};

/** Derive a page label from the last meaningful pathname segment. */
function derivePageLabel(pathname: string): string {
  const segments = pathname.split("/").filter(Boolean);
  const last = segments[segments.length - 1] ?? "dashboard";
  return PAGE_LABELS[last] ?? last.charAt(0).toUpperCase() + last.slice(1);
}

interface Props {
  farmName?: string;
}

export default function TopNav({ farmName }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const supabase = createSupabaseBrowserClient();
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setEmail(session?.user?.email ?? null);
    });
  }, [supabase]);

  async function handleSignOut() {
    await supabase.auth.signOut();
    router.push("/");
    router.refresh();
  }

  const pageLabel = derivePageLabel(pathname);

  return (
    <header className="h-14 bg-white border-b border-gray-100 flex items-center justify-between px-5 md:px-6 flex-shrink-0">
      {/* Left: farm name + breadcrumb */}
      <div className="flex items-center gap-2 min-w-0">
        {farmName && (
          <>
            <span className="text-sm font-semibold text-gray-900 truncate">
              {farmName}
            </span>
            <span className="text-gray-300 select-none" aria-hidden="true">
              /
            </span>
          </>
        )}
        <span className="text-sm text-gray-500">{pageLabel}</span>
      </div>

      {/* Right: email + sign-out */}
      <div className="flex items-center gap-3 flex-shrink-0">
        {email && (
          <span className="text-xs text-gray-500 hidden sm:block select-none">
            {email}
          </span>
        )}
        {email && (
          <span className="text-gray-200 hidden sm:block select-none" aria-hidden="true">
            |
          </span>
        )}
        <button
          onClick={handleSignOut}
          className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-red-600 transition-colors duration-150"
        >
          <LogOut size={14} />
          Abmelden
        </button>
      </div>
    </header>
  );
}
