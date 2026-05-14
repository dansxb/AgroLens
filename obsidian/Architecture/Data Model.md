# Data Model

## Entity Relationship (simplified)

```
User (Supabase UUID)
 └── Farm (1:N)
      └── Field (1:N)  ← flik: String(18), area_ha, geometry (POLYGON)
           ├── SatelliteScene (1:N)  ← s3 keys for raw bands
           ├── VegetationIndex (1:N) ← mean_value, index_type (ndvi|ndre)
           ├── PipelineRun (1:N)
           ├── ManagementZone (1:N)  ← zone_label enum, geometry (MULTIPOLYGON)
           ├── Prescription (1:N)   ← application_type, base_rate_l_ha, disclaimer
           │    └── SprayingRecord (1:N) ← §67 PflSchG documentation
           └── NotificationPreference (via user)

User
 └── ApiKey (1:N)        ← key_hash (bcrypt), key_prefix, revoked
 └── Subscription (1:1)  ← Phase 5
```

## Migrations

| Migration | Tables | Notes |
|-----------|--------|-------|
| 0001 | users, farms, fields | Phase 1 core |
| 0002 | satellite_scenes, vegetation_indices, pipeline_runs | Phase 2 imagery |
| 0003 | fields.flik column | FLIK-Nummer for InVeKoS |
| 0004 | management_zones, prescriptions, spraying_records | Phase 3 |
| 0005 | notification_preferences | Phase 4.5 |
| 0006 | api_keys | Phase 4.6 |

## Key design decisions

- **PgEnum** (`sqlalchemy.dialects.postgresql.ENUM`) — NOT `sa.Enum`, which causes `DuplicateObject` errors on reruns
- `create_type=False` on all PgEnum instances — migration creates the type, model doesn't
- **PostGIS geometry** added via `SELECT AddGeometryColumn(...)` in migrations, NOT inline in `op.create_table()`
- `SprayingRecord.prescription_id` uses `ondelete="SET NULL"` — records survive prescription deletion (legal requirement)
