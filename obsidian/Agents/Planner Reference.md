# Planner Agent — Technical Reference

*API contracts, integration patterns, and stack reference for planning tasks.*

---

## Sentinel Hub Process API (Sentinel-2 NDVI)

**Endpoint:** `POST https://sh.dataspace.copernicus.eu/api/v1/process`

**Auth:** OAuth2 client credentials → `https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token`

**Complete request body for NDVI:**
```json
{
  "input": {
    "bounds": {
      "bbox": [13.8, 45.8, 13.9, 45.9],
      "properties": { "crs": "http://www.opengis.net/gml/srs/epsg.xml#4326" }
    },
    "data": [{
      "type": "sentinel-2-l2a",
      "dataFilter": {
        "timeRange": { "from": "2024-06-01T00:00:00Z", "to": "2024-06-30T23:59:59Z" },
        "maxCloudCoverage": 30
      }
    }]
  },
  "output": {
    "width": 512, "height": 512,
    "responses": [{ "identifier": "default", "format": { "type": "image/tiff" } }]
  },
  "evalscript": "//VERSION=3\nfunction setup() {\n  return {\n    input: [{ bands: ['B04','B08'], units: 'REFLECTANCE' }],\n    output: { id: 'default', bands: 1, sampleType: SampleType.FLOAT32 }\n  };\n}\nfunction evaluatePixel(sample) {\n  let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);\n  return [ndvi];\n}"
}
```

**Key notes:**
- B04 = Red (~665nm), B08 = NIR (~842nm) — NDVI = (NIR−Red)/(NIR+Red)
- `SampleType.FLOAT32` → values −1 to +1 as float GeoTIFF
- Use `"resx": 10, "resy": 10` for 10m native Sentinel-2 resolution instead of width/height

---

## Stripe Subscription Integration

**Flow:**
1. Create Product + Price (recurring) in Stripe dashboard → get `price_id`
2. `POST /v1/customers` → create customer, store `customer_id`
3. `POST /v1/checkout/sessions` with `mode: "subscription"` → redirect to `session.url`
4. Handle webhooks → provision/update access in DB
5. `POST /v1/billing_portal/sessions` → self-service management

**Critical webhooks to handle:**

| Event | Action |
|---|---|
| `checkout.session.completed` | Save customer_id, activate subscription |
| `invoice.paid` | Continue provisioning each cycle |
| `invoice.payment_failed` | Warn user, redirect to portal |
| `customer.subscription.updated` | Handle plan changes, past_due |
| `customer.subscription.deleted` | Revoke access immediately |

**Webhook validation (Python):**
```python
event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
# raises SignatureVerificationError if tampered
```

**DB access model:** Store `(stripe_customer_id, subscription_status, current_period_end)`. Grant access if `current_period_end > now()` AND `status in ('active', 'trialing')`.

---

## Supabase JWT Claims Reference

**Always present in every access token:**

| Claim | Type | Notes |
|---|---|---|
| `sub` | string | User UUID — use as FK in all tables |
| `email` | string | User email |
| `role` | string | `"authenticated"` for logged-in users |
| `aud` | string | `"authenticated"` |
| `exp` / `iat` | number | Expiry / issued-at Unix timestamps |
| `aal` | string | `"aal1"` (password) or `"aal2"` (MFA) |
| `session_id` | string | Unique per login |
| `is_anonymous` | boolean | True for anon sessions |

**Optional but useful:**

| Claim | Use |
|---|---|
| `app_metadata` | Server-side only — store subscription plan/tier here (not accessible by client JS) |
| `user_metadata` | User-editable profile data |

**AgroLens pattern:** Use `sub` as the canonical user ID. Store plan in `app_metadata.plan` (set via Supabase Admin API in webhook handler after Stripe checkout). RLS: `auth.uid() = user_id` and `auth.jwt() -> 'app_metadata' ->> 'plan'` for plan gating.
