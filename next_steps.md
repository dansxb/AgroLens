# AgroLens — Next Steps & Open Tasks

*Last updated: 2026-05-15*

---

## 1. Stripe konfigurieren (blockiert Billing-Seite)

### 1a. Publishable Key ins Frontend eintragen

Datei: `src/frontend/.env`

```
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_51TX...
```

Wo: [Stripe Dashboard → Developers → API Keys](https://dashboard.stripe.com/test/apikeys) → "Publishable key" (beginnt mit `pk_test_`)

---

### 1b. 6 Produkte in Stripe anlegen → Price IDs ins Backend

Datei: `src/backend/.env` — diese 6 Zeilen befüllen:

```
STRIPE_PRICE_ID_STARTER_MONTHLY=price_...
STRIPE_PRICE_ID_STARTER_ANNUAL=price_...
STRIPE_PRICE_ID_FARMER_MONTHLY=price_...
STRIPE_PRICE_ID_FARMER_ANNUAL=price_...
STRIPE_PRICE_ID_PRO_MONTHLY=price_...
STRIPE_PRICE_ID_PRO_ANNUAL=price_...
```

Schritte:
1. [Stripe Dashboard → Product catalog → + Add product](https://dashboard.stripe.com/test/products)
2. Erstelle 3 Produkte: **Starter**, **Farmer**, **Pro**
3. Für jedes Produkt 2 Preise: monatlich + jährlich
   - Starter: 29 €/Mo · 290 €/Jahr
   - Farmer: 79 €/Mo · 790 €/Jahr
   - Pro: 199 €/Mo · 1.990 €/Jahr
4. `price_xxx...` IDs kopieren → in `.env` eintragen
5. Danach: `docker restart agrolens_backend agrolens_celery_worker agrolens_celery_beat`

---

### 1c. Stripe Billing Portal aktivieren (einmalig)

1. [Stripe Dashboard → Settings → Billing → Customer portal](https://dashboard.stripe.com/test/settings/billing/portal)
2. "Activate test link" klicken
3. Aktivieren: Abo-Wechsel ✅ · Kündigung ✅ · Rechnungshistorie ✅
4. Speichern

Ohne das schlägt der "Abonnement verwalten"-Button fehl.

---

### 1d. Stripe Webhook einrichten

**Für lokale Tests — Stripe CLI:**
```bash
brew install stripe/stripe-cli/stripe
stripe login
stripe listen --forward-to localhost:8000/api/v1/webhooks/stripe
```
Den ausgegebenen `whsec_...` Secret in `src/backend/.env` → `STRIPE_WEBHOOK_SECRET` eintragen.

**Für Production:**
1. [Stripe Dashboard → Developers → Webhooks → + Add endpoint](https://dashboard.stripe.com/webhooks)
2. URL: `https://api.agrolens.io/api/v1/webhooks/stripe`
3. Events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

---

## 2. Sentinel Hub (Satellitenbilder — Kernfunktion der App)

Datei: `src/backend/.env`

```
SENTINEL_HUB_CLIENT_ID=...
SENTINEL_HUB_CLIENT_SECRET=...
SENTINEL_HUB_INSTANCE_ID=...
```

Schritte:
1. Account erstellen: [https://www.sentinel-hub.com/](https://www.sentinel-hub.com/) — kostenloser Trial verfügbar
2. [Dashboard → User Settings → OAuth clients → + Add](https://apps.sentinel-hub.com/dashboard/#/account/settings) → Client ID + Secret kopieren
3. [Dashboard → Configurations → + Create new](https://apps.sentinel-hub.com/dashboard/#/configurations) → Layer konfigurieren → Instance ID kopieren

---

## 3. AWS S3 (Bildspeicher)

Datei: `src/backend/.env`

```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET_NAME=agrolens-imagery-dev
AWS_S3_REGION=eu-central-1
```

Schritte:
1. [AWS Console → IAM → Users → Create user](https://console.aws.amazon.com/iam/)
2. Policy: `AmazonS3FullAccess` (oder custom Policy nur für diesen Bucket)
3. Access Key erstellen → in `.env` eintragen
4. Bucket anlegen:
   ```bash
   aws s3 mb s3://agrolens-imagery-dev --region eu-central-1
   ```

---

## 4. SendGrid (E-Mail-Benachrichtigungen)

Datei: `src/backend/.env`

```
SENDGRID_API_KEY=SG...
SENDGRID_FROM_EMAIL=noreply@agrolens.io
```

1. [https://sendgrid.com/](https://sendgrid.com/) — kostenloser Plan bis 100 Mails/Tag
2. Settings → API Keys → Create API Key → "Full Access"
3. Sender-Verifizierung: deine From-E-Mail-Adresse bestätigen

---

## 5. Monitor Secret Key (Sicherheit)

Datei: `src/backend/.env`

```
MONITOR_SECRET_KEY=...
```

Generieren:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 6. Sentry (Fehler-Monitoring — optional)

Backend: `src/backend/.env` → `SENTRY_DSN`
Frontend: `src/frontend/.env` → `NEXT_PUBLIC_SENTRY_DSN`

1. [https://sentry.io/](https://sentry.io/) → zwei Projekte anlegen: Python/FastAPI + Next.js
2. DSN-URLs kopieren und eintragen

---

## 7. Rechtliche Pflichtseiten (vor Launch)

Gesetzlich vorgeschrieben (§5 TMG + DSGVO):

| Seite | Route | Status |
|---|---|---|
| Impressum | `/impressum` | ❌ fehlt |
| Datenschutzerklärung | `/datenschutz` | ❌ fehlt |
| AGB | `/agb` | ❌ fehlt |

Empfehlung: Anwalt oder Dienst wie [e-recht24.de](https://www.e-recht24.de/) nutzen.

---

## 8. App testen (nach Stripe-Setup)

Reihenfolge:
1. `http://localhost:3000/signup` → Account erstellen
2. Login → Dashboard prüfen
3. Feld anlegen → Felder-Seite
4. Einstellungen aufrufen
5. Abrechnung → Plan-Upgrade testen (Stripe Test-Karte: `4242 4242 4242 4242`)

---

## Was bereits funktioniert

| Service | Status |
|---|---|
| Supabase Auth (Login/Signup) | ✅ |
| PostgreSQL + PostGIS | ✅ |
| Redis + Celery | ✅ |
| Mapbox (Karten) | ✅ |
| Stripe Secret Key + Webhook Secret | ✅ gesetzt |
| Supabase Auth-Migration zu `@supabase/ssr` | ✅ heute gefixt |
| Alle 7 Datenbankmigrationen | ✅ |
| Backend-Routen (Felder, Farms, Users, Billing) | ✅ |
