"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { LayoutDashboard, Rows3, Settings, CreditCard } from "lucide-react";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, exact: true },
  { href: "/dashboard/fields", label: "Felder", icon: Rows3 },
  { href: "/dashboard/settings", label: "Einstellungen", icon: Settings },
  { href: "/dashboard/billing", label: "Abrechnung", icon: CreditCard },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex flex-col w-[260px] bg-agrolens-950 min-h-screen flex-shrink-0">
      {/* Logo area */}
      <div className="flex items-center gap-2.5 px-5 py-5 border-b border-white/10">
        {/* Leaf / satellite SVG icon */}
        <svg
          width="28"
          height="28"
          viewBox="0 0 28 28"
          fill="none"
          aria-hidden="true"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M4 24C4 24 6 14 14 10C22 6 24 4 24 4C24 4 22 14 14 18C6 22 4 24 4 24Z"
            fill="white"
            fillOpacity="0.9"
          />
          <path
            d="M4 24L14 14"
            stroke="white"
            strokeOpacity="0.5"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
        </svg>
        <span className="text-xl font-bold text-white tracking-tight">AgroLens</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 pt-5 pb-3">
        <p className="px-3 mb-2 text-xs font-semibold uppercase tracking-widest text-agrolens-500">
          Navigation
        </p>
        <ul className="space-y-0.5">
          {NAV.map(({ href, label, icon: Icon, exact }) => {
            const active = exact ? pathname === href : pathname.startsWith(href);
            return (
              <li key={href}>
                <Link
                  href={href}
                  className={clsx(
                    "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150",
                    active
                      ? "bg-white/10 text-white shadow-sm"
                      : "text-agrolens-200 hover:bg-white/5 hover:text-white"
                  )}
                >
                  <Icon
                    size={18}
                    className={clsx(
                      "flex-shrink-0",
                      active ? "text-agrolens-300" : "text-agrolens-400"
                    )}
                  />
                  {label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Bottom user area */}
      <div className="border-t border-white/10 px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-agrolens-700 text-white text-xs font-bold flex-shrink-0">
            ?
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium text-white truncate">Mein Betrieb</p>
            <p className="text-xs text-agrolens-400">AgroLens Farmer</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
