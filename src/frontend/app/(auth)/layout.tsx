/**
 * Auth layout — split-screen layout for all authentication pages.
 *
 * On desktop (md+): left brand panel with social proof + right form area.
 * On mobile/tablet: centered card with a compact brand header.
 *
 * All auth pages (login, signup, reset-password) share this shell.
 */

import React from "react";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: {
    template: "%s | AgroLens",
    default: "AgroLens — Precision Agriculture",
  },
  description: "Sign in to AgroLens precision pesticide intelligence platform.",
};

/** Props for the auth layout component. */
interface AuthLayoutProps {
  children: React.ReactNode;
}

/** Leaf SVG mark used in the brand panels. */
function LeafMark({ className }: { className?: string }): React.ReactElement {
  return (
    <svg
      className={className ?? "h-5 w-5 text-white"}
      viewBox="0 0 24 24"
      fill="currentColor"
      aria-hidden="true"
    >
      <path d="M17 8C8 10 5.9 16.17 3.82 19.07a10 10 0 0 0 15.44-1.83A16 16 0 0 0 17 8Z" />
      <path
        d="M12 3c-1 3.5 1 6 2 8l-4.5 6"
        stroke="currentColor"
        strokeWidth="1.5"
        fill="none"
        strokeLinecap="round"
      />
    </svg>
  );
}

/** Feature highlights shown in the brand panel. */
const FEATURES = [
  { label: "Sentinel-2-Satellitenanalyse alle 5–10 Tage" },
  { label: "ISOBUS-kompatible Ausbringungskarten (TASKDATA.XML)" },
  { label: "§67 PflSchG — vollständiges Ausbringungsprotokoll" },
  { label: "DSGVO-konform · Daten ausschließlich in der EU" },
] as const;

/**
 * Shared layout for all pages under the {@code (auth)} route group.
 *
 * Renders a two-panel shell on desktop (brand left, form right) and a
 * compact stacked shell on mobile with a brand header above the form.
 *
 * @param props - Layout props containing page-specific {@code children}.
 * @returns The auth shell layout React element.
 */
export default function AuthLayout({ children }: AuthLayoutProps): React.ReactElement {
  return (
    <div className="min-h-screen bg-gray-50 md:flex">
      {/* ── LEFT: Brand panel — desktop only ── */}
      <div className="hidden md:flex md:w-1/2 lg:w-2/5 flex-col justify-between bg-agrolens-950 px-12 py-16">
        {/* Top: wordmark */}
        <Link
          href="/"
          className="flex items-center gap-3 text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-agrolens-400 focus-visible:ring-offset-2 focus-visible:ring-offset-agrolens-950 rounded-lg"
          aria-label="AgroLens home"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-agrolens-600">
            <LeafMark />
          </div>
          <span className="text-xl font-bold tracking-tight">AgroLens</span>
        </Link>

        {/* Middle: value proposition + features */}
        <div>
          <p className="text-2xl font-bold leading-snug text-white">
            Präzise Ausbringungskarten aus Satellitendaten —
            automatisch, ISOBUS-kompatibel, EU-konform.
          </p>

          <ul className="mt-10 space-y-4">
            {FEATURES.map((feature) => (
              <li key={feature.label} className="flex items-start gap-3">
                <svg
                  className="mt-0.5 h-5 w-5 flex-shrink-0 text-agrolens-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-sm text-agrolens-300">{feature.label}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Bottom: ESA attribution */}
        <p className="text-xs text-agrolens-600">
          Contains modified Copernicus Sentinel data {new Date().getFullYear()}.
        </p>
      </div>

      {/* ── RIGHT: Form area ── */}
      <div className="flex flex-1 flex-col">
        {/* Mobile-only compact brand header */}
        <header className="md:hidden bg-agrolens-950 px-6 py-4">
          <Link
            href="/"
            className="flex items-center gap-2 text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-agrolens-400 rounded-lg"
            aria-label="AgroLens home"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-agrolens-600">
              <LeafMark className="h-4 w-4 text-white" />
            </div>
            <span className="text-base font-bold">AgroLens</span>
          </Link>
        </header>

        {/* Form container */}
        <main className="flex flex-1 items-center justify-center px-4 py-12 sm:px-8">
          {children}
        </main>

        {/* Footer */}
        <footer className="py-4 text-center text-xs text-gray-400">
          &copy; {new Date().getFullYear()} AgroLens. Alle Rechte vorbehalten.
        </footer>
      </div>
    </div>
  );
}
