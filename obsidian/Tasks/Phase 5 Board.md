# Phase 5 Task Board — Billing & Subscriptions

## Status: 🔲 Not started

Phase 5 wires Stripe into the backend and enforces subscription limits on field creation and prescription generation.

---

## Plan

### Models

- [ ] `Subscription` ORM model
  - Columns: `id`, `user_id` (FK), `stripe_customer_id`, `stripe_subscription_id`, `plan` (PgEnum: starter/farmer/pro), `status` (PgEnum: active/past_due/canceled/trialing), `current_period_end`, `created_at`, `updated_at`
  - Add `create_type=False` on all PgEnums
- [ ] Migration `0007_create_subscriptions.py`
- [ ] Add `subscription` relationship to `User` model

### Stripe Integration

- [ ] `services/stripe_service.py`
  - `create_checkout_session(user, price_id)` → Stripe Checkout URL
  - `create_portal_session(stripe_customer_id)` → Customer Portal URL
  - `get_or_create_customer(user)` → Stripe Customer ID
- [ ] `POST /api/v1/billing/checkout` — returns `{"url": "https://checkout.stripe.com/..."}`
- [ ] `POST /api/v1/billing/portal` — returns `{"url": "https://billing.stripe.com/..."}`

### Webhook Handler

- [ ] `POST /api/v1/webhooks/stripe`
  - Verify `Stripe-Signature` header with `STRIPE_WEBHOOK_SECRET`
  - Handle events: `checkout.session.completed`, `invoice.paid`, `invoice.payment_failed`, `customer.subscription.deleted`, `customer.subscription.updated`
  - Update `Subscription` record on each event
  - Celery task `billing.sync_subscription_status` for async DB updates

### Subscription Enforcement

- [ ] `app/core/limits.py` — plan limits table
  ```
  starter:  50 ha, 5 fields
  farmer:   500 ha, 50 fields
  pro:      unlimited
  free:     10 ha, 2 fields (trial)
  ```
- [ ] Enforce in `POST /api/v1/fields` — reject if field count or total hectares over limit
- [ ] Enforce in `POST /api/v1/fields/{id}/prescriptions` — reject if over limit
- [ ] `GET /api/v1/account/usage` — return real `plan_limit` from `Subscription` (currently hardcoded null)

### Frontend (Phase 5 UI)

- [ ] `app/(dashboard)/settings/billing/page.tsx` — current plan, usage bar, upgrade/manage button
- [ ] Checkout redirect flow
- [ ] Subscription status banner (past_due / canceled warning)
- [ ] Upgrade CTA from `PlanUsageBar` → `/settings/billing`

---

## Stripe Price IDs (set in `.env`)

```
STRIPE_PRICE_ID_STARTER_MONTHLY  €49/month
STRIPE_PRICE_ID_STARTER_ANNUAL   €470/year
STRIPE_PRICE_ID_FARMER_MONTHLY   €199/month
STRIPE_PRICE_ID_FARMER_ANNUAL    €1,910/year
STRIPE_PRICE_ID_PRO_MONTHLY      €599/month
STRIPE_PRICE_ID_PRO_ANNUAL       €5,750/year
```

---

## Migration

| Migration | Covers | down_revision |
|-----------|--------|---------------|
| `0007_create_subscriptions.py` | subscriptions table + plantype + subscriptionstatus enums | 0006 |

---

## Notes

- Use `stripe.Webhook.construct_event()` for webhook verification — never trust raw payload
- `STRIPE_WEBHOOK_SECRET` is different per endpoint (use CLI secret for local dev: `stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe`)
- `db/base.py` already has a `try/except` guard for the Phase 5 Subscription import — remove the guard once the model is implemented
