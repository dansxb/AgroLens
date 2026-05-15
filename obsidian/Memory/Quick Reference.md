# Quick Reference — AgroLens

Dichte Lookup-Tabelle für häufig benötigte Infos. Wird bei jedem Session-Start automatisch geladen.

---

## Kritische Import-Regeln

```python
# PgEnum — IMMER so, nie sa.Enum
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
MY_ENUM = PgEnum("a", "b", name="mytype", create_type=False)

# relationship() — KEIN comment= kwarg
user = relationship("User")           # ✅
user = relationship("User", comment="x")  # ❌ TypeError

# Async DB dependency
from app.db.session import get_db    # ✅  (nicht get_async_db)

# togeojson import
import * as toGeoJSON from "@mapbox/togeojson"   # ✅
import { toGeoJSON } from "@mapbox/togeojson"    # ❌
```

---

## Env-Variablen (backend/.env)

| Variable | Status | Wert |
|---|---|---|
| `SECRET_KEY` | ✅ gesetzt | 64-char hex |
| `SUPABASE_URL` | ✅ gesetzt | `https://feoohtmphywquwzonpwq.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ gesetzt | *(in .env, nicht hier)* |
| `SUPABASE_JWT_SECRET` | ✅ gesetzt | base64 string |
| `CELERY_BROKER_URL` | ✅ gesetzt | `redis://localhost:6379/0` |
| `SENTINEL_HUB_*` | ❌ fehlt | Für Bildgebungspipeline |
| `AWS_*` | ❌ fehlt | Für S3-Storage |
| `SENDGRID_API_KEY` | ❌ fehlt | Für E-Mail-Benachrichtigungen |
| `STRIPE_*` | ❌ fehlt | Phase 5 |

## Env-Variablen (frontend/.env)

| Variable | Status |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ gesetzt |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ gesetzt |
| `NEXT_PUBLIC_MAPBOX_TOKEN` | ✅ gesetzt |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | ❌ Phase 5 |

---

## Migrations-Reihenfolge

| Nr. | Datei | Inhalt |
|---|---|---|
| 0001 | `create_users_farms_fields` | User, Farm, Field + PostGIS |
| 0002 | `create_imagery_pipeline_tables` | SatelliteScene, VegetationIndex, NdviComposite |
| 0003 | `add_flik_to_fields` | flik Spalte auf fields |
| 0004 | `create_phase3_tables` | ManagementZone, Prescription, SprayingRecord |
| 0005 | `create_notification_preferences` | NotificationPreference |
| 0006 | `create_api_keys` | ApiKey |
| 0007 | _Phase 5_ | Subscription (noch nicht gebaut) |

---

## Wichtige Modell-Felder

```python
# VegetationIndex
VegetationIndex.created_at   # ✅  (NICHT computed_at)

# Field
Field.flik                   # nullable String(18), FLIK-Nummer
Field.area_ha                # Numeric(12, 4)

# ApiKey
ApiKey.key_prefix            # String(8), erste 8 Zeichen
ApiKey.key_hash              # bcrypt-Hash, nie Plaintext
# key-Format: agro_sk_<32 random chars>
```

---

## Dockerfile-Regel: rasterio auf ARM64

rasterio 1.3.x hat kein ARM64-Wheel → baut aus Source. pip 26+ erstellt isolierte Build-Envs ohne `pkg_resources` im Overlay → `ModuleNotFoundError`. Fix im builder-Stage:

```dockerfile
RUN pip install "setuptools<81" pip --upgrade && \
    pip install --prefix=/install --no-build-isolation rasterio==1.3.* && \
    pip install --prefix=/install -r requirements.txt
```

`--no-build-isolation` nur für rasterio → nutzt pkg_resources aus der Hauptumgebung.

---

## Docker-Befehle

```bash
cd "/Users/danielschaller/Desktop/CS Haus & Garten/Winter…/Claude Agents/src"

# Alles starten
docker compose up --build

# Migrations laufen lassen (einmalig nach erstem Build)
docker compose exec backend alembic upgrade head

# Logs einzelner Services
docker compose logs -f backend
docker compose logs -f celery_worker

# DB-Zugriff
docker compose exec postgres psql -U agrolens -d agrolens_dev

# Kompletter Reset
docker compose down -v && docker compose up --build
```

---

## Service-URLs (lokal)

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |

---

## Agents und ihre Outputs

| Agent | Schreibt nach |
|---|---|
| CEO | `docs/ceo-strategy.md` |
| Planner | `docs/development-plan.md` |
| Software Developer | Code + `docs/dev-log.md` + `docs/blockers.md` |
| Checker | `docs/checker-review.md` |
| Landwirt Validator | `docs/landwirt-validator-report.md` |

**Phase-Freigabe nur wenn:** Checker = APPROVED **und** Landwirt Validator = FREIGEGEBEN
