"use client";

import clsx from "clsx";
import Link from "next/link";

interface Props {
  hectaresUsed: number;
  planLimit: number | null;
  usagePct: number;
}

/**
 * PlanUsageBar — refined hectare usage indicator.
 *
 * Two rendering modes:
 *  - Limited plan: shows used / limit ha, a progress bar, and an upgrade
 *    prompt when usage exceeds 80 %.
 *  - Unlimited plan (planLimit === null): shows a branded confirmation badge
 *    with a check-circle icon.
 *
 * All business logic (pct calculation, barColor thresholds, showUpgrade) is
 * preserved; only the visual layer is upgraded.
 */
export default function PlanUsageBar({
  hectaresUsed,
  planLimit,
  usagePct,
}: Props) {
  // ── Unlimited plan ──────────────────────────────────────────────────────────
  if (planLimit === null) {
    return (
      <div className="bg-white rounded-2xl shadow-sm ring-1 ring-black/5 px-6 py-5 flex items-center gap-4">
        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-agrolens-50 flex-shrink-0">
          <svg
            className="h-5 w-5 text-agrolens-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-widest text-gray-400">
            Plan-Nutzung
          </p>
          <p className="text-sm font-semibold text-gray-900 mt-0.5">
            Pro — Unbegrenzt
          </p>
        </div>
      </div>
    );
  }

  // ── Limited plan ────────────────────────────────────────────────────────────
  const pct = Math.min(usagePct * 100, 100);

  /** Bar fill: red at ≥ 95 %, amber at ≥ 80 %, green otherwise. */
  const barColor =
    pct >= 95 ? "bg-red-500" : pct >= 80 ? "bg-amber-500" : "bg-agrolens-500";

  /** Upgrade prompt appears when capacity is tight. */
  const showUpgrade = pct >= 80;

  return (
    <div className="bg-white rounded-2xl shadow-sm ring-1 ring-black/5 px-6 py-5">
      {/* Label row */}
      <div className="flex items-center justify-between mb-1">
        <p className="text-xs font-semibold uppercase tracking-widest text-gray-400">
          Plan-Nutzung
        </p>
        {showUpgrade && (
          <Link
            href="/dashboard/billing"
            className="text-xs font-semibold text-agrolens-600 hover:text-agrolens-700 transition-colors"
          >
            Upgrade &rarr;
          </Link>
        )}
      </div>

      {/* Value display */}
      <div className="flex items-baseline gap-1 mt-1 mb-3">
        <span className="text-2xl font-extrabold text-gray-900 tabular-nums">
          {hectaresUsed.toFixed(1)}
        </span>
        <span className="text-sm text-gray-400">/ {planLimit} ha</span>
      </div>

      {/* Progress bar */}
      <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={clsx(
            "h-full rounded-full transition-all duration-500",
            barColor
          )}
          style={{ width: `${pct}%` }}
        />
      </div>

      <p className="text-xs text-gray-400 mt-2">{pct.toFixed(0)}% genutzt</p>
    </div>
  );
}
