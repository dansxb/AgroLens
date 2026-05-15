/**
 * PlanSelector component.
 *
 * Renders the four AgroLens pricing tiers (Basis, Starter, Farmer, Pro) in a
 * responsive card grid with a monthly / annual billing-interval toggle.
 *
 * The currently active plan is shown with a disabled "Aktueller Plan" badge.
 * Other paid plans render an "Upgrade" or "Wechseln" CTA that fires the
 * `onSelectPlan` callback, triggering Stripe Checkout in the parent.
 *
 * Uses only inline SVGs — no external icon libraries.
 */

"use client";

import { useState } from "react";
import type { Subscription } from "@/lib/api/billing";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Props {
  /** The user's current subscription, used to highlight the active plan. */
  currentSubscription: Subscription;
  /**
   * Called when the user clicks a paid plan CTA.
   *
   * @param plan     - Target plan identifier.
   * @param interval - Billing cadence chosen via the toggle.
   */
  onSelectPlan: (
    plan: "starter" | "farmer" | "pro",
    interval: "monthly" | "annual"
  ) => void;
  /** When `true` all CTA buttons are disabled and show a loading label. */
  loading: boolean;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

/** Inline check-mark icon for included features. */
function CheckIcon() {
  return (
    <svg
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
      className="h-4 w-4 flex-shrink-0 text-agrolens-600"
    >
      <path
        fillRule="evenodd"
        d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
        clipRule="evenodd"
      />
    </svg>
  );
}

/** Inline cross icon for excluded features. */
function CrossIcon() {
  return (
    <svg
      viewBox="0 0 20 20"
      fill="currentColor"
      aria-hidden="true"
      className="h-4 w-4 flex-shrink-0 text-gray-300"
    >
      <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
    </svg>
  );
}

// ---------------------------------------------------------------------------
// Plan definitions
// ---------------------------------------------------------------------------

interface PlanDefinition {
  id: "basis" | "starter" | "farmer" | "pro";
  name: string;
  monthlyPrice: number;
  /** Total charged per year. Displayed as "€ X / Jahr" when annual is active. */
  annualPrice: number;
  description: string;
  /** Short limits summary shown as a highlighted chip. */
  limits: string;
  /** Features included in this plan. */
  features: string[];
  /** Features explicitly NOT included — rendered with a cross icon. */
  excluded: string[];
  /** When true, render the "Empfohlen" badge and an accent ring. */
  highlighted?: boolean;
}

const PLANS: PlanDefinition[] = [
  {
    id: "basis",
    name: "Basis",
    monthlyPrice: 0,
    annualPrice: 0,
    description: "Zum Kennenlernen",
    limits: "1 Feld · 15 ha",
    features: ["NDVI-Analyse", "Satellitenübersicht", "Dashboard"],
    excluded: ["Ausbringungskarten", "ISOBUS-Export", "API-Zugang"],
  },
  {
    id: "starter",
    name: "Starter",
    monthlyPrice: 49,
    annualPrice: 470,
    description: "Für kleine Betriebe",
    limits: "5 Felder · 100 ha",
    features: [
      "NDVI-Analyse",
      "Ausbringungskarten",
      "ISOBUS-Export (Shapefile)",
      "PDF-Berichte",
      "E-Mail-Alerts",
    ],
    excluded: ["API-Zugang"],
  },
  {
    id: "farmer",
    name: "Farmer",
    monthlyPrice: 149,
    annualPrice: 1430,
    description: "Für wachsende Betriebe",
    limits: "50 Felder · 500 ha",
    features: [
      "NDVI-Analyse",
      "Ausbringungskarten",
      "ISOBUS-Export (SHP + TASKDATA.XML)",
      "PDF-Berichte",
      "E-Mail-Alerts",
      "API-Zugang",
    ],
    excluded: [],
    highlighted: true,
  },
  {
    id: "pro",
    name: "Pro",
    monthlyPrice: 599,
    annualPrice: 5750,
    description: "Für große Betriebe",
    limits: "Unbegrenzte Felder & Fläche",
    features: [
      "NDVI-Analyse",
      "Ausbringungskarten",
      "ISOBUS-Export (SHP + TASKDATA.XML)",
      "PDF-Berichte",
      "E-Mail-Alerts",
      "API-Zugang",
      "Konfigurierbare Zonenzahl (2–5)",
    ],
    excluded: [],
  },
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Pricing grid with monthly/annual billing toggle and upgrade CTAs.
 *
 * @param props - {@link Props}
 * @returns The plan selector React element.
 */
export default function PlanSelector({
  currentSubscription,
  onSelectPlan,
  loading,
}: Props) {
  const [billingInterval, setBillingInterval] = useState<"monthly" | "annual">(
    "monthly"
  );

  return (
    <div>
      {/* Billing-interval toggle */}
      <div className="mb-8 flex items-center justify-center">
        <div className="inline-flex items-center rounded-xl border border-gray-200 bg-white p-1 shadow-sm">
          <button
            type="button"
            onClick={() => setBillingInterval("monthly")}
            className={`rounded-lg px-5 py-2 text-sm font-semibold transition-all duration-150 ${
              billingInterval === "monthly"
                ? "bg-agrolens-600 text-white shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Monatlich
          </button>
          <button
            type="button"
            onClick={() => setBillingInterval("annual")}
            className={`rounded-lg px-5 py-2 text-sm font-semibold transition-all duration-150 ${
              billingInterval === "annual"
                ? "bg-agrolens-600 text-white shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            Jährlich
            <span className="ml-1.5 rounded-full bg-agrolens-50 px-2 py-0.5 text-xs font-bold text-agrolens-700">
              –20%
            </span>
          </button>
        </div>
      </div>

      {/* Plan grid — 1 col mobile, 2 col sm, 4 col xl */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {PLANS.map((plan) => {
          const isCurrent = currentSubscription.plan === plan.id;
          const isFree = plan.monthlyPrice === 0;

          // Effective monthly price — show annual÷12 when annual toggle is on.
          const effectiveMonthlyPrice =
            billingInterval === "annual"
              ? Math.round(plan.annualPrice / 12)
              : plan.monthlyPrice;

          // "Upgrade" label when the user is on Basis or Starter and the target
          // plan is higher; otherwise "Wechseln" for lateral/downgrade moves.
          const planOrder: Record<string, number> = {
            basis: 0,
            starter: 1,
            farmer: 2,
            pro: 3,
          };
          const isUpgrade =
            !isCurrent &&
            !isFree &&
            planOrder[plan.id] > planOrder[currentSubscription.plan];

          return (
            <div
              key={plan.id}
              className={`relative flex flex-col rounded-xl bg-white p-6 transition-shadow duration-200 ${
                plan.highlighted
                  ? "shadow-md ring-2 ring-agrolens-600"
                  : "shadow-sm ring-1 ring-gray-200"
              }`}
            >
              {/* "Empfohlen" badge — floats above the card top edge */}
              {plan.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="inline-flex items-center rounded-full bg-agrolens-600 px-3 py-0.5 text-xs font-bold text-white">
                    Empfohlen
                  </span>
                </div>
              )}

              {/* Plan header */}
              <div>
                <h3 className="text-base font-bold text-gray-900">
                  {plan.name}
                </h3>
                <p className="mt-0.5 text-xs text-gray-500">
                  {plan.description}
                </p>
                <p className="mt-1 inline-block rounded-md bg-agrolens-50 px-2 py-0.5 text-xs font-medium text-agrolens-600">
                  {plan.limits}
                </p>
              </div>

              {/* Pricing */}
              <div className="mt-4 border-b border-gray-100 pb-4">
                {isFree ? (
                  <p
                    className="text-2xl font-extrabold text-gray-900"
                    style={{ letterSpacing: "-0.02em" }}
                  >
                    Gratis
                  </p>
                ) : (
                  <>
                    <p className="flex items-baseline gap-1">
                      <span
                        className="text-2xl font-extrabold text-gray-900"
                        style={{ letterSpacing: "-0.02em" }}
                      >
                        € {effectiveMonthlyPrice}
                      </span>
                      <span className="text-sm text-gray-500">/ Monat</span>
                    </p>
                    {billingInterval === "annual" && (
                      <p className="mt-0.5 text-xs text-gray-400">
                        € {plan.annualPrice} / Jahr
                      </p>
                    )}
                  </>
                )}
              </div>

              {/* Feature list */}
              <ul className="mt-4 flex-1 space-y-2">
                {plan.features.map((feature) => (
                  <li
                    key={feature}
                    className="flex items-start gap-2 text-xs text-gray-700"
                  >
                    <CheckIcon />
                    {feature}
                  </li>
                ))}
                {plan.excluded.map((feature) => (
                  <li
                    key={feature}
                    className="flex items-start gap-2 text-xs text-gray-400"
                  >
                    <CrossIcon />
                    {feature}
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <div className="mt-6">
                {isCurrent ? (
                  <div className="block rounded-lg bg-gray-100 px-4 py-2 text-center text-sm font-semibold text-gray-500">
                    Aktueller Plan
                  </div>
                ) : isFree ? null : (
                  <button
                    type="button"
                    onClick={() =>
                      onSelectPlan(
                        plan.id as "starter" | "farmer" | "pro",
                        billingInterval
                      )
                    }
                    disabled={loading}
                    className={`block w-full rounded-lg px-4 py-2 text-center text-sm font-semibold transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-agrolens-500 focus:ring-offset-2 disabled:opacity-50 ${
                      plan.highlighted
                        ? "bg-agrolens-600 text-white shadow-sm hover:bg-agrolens-700"
                        : "bg-gray-50 text-gray-900 ring-1 ring-gray-200 hover:bg-gray-100"
                    }`}
                  >
                    {loading ? "Lädt…" : isUpgrade ? "Upgrade" : "Wechseln"}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <p className="mt-6 text-center text-xs text-gray-400">
        Alle Preise zzgl. MwSt. · Keine Mindestlaufzeit bei Monatsplänen
      </p>
    </div>
  );
}
