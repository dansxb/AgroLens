# ADR-004: Supabase JWT Verification mit python-jose

**Status:** Entschieden  
**Datum:** 2026-05-13

---

## Kontext

Das Backend muss Supabase-ausgestellte JWTs verifizieren. Drei Werte aus dem Supabase-Dashboard sind relevant:
- **Anon Key** (`sb_publishable_...`) — Frontend-Only, für Supabase-Client
- **Service Role Key** (`sb_secret_...`) — Backend-Only, Admin-Zugriff auf Supabase
- **JWT Secret** — HMAC-Schlüssel zum Verifizieren von Access Tokens

## Problem (aufgetreten in der Session)

Der JWT Secret wurde mit dem Service Role Key verwechselt. Das Service Role JWT (`eyJ...`) wurde als `SUPABASE_JWT_SECRET` eingetragen — das führt zu 401-Fehlern bei jedem Login, weil `jwt.decode()` ein falsches HMAC-Secret verwendet.

## Die drei Werte im Überblick

| Variable | Typ | Gefunden unter |
|---|---|---|
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `sb_publishable_...` | Settings → API → anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | `sb_secret_...` | Settings → API → service_role key |
| `SUPABASE_JWT_SECRET` | Base64-String (kein `eyJ`, kein `sb_`) | Settings → API → JWT Settings → JWT Secret |

## Entscheidung

`verify_supabase_jwt()` in `app/core/security.py` verwendet HS256 mit `settings.supabase_jwt_secret` als HMAC-Key:

```python
payload = jwt.decode(
    token,
    settings.supabase_jwt_secret,   # muss der rohe Base64-Signing-Key sein
    algorithms=["HS256"],
    options={"verify_aud": False}
)
```

Der `sub`-Claim im Payload ist die kanonische User-UUID für alle DB-Foreign-Keys.

## Konsequenz

- `SUPABASE_JWT_SECRET` ist NIEMALS das Service Role JWT — es ist der kurze Base64-Signing-Key
- Neuer Entwickler? → Supabase Dashboard → Settings → API → JWT Settings → "JWT Secret" (nicht "service_role")
- Wenn Auth mit 401 fehlschlägt: ersten Schritt prüfen ob der richtige Wert eingetragen ist
