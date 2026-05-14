"use client";

import clsx from "clsx";
import Link from "next/link";

interface Props {
  hectaresUsed: number;
  planLimit: number | null;
  usagePct: number;
}

export default function PlanUsageBar({ hectaresUsed, planLimit, usagePct }: Props) {
  if (planLimit === null) {
    return (
      <div className="bg-white rounded-xl border border-gray-100 px-5 py-4 shadow-sm">
        <p className="text-xs text-gray-500 mb-1">Plan-Nutzung</p>
        <p className="text-sm text-gray-400">Kein aktives Abo — unbegrenzt</p>
      </div>
    );
  }

  const pct = Math.min(usagePct * 100, 100);
  const barColor =
    pct >= 95 ? "bg-red-500" : pct >= 80 ? "bg-amber-500" : "bg-green-500";
  const showUpgrade = pct >= 80;

  return (
    <div className="bg-white rounded-xl border border-gray-100 px-5 py-4 shadow-sm">
      <div className="flex items-center justify-between mb-2">
        <p className="text-xs text-gray-500">
          Plan-Nutzung — {hectaresUsed.toFixed(1)} / {planLimit} ha
        </p>
        {showUpgrade && (
          <Link
            href="/dashboard/billing"
            className="text-xs font-medium text-amber-600 hover:text-amber-800"
          >
            Upgrade
          </Link>
        )}
      </div>
      <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={clsx("h-full rounded-full transition-all", barColor)}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-xs text-gray-400 mt-1">{pct.toFixed(0)}% genutzt</p>
    </div>
  );
}
