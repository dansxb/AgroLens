"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";
import { LogOut } from "lucide-react";

interface Props {
  farmName?: string;
}

export default function TopNav({ farmName }: Props) {
  const router = useRouter();
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

  return (
    <header className="h-14 bg-white border-b border-gray-100 flex items-center justify-between px-5 md:px-6">
      <div className="flex items-center gap-2">
        {farmName && (
          <span className="text-sm font-medium text-gray-700">{farmName}</span>
        )}
      </div>
      <div className="flex items-center gap-3">
        {email && (
          <span className="text-xs text-gray-500 hidden sm:block">{email}</span>
        )}
        <button
          onClick={handleSignOut}
          className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-800 transition-colors"
        >
          <LogOut size={15} />
          Abmelden
        </button>
      </div>
    </header>
  );
}
