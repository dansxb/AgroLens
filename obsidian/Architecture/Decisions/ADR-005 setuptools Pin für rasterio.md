# ADR-005: setuptools auf <81 pinnen für rasterio-Build

**Status:** Entschieden  
**Datum:** 2026-05-13

---

## Problem

`rasterio==1.3.*` hat kein pre-built Wheel für ARM64 (linux/aarch64). pip baut es aus dem Source-Code.

Beim Source-Build erstellt pip eine **isolierte Build-Umgebung** in `/tmp/pip-build-env-xxx/`. In dieser Umgebung versucht rasterios `setup.py` `import pkg_resources` — und schlägt fehl, weil `setuptools>=81` `pkg_resources` aus den isolierten Envs entfernt hat.

Fehlermeldung: `ModuleNotFoundError: No module named 'pkg_resources'`

## Ursache

- setuptools 81.0.0 (April 2025) entfernte `pkg_resources` als Standard-Bestandteil in isolierten pip-Build-Umgebungen
- `pip install --upgrade setuptools pip` zieht 82.x, was den Build bricht
- Kein pre-built ARM64-Wheel für rasterio 1.3.x → immer Source-Build auf ARM64

## Fix

```dockerfile
# FALSCH — holt setuptools 82+ → bricht rasterio-Build
RUN pip install --upgrade setuptools pip && \

# RICHTIG — pinnt unter die brechende Version
RUN pip install "setuptools<81" pip --upgrade && \
```

## Konsequenz

- `Dockerfile` builder stage muss immer `"setuptools<81"` pinnen solange rasterio 1.3.x verwendet wird
- Checker-Checkliste: Dockerfile-Review muss diese Zeile prüfen
- Gilt für alle Services die das Backend-Dockerfile verwenden: backend, celery_worker, celery_beat
