/**
 * Auth layout — centered card layout for all authentication pages.
 *
 * Wraps the login, signup, and reset-password pages with a full-height
 * background and a centred content column that houses the auth card.
 * The AgroLens logo/wordmark is displayed above the card.
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

/**
 * Shared layout for all pages under the {@code (auth)} route group.
 *
 * Renders a two-tone background (green top band + white/gray bottom)
 * with the auth card vertically and horizontally centred.
 *
 * @param props - Layout props containing page-specific {@code children}.
 * @returns The auth shell layout React element.
 */
export default function AuthLayout({ children }: AuthLayoutProps): React.ReactElement {
  return (
    <div className="flex min-h-screen flex-col bg-gray-50">
      {/* Top brand bar */}
      <header className="bg-agrolens-700 py-4">
        <div className="mx-auto max-w-md px-4">
          <Link
            href="/"
            className="flex items-center gap-2 text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-white"
            aria-label="AgroLens home"
          >
            {/* Leaf icon (inline SVG — no external icon dependency) */}
            <svg
              className="h-7 w-7"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <path
                d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"
                fill="currentColor"
                opacity="0.2"
              />
              <path
                d="M12 3.5C7.5 3.5 5 7 5 12c0 2.5 2 5 4 6.5 1-2 3-3.5 6-4L12 3.5z"
                fill="currentColor"
              />
              <path
                d="M12 3.5l3 11c2-1.5 4-4 4-6.5 0-2.5-2-5-7-4.5z"
                fill="currentColor"
                opacity="0.7"
              />
            </svg>
            <span className="text-lg font-bold tracking-tight">AgroLens</span>
          </Link>
        </div>
      </header>

      {/* Main content — vertically centred card */}
      <main className="flex flex-1 items-center justify-center px-4 py-12">
        {children}
      </main>

      {/* Footer */}
      <footer className="py-4 text-center text-xs text-gray-400">
        &copy; {new Date().getFullYear()} AgroLens. All rights reserved.
      </footer>
    </div>
  );
}
