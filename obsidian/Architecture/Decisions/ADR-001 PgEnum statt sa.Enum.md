# ADR-001: PgEnum statt sa.Enum für PostgreSQL-Enums

**Status:** Entschieden  
**Datum:** 2026-05-13

---

## Kontext

SQLAlchemy bietet zwei Wege, PostgreSQL-native Enums zu definieren:
- `sa.Enum("a", "b", name="mytype", create_type=False)`
- `PgEnum("a", "b", name="mytype", create_type=False)` aus `sqlalchemy.dialects.postgresql`

## Problem

`sa.Enum` feuert ein `_on_table_create`-Event **unabhängig von `create_type=False`**. Das führt bei jedem Migrations-Rerun zu `psycopg2.errors.DuplicateObject` — der Enum-Typ existiert bereits in der DB und `sa.Enum` versucht ihn trotzdem erneut zu erstellen.

## Entscheidung

**Immer `PgEnum` aus `sqlalchemy.dialects.postgresql` verwenden.**

```python
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
MY_ENUM = PgEnum("value_a", "value_b", name="mytype", create_type=False)
```

`PgEnum` respektiert `create_type=False` korrekt und versucht keinen erneuten `CREATE TYPE`.

## Konsequenz

- Alle Modell-Dateien: ausschließlich `PgEnum`
- Checker prüft dies bei jedem Code-Review
- `sa.Enum` ist im Projekt verboten
