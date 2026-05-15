/**
 * CurrentPlanCard component.
 *
 * Displays the user's active plan tier, subscription status, and next billing
 * date. For paid plans it renders a "Abonnement verwalten" button that opens
 * the Stripe Customer Portal via the `onManage` callback.
 *
 * Follows the card style established in `app/(dashboard)/settings/page.tsx`.
 * Uses only inline SVGs — no external icon libraries.
 */

"use client";

import type { Subscription } from "@/lib/api/billing";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Props {
  /** The user's current subscription state. */
  subscription: Subscription;
  /** Called when the user clicks "Abonnement verwalten". */
  onManage: () => void;
  /** When `true` the manage button is disabled and shows a loading label. */
  loading: boolean;
}

// ---------------------------------------------------------------------------
// Label / colour maps
// ---------------------------------------------------------------------------

const PLAN_LABELS: Record<string, string> = {
  basis: "Basis (kostenlos)",
  starter: "Starter",
  farmer: "Farmer",
  pro: "Pro",
};

const PLAN_COLORS: Record<string, string> = {
  basis: "bg-gray-100 text-gray-700",
  starter: "bg-agrolens-100 text-agrolens-700",
  farmer: "bg-blue-100 text-blue-700",
  pro: "bg-purple-100 text-purple-700",
};

const STATUS_LABELS: Record<string, string> = {
  active: "Aktiv",
  trialing: "Testphase",
  past_due: "Zahlung ausstehend",
  canceled: "Gekündigt",
};

/**
 * Tailwind text-colour classes for each subscription status.
 *
 * trialing maps to blue because it is an informational state, not
 * a success state.
 */
const STATUS_COLORS: Record<string, string> = {
  active: "text-green-600",
  trialing: "text-blue-600",
  past_due: "text-amber-600",
  canceled: "text-red-600",
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * Card showing the current AgroLens plan and its lifecycle status.
 *
 * @param props - {@link Props}
 * @returns The plan status card React element.
 */
export default function CurrentPlanCard({
  subscription,
  onManage,
  loading,
}: Props) {
  const isBasis = subscription.plan === "basis";

  // Format the period-end date in German locale when present.
  const periodEnd = subscription.current_period_end
    ? new Date(subscription.current_period_end).toLocaleDateString("de-DE", {
        day: "2-digit",
        month: "long",
        year: "numeric",
      })
    : null;

  const planColorClass =
    PLAN_COLORS[subscription.plan] ?? "bg-gray-100 text-gray-700";
  const statusColorClass =
    STATUS_COLORS[subscription.status] ?? "text-gray-600";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        {/* Left side — plan badge + status + next billing date */}
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
            Aktueller Plan
          </h3>

          <div className="mt-2 flex items-center gap-3">
            {/* Plan tier badge */}
            <span
              className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-semibold ${planColorClass}`}
            >
              {PLAN_LABELS[subscription.plan] ?? subscription.plan}
            </span>

            {/* Status indicator with filled-circle dot */}
            <span
              className={`flex items-center gap-1.5 text-sm font-medium ${statusColorClass}`}
            >
              <svg
                width="8"
                height="8"
                viewBox="0 0 8 8"
                aria-hidden="true"
                className="flex-shrink-0"
              >
                <circle cx="4" cy="4" r="4" fill="currentColor" />
              </svg>
              {STATUS_LABELS[subscription.status] ?? subscription.status}
            </span>
          </div>

          {/* Next billing / end date */}
          {periodEnd && (
            <p className="mt-2 text-sm text-gray-500">
              {subscription.status === "canceled"
                ? "Endet am"
                : "Nächste Abrechnung am"}{" "}
              {periodEnd}
            </p>
          )}
        </div>

        {/* Right side — "Manage" button (hidden on free Basis plan) */}
        {!isBasis && (
          <button
            type="button"
            onClick={onManage}
            disabled={loading}
            className="flex-shrink-0 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm transition-all duration-150 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-agrolens-500 focus:ring-offset-2 disabled:opacity-50"
          >
            {loading ? "Lädt…" : "Abonnement verwalten"}
          </button>
        )}
      </div>
    </div>
  );
}
