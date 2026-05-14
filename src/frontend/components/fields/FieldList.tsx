"use client";

import { useState } from "react";
import Link from "next/link";
import clsx from "clsx";
import type { Field } from "@/lib/api/fields";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type SortKey = "name" | "area_ha" | "crop_type";

interface Props {
  fields: Field[];
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/**
 * Tailwind class pairs for each health status badge.
 * Colours are intentionally muted (100-level bg, 700/800 text) so they read
 * as status signals — not decoration — against the white row background.
 */
const HEALTH_COLORS: Record<string, string> = {
  normal: "bg-green-100 text-green-700",
  mild_stress: "bg-amber-100 text-amber-700",
  significant_stress: "bg-red-100 text-red-700",
  unknown: "bg-gray-100 text-gray-500",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Returns a display label and status key for a field's vegetation health.
 *
 * Phase 4: once analytics summary data is wired up, derive the key from the
 * most-recent NDVI reading attached to the field object.
 */
function healthLabel(field: Field): { key: string; label: string } {
  // Placeholder until analytics endpoint is connected in Phase 4.
  return { key: "unknown", label: "Wird berechnet …" };
}

/**
 * Shared SVG path for the field / map-boundary icon used throughout this
 * component.  Defined once to avoid duplication.
 */
const FIELD_ICON_PATH =
  "M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497z";

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * FieldList — sorted, interactive list of farm fields.
 *
 * Renders an actionable empty state when `fields` is empty, otherwise a
 * sort-controlled list of card-style rows, each linking to the field detail
 * page.
 */
export default function FieldList({ fields }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>("name");
  const [asc, setAsc] = useState(true);

  // Stable sort — preserves original order for equal values.
  const sorted = [...fields].sort((a, b) => {
    const av = a[sortKey] ?? "";
    const bv = b[sortKey] ?? "";
    if (av < bv) return asc ? -1 : 1;
    if (av > bv) return asc ? 1 : -1;
    return 0;
  });

  /** Toggle sort direction if already active; otherwise adopt the new key ascending. */
  function toggleSort(key: SortKey) {
    if (key === sortKey) {
      setAsc((v) => !v);
    } else {
      setSortKey(key);
      setAsc(true);
    }
  }

  /**
   * Pill-shaped sort button.  Active state uses a filled agrolens-tinted
   * background so the current sort axis is immediately obvious at a glance.
   */
  function SortBtn({ k, label }: { k: SortKey; label: string }) {
    const active = sortKey === k;
    return (
      <button
        onClick={() => toggleSort(k)}
        className={clsx(
          "flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors",
          active
            ? "bg-agrolens-50 text-agrolens-700"
            : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
        )}
      >
        {label}
        {active && (
          <span className="text-agrolens-500">{asc ? "↑" : "↓"}</span>
        )}
      </button>
    );
  }

  // ---------------------------------------------------------------------------
  // Empty state
  // ---------------------------------------------------------------------------

  if (fields.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center px-4">
        {/* Illustrated icon lockup */}
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-agrolens-50 mb-6">
          <svg
            className="h-8 w-8 text-agrolens-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={1.5}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d={FIELD_ICON_PATH}
            />
          </svg>
        </div>

        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Noch keine Felder
        </h3>
        <p className="text-sm text-gray-500 max-w-sm mb-6">
          Fügen Sie Ihr erstes Feld hinzu, um mit der Satellitenanalyse zu
          beginnen.
        </p>

        <Link href="/dashboard/fields/new" className="inline-flex items-center rounded-lg bg-agrolens-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-agrolens-700 focus:outline-none focus:ring-2 focus:ring-agrolens-600 focus:ring-offset-2 transition-all duration-200">
          Erstes Feld anlegen
        </Link>
      </div>
    );
  }

  // ---------------------------------------------------------------------------
  // Populated list
  // ---------------------------------------------------------------------------

  return (
    <div>
      {/* Sort header -------------------------------------------------------- */}
      <div className="flex items-center gap-1 px-4 py-3 border-b border-gray-100">
        <span className="text-xs font-semibold uppercase tracking-widest text-gray-400 mr-2">
          Sortieren:
        </span>
        <SortBtn k="name" label="Name" />
        <span className="text-gray-200">·</span>
        <SortBtn k="area_ha" label="Fläche" />
        <span className="text-gray-200">·</span>
        <SortBtn k="crop_type" label="Frucht" />
      </div>

      {/* Field rows --------------------------------------------------------- */}
      <div className="divide-y divide-gray-50">
        {sorted.map((field) => {
          const health = healthLabel(field);

          // Derive the icon background and foreground colours from health status
          // so the icon doubles as a quick-scan status signal.
          const iconBg =
            health.key === "normal"
              ? "bg-green-100"
              : health.key === "mild_stress"
              ? "bg-amber-100"
              : health.key === "significant_stress"
              ? "bg-red-100"
              : "bg-gray-100";

          const iconColor =
            health.key === "normal"
              ? "text-green-600"
              : health.key === "mild_stress"
              ? "text-amber-600"
              : health.key === "significant_stress"
              ? "text-red-600"
              : "text-gray-400";

          return (
            <Link
              key={field.id}
              href={`/dashboard/fields/${field.id}`}
              className="flex items-center justify-between px-4 py-4 hover:bg-gray-50 transition-colors group"
            >
              {/* Left: field identity -------------------------------------- */}
              <div className="flex items-center gap-4 min-w-0">
                {/* Status-tinted field icon */}
                <div
                  className={clsx(
                    "flex-shrink-0 h-9 w-9 rounded-xl flex items-center justify-center",
                    iconBg
                  )}
                >
                  <svg
                    className={clsx("h-5 w-5", iconColor)}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={1.5}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d={FIELD_ICON_PATH}
                    />
                  </svg>
                </div>

                {/* Name + crop / area metadata */}
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-gray-900 truncate group-hover:text-agrolens-700 transition-colors">
                    {field.name}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {field.crop_type ?? "Frucht unbekannt"}
                    {" · "}
                    {field.area_ha != null
                      ? `${field.area_ha.toFixed(1)} ha`
                      : "— ha"}
                  </p>
                </div>
              </div>

              {/* Right: health badge + navigation chevron ------------------ */}
              <div className="flex items-center gap-3 flex-shrink-0">
                <span
                  className={clsx(
                    "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium",
                    HEALTH_COLORS[health.key]
                  )}
                >
                  {health.label}
                </span>

                {/* Chevron — communicates row navigability */}
                <svg
                  className="h-4 w-4 text-gray-300 group-hover:text-gray-500 transition-colors"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M8.25 4.5l7.5 7.5-7.5 7.5"
                  />
                </svg>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
