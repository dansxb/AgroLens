# ADR-002: AsyncSession nie zwischen Tasks teilen

**Status:** Entschieden  
**Datum:** 2026-05-13

---

## Kontext

FastAPI mit SQLAlchemy 2.0 AsyncSession. Celery Workers brauchen DB-Zugriff für Background Tasks.

## Entscheidungen

### 1. `expire_on_commit=False` auf `async_sessionmaker`

Ohne dieses Flag werden alle ORM-Attribute nach `await session.commit()` ungültig (expired). Zugriffe danach lösen einen Lazy-Load aus — der in async-Kontext zu `MissingGreenlet`-Fehlern führt.

```python
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

### 2. Dependency-Name: `get_db`, nicht `get_async_db`

Im Projekt heißt die FastAPI-Dependency `get_db` (aus `app.db.session`). `get_async_db` existiert nicht.

### 3. Celery Workers nutzen `SessionLocal` (sync)

Celery läuft nicht im asyncio-Loop. Worker-Tasks verwenden die synchrone `SessionLocal`, nicht `AsyncSessionLocal`.

```python
# In Celery Tasks:
from app.db.session import SessionLocal
with SessionLocal() as db:
    ...
```

### 4. Relationships immer mit `selectinload()` laden

Niemals auf ungeladene Relationships nach einem `await` zugreifen — löst Lazy-Load-Fehler aus.

```python
result = await session.execute(
    select(Field).options(selectinload(Field.vegetation_indices))
)
```

## Konsequenz

- Keine `AsyncSession` über Task-Grenzen hinweg teilen
- Kein `get_async_db` in neuen Route-Dateien verwenden
- Celery-Tasks: immer sync `SessionLocal`
