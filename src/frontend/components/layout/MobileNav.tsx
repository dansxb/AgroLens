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
    <nav
      className="md:hidden fixed bottom-0 inset-x-0 bg-white z-50 flex justify-around"
      style={{ boxShadow: "0 -1px 0 0 rgba(0,0,0,0.06), 0 -4px 16px 0 rgba(0,0,0,0.04)" }}
    >
      {NAV.map(({ href, label, icon: Icon, exact }) => {
        const active = exact ? pathname === href : pathname.startsWith(href);
        return (
          <Link
            key={href}
            href={href}
            className={clsx(
              "relative flex flex-col items-center gap-1 px-4 py-2 transition-colors duration-150",
              active ? "text-agrolens-600" : "text-gray-400 hover:text-gray-600"
            )}
          >
            {/* Active indicator — top bar */}
            {active && (
              <span
                className="absolute top-0 inset-x-3 h-0.5 rounded-full bg-agrolens-500"
                aria-hidden="true"
              />
            )}
            <Icon size={20} />
            <span className="text-xs font-medium">{label}</span>
          </Link>
        );
      })}
    </nav>
  );
}
