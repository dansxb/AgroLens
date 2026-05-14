"use client";

import { useState } from "react";
import Link from "next/link";
import clsx from "clsx";
import type { Field } from "@/lib/api/fields";

type SortKey = "name" | "area_ha" | "crop_type";

interface Props {
  fields: Field[];
}

const HEALTH_COLORS: Record<string, string> = {
  normal: "bg-green-100 text-green-800",
  mild_stress: "bg-amber-100 text-amber-800",
  significant_stress: "bg-red-100 text-red-800",
  unknown: "bg-gray-100 text-gray-500",
};

function healthLabel(field: Field): { key: string; label: string } {
  // Phase 4: health status will come from analytics summary endpoint.
  // Until analytics data exists we show "Calculating…"
  return { key: "unknown", label: "Calculating…" };
}

export default function FieldList({ fields }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("name");
  const [asc, setAsc] = useState(true);

  const sorted = [...fields].sort((a, b) => {
    const av = a[sortKey] ?? "";
    const bv = b[sortKey] ?? "";
    if (av < bv) return asc ? -1 : 1;
    if (av > bv) return asc ? 1 : -1;
    return 0;
  });

  function toggleSort(key: SortKey) {
    if (key === sortKey) setAsc((v) => !v);
    else { setSortKey(key); setAsc(true); }
  }

  function SortBtn({ k, label }: { k: SortKey; label: string }) {
    return (
      <button
        onClick={() => toggleSort(k)}
        className={clsx(
          "text-xs font-medium uppercase tracking-wide",
          sortKey === k ? "text-green-700" : "text-gray-500 hover:text-gray-700"
        )}
      >
        {label} {sortKey === k ? (asc ? "↑" : "↓") : ""}
      </button>
    );
  }

  if (fields.length === 0) {
    return (
      <div className="text-center py-16 text-gray-500">
        <p className="text-lg font-medium">Noch keine Felder vorhanden</p>
        <p className="text-sm mt-1">Fügen Sie Ihr erstes Feld hinzu.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex gap-4 mb-3 px-1">
        <SortBtn k="name" label="Name" />
        <SortBtn k="area_ha" label="Fläche" />
        <SortBtn k="crop_type" label="Frucht" />
      </div>
      <ul className="divide-y divide-gray-100">
        {sorted.map((field) => {
          const health = healthLabel(field);
          return (
            <li key={field.id}>
              <Link
                href={`/dashboard/fields/${field.id}`}
                className="flex items-center justify-between px-3 py-3 hover:bg-gray-50 rounded-lg transition-colors"
              >
                <div>
                  <p className="font-medium text-gray-900 text-sm">{field.name}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {field.crop_type ?? "—"} ·{" "}
                    {field.area_ha != null ? `${field.area_ha.toFixed(1)} ha` : "— ha"}
                  </p>
                </div>
                <span
                  className={clsx(
                    "text-xs font-medium px-2 py-0.5 rounded-full",
                    HEALTH_COLORS[health.key]
                  )}
                >
                  {health.label}
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
