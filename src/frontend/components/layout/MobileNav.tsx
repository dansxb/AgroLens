"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { LayoutDashboard, Rows3, Settings, CreditCard } from "lucide-react";

const NAV = [
  { href: "/dashboard", label: "Home", icon: LayoutDashboard, exact: true },
  { href: "/dashboard/fields", label: "Felder", icon: Rows3 },
  { href: "/dashboard/settings", label: "Einstellungen", icon: Settings },
  { href: "/dashboard/billing", label: "Abo", icon: CreditCard },
];

export default function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="md:hidden fixed bottom-0 inset-x-0 bg-white border-t border-gray-100 flex justify-around py-2 z-50">
      {NAV.map(({ href, label, icon: Icon, exact }) => {
        const active = exact ? pathname === href : pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            className={clsx(
              "flex flex-col items-center gap-0.5 px-3 py-1 text-xs font-medium",
              active ? "text-green-700" : "text-gray-500"
            )}
          >
            <Icon size={20} />
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
