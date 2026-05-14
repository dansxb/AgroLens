# Software Developer Agent — Technical Reference

*Patterns, gotchas, and code snippets for the AgroLens stack.*

---

## FastAPI + AsyncSession (SQLAlchemy 2.0)

**Engine setup:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@host/db",
    pool_size=10, max_overflow=20,
    pool_pre_ping=True,   # test connections before use
    echo=False
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
# expire_on_commit=False is CRITICAL — avoids lazy load errors after commit
```

**Dependency injection pattern:**
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

**Query patterns:**
```python
# Get by PK
obj = await session.get(MyModel, pk_value)

# Select with filter
result = await session.execute(select(MyModel).where(MyModel.id == id))
item = result.scalar_one_or_none()

# Eager load to avoid N+1
result = await session.execute(
    select(Field).options(selectinload(Field.vegetation_indices))
)
```

**Critical rules:**
- Never share an `AsyncSession` across concurrent tasks (not thread-safe)
- Use `selectinload()` or `joinedload()` for relationships — never access unloaded after `await`
- Call `await engine.dispose()` on app shutdown

---

## Celery + Redis — Production Config

```python
# celeryconfig.py
broker_url = "redis://redis:6379/0"
result_backend = "redis://redis:6379/1"

task_acks_late = True               # ack after completion, not before
task_reject_on_worker_lost = True   # requeue if worker dies mid-task
worker_prefetch_multiplier = 1      # fair distribution for long tasks
worker_max_tasks_per_child = 1000   # prevent memory leaks
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
result_expires = 3600               # 1 hour TTL on results
```

**Task definition with retry:**
```python
@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_ndvi(self, field_id: str):
    try:
        ...
    except Exception as exc:
        raise self.retry(exc=exc)
```

**Queue routing** (separate queues for compute vs notifications):
```python
task_routes = {
    "tasks.imagery.*": {"queue": "compute"},
    "tasks.notifications.*": {"queue": "critical"},
}
```

---

## Next.js 14/15 App Router — Data Fetching

**Server component (no cache by default in v15):**
```tsx
export default async function FieldPage({ params }) {
  const data = await fetch(`${API_URL}/fields/${params.id}`, { cache: 'no-store' })
  const field = await data.json()
  return <FieldMap field={field} />
}
```

**With revalidation:**
```tsx
const data = await fetch(url, { next: { revalidate: 300 } }) // re-fetch every 5min
```

**Parallel fetching (avoid waterfall):**
```tsx
const [field, ndvi] = await Promise.all([getField(id), getNDVI(id)])
```

**Client-side SWR (for interactive data):**
```tsx
'use client'
import useSWR from 'swr'
const { data, isLoading } = useSWR(`/api/fields/${id}/ndvi`, fetcher)
```

**Key change in v15:** `fetch` is NOT cached by default (changed from v13/14). Always explicit `next: { revalidate }` or `cache: 'force-cache'` for caching.

---

## Mapbox GL JS — GeoJSON Layer Pattern

```javascript
map.on('load', () => {
  // Add source
  map.addSource('fields', { type: 'geojson', data: geojsonData })

  // Fill layer with NDVI color ramp
  map.addLayer({
    id: 'field-fill',
    type: 'fill',
    source: 'fields',
    paint: {
      'fill-color': [
        'interpolate', ['linear'], ['get', 'ndvi'],
        0.0, '#d73027',   // red = low NDVI
        0.5, '#ffffbf',   // yellow = medium
        1.0, '#1a9850'    // green = high
      ],
      'fill-opacity': 0.7
    }
  })

  // Outline layer
  map.addLayer({
    id: 'field-outline', type: 'line', source: 'fields',
    paint: { 'line-color': '#ffffff', 'line-width': 2 }
  })
})

// Update data without recreating layer
map.getSource('fields').setData(newGeoJSON)
```

**Rules:**
- All `addSource`/`addLayer` calls inside `map.on('load', ...)`
- Sources must be added before layers that reference them
- Insert layer below labels: `map.addLayer({...}, 'road-label')`

---

## AgroLens-Specific Gotchas (hard-learned)

| Bug | Wrong | Correct |
|---|---|---|
| SQLAlchemy enum | `sa.Enum(create_type=False)` | `PgEnum` from `sqlalchemy.dialects.postgresql` |
| `relationship()` kwarg | `relationship(..., comment=...)` | No `comment=` on relationship — only on `mapped_column()` |
| DB dependency name | `get_async_db` | `get_db` |
| togeojson import | `import { toGeoJSON }` | `import * as toGeoJSON from "@mapbox/togeojson"` |
| next-pwa cache path | `require("next-pwa/cache")` | Remove — v5 has no sub-path |
| JWT secret value | Paste the service role JWT | Paste the raw signing secret (plain string, not `eyJ...`) |
| Workers import ml/ | Missing volume mount | Add `./ml:/app/ml` to celery_worker + celery_beat volumes |
