/**
 * Billing API client for AgroLens.
 *
 * Provides typed wrappers around the three billing endpoints:
 *  - GET  /api/v1/billing/subscription  → current plan + status
 *  - POST /api/v1/billing/checkout      → create Stripe Checkout session
 *  - POST /api/v1/billing/portal        → create Stripe Customer Portal session
 */

"use client";

import { apiClient } from "@/lib/api/client";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** The four subscription tiers available in AgroLens. */
export type Plan = "basis" | "starter" | "farmer" | "pro";

/** Lifecycle states returned by the backend (mirrors Stripe status). */
export type SubscriptionStatus = "trialing" | "active" | "past_due" | "canceled";

/** Billing interval for paid plans. */
export type BillingInterval = "monthly" | "annual";

/**
 * Current subscription state for the authenticated user.
 *
 * `current_period_end` is an ISO-8601 UTC string when the user is on a paid
 * plan, or `null` for the free Basis tier.
 */
export interface Subscription {
  plan: Plan;
  status: SubscriptionStatus;
  current_period_end: string | null;
}

/**
 * Request body for creating a Stripe Checkout session.
 *
 * `success_url` and `cancel_url` must be absolute URLs — the browser will
 * be redirected to them after the Stripe Checkout flow completes or is
 * cancelled.
 */
export interface CheckoutRequest {
  plan: "starter" | "farmer" | "pro";
  interval: BillingInterval;
  success_url: string;
  cancel_url: string;
}

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Fetch the current subscription for the authenticated user.
 *
 * @returns The user's active {@link Subscription}.
 * @throws {@link ApiError} on non-2xx responses.
 */
export function getSubscription(): Promise<Subscription> {
  return apiClient.get<Subscription>("/api/v1/billing/subscription");
}

/**
 * Create a Stripe Checkout session for upgrading/changing the subscription.
 *
 * @param data - Plan selection and redirect URLs.
 * @returns An object containing the Stripe Checkout `url` to redirect to.
 * @throws {@link ApiError} on non-2xx responses.
 */
export function createCheckoutSession(
  data: CheckoutRequest
): Promise<{ url: string }> {
  return apiClient.post<{ url: string }>("/api/v1/billing/checkout", data);
}

/**
 * Create a Stripe Customer Portal session for managing the subscription.
 *
 * @param return_url - Absolute URL to redirect back to after the portal session.
 * @returns An object containing the Stripe Portal `url` to redirect to.
 * @throws {@link ApiError} on non-2xx responses.
 */
export function createPortalSession(
  return_url: string
): Promise<{ url: string }> {
  return apiClient.post<{ url: string }>("/api/v1/billing/portal", {
    return_url,
  });
}
