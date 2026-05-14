/**
 * Billing & Subscription management page — /dashboard/billing
 *
 * Fetches the authenticated user's current subscription from
 * GET /api/v1/billing/subscription on mount, then renders:
 *
 *  - {@link CurrentPlanCard}  — plan tier + status + next billing date
 *  - {@link PlanSelector}     — interactive pricing grid with upgrade CTAs
 *
 * The "Abonnement verwalten" button opens the Stripe Customer Portal.
 * Clicking an upgrade CTA starts a Stripe Checkout session and redirects
 * the browser to Stripe. Both actions set `actionLoading` to avoid
 * duplicate clicks while the redirect is in flight.
 *
 * This is a Client Component — all data fetching uses the authenticated
 * Supabase session via `apiClient`.
 */

"use client";

import { useEffect, useState, useCallback } from "react";
import {
  getSubscription,
  createCheckoutSession,
  createPortalSession,
  type Subscription,
} from "@/lib/api/billing";
import CurrentPlanCard from "@/components/billing/CurrentPlanCard";
import PlanSelector from "@/components/billing/PlanSelector";

/**
 * Billing page component.
 *
 * @returns The billing management page React element.
 */
export default function BillingPage() {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  /** True while the initial subscription fetch is in progress. */
  const [loadingPage, setLoadingPage] = useState<boolean>(true);
  /**
   * True while a portal or checkout redirect is in flight.
   * Disables all action buttons to prevent duplicate submissions.
   */
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch subscription on mount.
  useEffect(() => {
    getSubscription()
      .then(setSubscription)
      .catch(() => setError("Abonnement konnte nicht geladen werden."))
      .finally(() => setLoadingPage(false));
  }, []);

  /**
   * Open the Stripe Customer Portal for the current user.
   * Redirects the browser on success.
   */
  const handleManage = useCallback(async () => {
    setActionLoading(true);
    setError(null);
    try {
      const { url } = await createPortalSession(window.location.href);
      window.location.href = url;
    } catch {
      setError("Billing-Portal konnte nicht geöffnet werden.");
      setActionLoading(false);
    }
  }, []);

  /**
   * Start a Stripe Checkout session for the selected plan and billing interval.
   * Redirects the browser to Stripe on success.
   *
   * @param plan     - Target subscription plan.
   * @param interval - Monthly or annual billing cadence.
   */
  const handleSelectPlan = useCallback(
    async (
      plan: "starter" | "farmer" | "pro",
      interval: "monthly" | "annual"
    ) => {
      setActionLoading(true);
      setError(null);
      try {
        const { url } = await createCheckoutSession({
          plan,
          interval,
          success_url: `${window.location.origin}/dashboard/billing?success=1`,
          cancel_url: window.location.href,
        });
        window.location.href = url;
      } catch {
        setError("Checkout konnte nicht gestartet werden.");
        setActionLoading(false);
      }
    },
    []
  );

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Page header */}
      <div className="mb-8">
        <h1
          className="text-2xl font-bold text-gray-900"
          style={{ letterSpacing: "-0.02em" }}
        >
          Abonnement & Abrechnung
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Verwalten Sie Ihren Plan und Ihre Zahlungsmethode.
        </p>
      </div>

      {/* Inline error banner */}
      {error && (
        <div
          role="alert"
          className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
        >
          {error}
        </div>
      )}

      {/* Loading skeleton */}
      {loadingPage && (
        <div className="space-y-4">
          <div className="h-28 animate-pulse rounded-xl bg-gray-100" />
          <div className="h-64 animate-pulse rounded-xl bg-gray-100" />
        </div>
      )}

      {/* Main content — rendered once the subscription is loaded */}
      {!loadingPage && subscription && (
        <div className="space-y-8">
          <CurrentPlanCard
            subscription={subscription}
            onManage={handleManage}
            loading={actionLoading}
          />

          <div>
            <h2 className="mb-4 text-lg font-semibold text-gray-900">
              {subscription.plan === "pro"
                ? "Ihr aktueller Plan"
                : "Plan wechseln"}
            </h2>
            <PlanSelector
              currentSubscription={subscription}
              onSelectPlan={handleSelectPlan}
              loading={actionLoading}
            />
          </div>
        </div>
      )}
    </div>
  );
}
