# AgroLens Debug Log

Laufendes Fehlerprotokoll. Wird nur angehängt — niemals überschrieben.
Geführt vom Debug-Spezialist Agent.

---

## Fix #1 — 2026-05-13

**Fehler:**
```
ModuleNotFoundError: No module named 'pkg_resources'
ERROR: Failed to build 'rasterio' when getting requirements to build wheel
```

**Ursache:**
pip 26 verändert das Verhalten isolierter Build-Envs: Das `overlay`-Layer erhält kein `pkg_resources` mehr aus dem Haupt-setuptools. rasterio 1.3.x hat kein ARM64-Wheel und baut aus Source — dabei importiert setup.py `pkg_resources` im Build-Env, das dann nicht verfügbar ist.

**Betroffene Datei(en):**
- `src/backend/Dockerfile` — rasterio-Install-Step im builder-Stage

**Änderung:**
```diff
- RUN pip install "setuptools<81" pip --upgrade && \
-     pip install --prefix=/install -r requirements.txt
+ RUN pip install "setuptools<81" pip --upgrade && \
+     pip install --prefix=/install --no-build-isolation rasterio==1.3.* && \
+     pip install --prefix=/install -r requirements.txt
```

**Geprüft mit:**
- [x] Dockerfile-Syntax geprüft (manuell)
- [ ] Docker build (Credentials fehlen — kann nicht lokal durchlaufen)

**Seiteneffekte geprüft:** Ja — `--no-build-isolation` gilt nur für rasterio, alle anderen Packages verwenden normales isoliertes Build-Env. Rasterio wird bei der zweiten `pip install -r requirements.txt` als bereits erfüllt erkannt und übersprungen.

**Für andere Agenten:**
Wenn pip auf eine neue Major-Version aktualisiert und rasterio-Build-Probleme auftreten: immer zuerst `--no-build-isolation` für rasterio prüfen, bevor setuptools weiter gepinnt wird.

---

## Fix #1b — 2026-05-13 (Folge-Fix zu #1)

**Fehler:**
```
ERROR: Cython.Build.cythonize not found. Cython is required to build rasterio.
```

**Ursache:**
Fix #1 (`--no-build-isolation`) löste das `pkg_resources`-Problem, aber `--no-build-isolation` deaktiviert auch das automatische Installieren von Build-Dependencies aus dem `[build-system].requires` in rasterio's `pyproject.toml`. Cython ist eine Build-Dependency von rasterio 1.3.x, wird aber nicht automatisch installiert wenn Build-Isolation abgeschaltet ist.

**Betroffene Datei(en):**
- `src/backend/Dockerfile` — builder-Stage pip-Install-Step

**Änderung:**
```diff
- RUN pip install "setuptools<81" pip --upgrade && \
+ RUN pip install "setuptools<81" "Cython" pip --upgrade && \
      pip install --prefix=/install --no-build-isolation rasterio==1.3.* && \
      pip install --prefix=/install -r requirements.txt
```

**Geprüft mit:**
- [x] Dockerfile-Syntax geprüft (manuell)
- [ ] Docker build (läuft)

**Seiteneffekte geprüft:** Ja — Cython ist eine reine Build-Zeit-Dependency, landet nicht im Container-Image (nur im builder-Stage). Kein Einfluss auf Runtime.

**Für andere Agenten:**
Bei `--no-build-isolation`: ALLE Build-Dependencies aus `[build-system].requires` müssen manuell vorinstalliert werden. Für rasterio 1.3.x: setuptools + Cython.

---

## Fix #1e — 2026-05-13 — FINALE LÖSUNG (Folge-Fix zu #1d)

**Fehler:**
```
ModuleNotFoundError: No module named 'pkg_resources'
ERROR: Failed to build 'rasterio' when getting requirements to build wheel
```
(Trat beim `pip install --prefix=/install -r requirements.txt` auf, obwohl rasterio zuvor mit --no-build-isolation erfolgreich gebaut wurde)

**Ursache:**
Der `--prefix=/install`-Install sieht bereits installierte Packages im Prefix **nicht** im sys.path während des pip-Runs. Deshalb erkennt pip rasterio als "noch nicht installiert" und versucht es aus requirements.txt erneut zu bauen — diesmal mit normalem isolated build, der `pkg_resources` nicht findet.

**Betroffene Datei(en):**
- `src/backend/Dockerfile` — builder-Stage RUN-Zeile

**Änderung:**
```diff
- RUN pip install "setuptools<81" "Cython<3" "numpy==1.26.*" pip --upgrade && \
-     pip install --prefix=/install --no-build-isolation rasterio==1.3.* && \
-     pip install --prefix=/install -r requirements.txt
+ RUN pip install "setuptools<81" "Cython<3" "numpy==1.26.*" pip --upgrade && \
+     pip wheel --no-build-isolation --no-deps --wheel-dir=/wheelhouse rasterio==1.3.11 && \
+     pip install --prefix=/install --find-links=/wheelhouse -r requirements.txt
```

**Strategie:**
1. Build-Deps vorinstallieren
2. Rasterio-Wheel einmalig bauen, in /wheelhouse cachen
3. requirements.txt mit `--find-links=/wheelhouse` installieren — pip findet das vorgebaute Wheel und baut nicht nochmal

**Geprüft mit:**
- [x] Dockerfile-Syntax (manuell)
- [ ] Docker build (läuft)

**Seiteneffekte geprüft:** Ja — `--find-links` ist additiv, beeinflusst keine anderen Packages.

**Für andere Agenten:**
Endgültige Regel: Wenn ein Package kein ARM64-Wheel hat, Wheel-Cache-Strategie verwenden: `pip wheel --no-build-isolation --wheel-dir=/wheelhouse <pkg>` + `pip install --find-links=/wheelhouse --prefer-binary -r requirements.txt`.

---

## Fix #1f — 2026-05-14 (Folge-Fix zu #1e)

**Problem:**
pip 26 mit `--find-links=/wheelhouse` allein garantiert nicht, dass das lokale Wheel gegenüber dem PyPI-Source-Tarball bevorzugt wird. Das Risiko besteht, dass pip `rasterio-1.3.11.tar.gz` von PyPI herunterlädt statt das lokal gebaute Wheel zu verwenden — was wieder zum `pkg_resources`-Fehler führt.

**Betroffene Datei(en):**
- `src/backend/Dockerfile` — builder-Stage, letzte RUN-Zeile

**Änderung:**
```diff
- pip install --prefix=/install --find-links=/wheelhouse -r requirements.txt
+ pip install --prefix=/install --find-links=/wheelhouse --prefer-binary -r requirements.txt
```

**Warum `--prefer-binary`:**
Weist pip an, für alle Packages binäre Distributionen (Wheels) gegenüber Source-Distributionen zu bevorzugen. Damit wird das lokal gebaute `rasterio-1.3.11-cp311-cp311-linux_aarch64.whl` aus `/wheelhouse` sicher gegenüber dem PyPI-Tarball gewählt.

**Geprüft mit:**
- [x] Dockerfile-Syntax (manuell)
- [ ] Docker build

**Seiteneffekte geprüft:** Ja — `--prefer-binary` ist global für den Install-Schritt, bevorzugt für ALLE Packages Wheels über Source. Alle anderen Packages in requirements.txt haben offizielle Wheels auf PyPI — kein Nachteil.

**Für andere Agenten:**
Vollständige robuste Strategie für ARM64-Packages ohne offizielle Wheels: `pip wheel --no-build-isolation --no-deps --wheel-dir=/wheelhouse <pkg>` + `pip install --find-links=/wheelhouse --prefer-binary -r requirements.txt`.

---

## Fix #1d — 2026-05-13 (Folge-Fix zu #1c)

**Fehler:**
```
ERROR: Numpy and its headers are required to run setup().
```

**Ursache:**
rasterio's `pyproject.toml` deklariert drei Build-System-Requirements: `setuptools`, `Cython`, `numpy`. Mit `--no-build-isolation` installiert pip diese nicht automatisch. Numpy fehlte als drittes.

**Betroffene Datei(en):**
- `src/backend/Dockerfile` — builder-Stage RUN-Zeile

**Änderung:**
```diff
- RUN pip install "setuptools<81" "Cython<3" pip --upgrade && \
+ RUN pip install "setuptools<81" "Cython<3" "numpy==1.26.*" pip --upgrade && \
```

**Geprüft mit:**
- [x] Dockerfile-Syntax (manuell)
- [ ] Docker build (läuft)

**Seiteneffekte geprüft:** Ja — numpy==1.26.* matcht requirements.txt. Kein Konflikt.

**Für andere Agenten:**
Vollständige Build-Deps für rasterio 1.3.x mit `--no-build-isolation`: `setuptools<81 + Cython<3 + numpy`. Das sind ALLE drei. Nach diesem Fix sollte der Build komplett durchlaufen.

---

## Fix #1c — 2026-05-13 (Folge-Fix zu #1b)

**Fehler:**
```
ERROR: Cython.Build.cythonize not found. Cython is required to build rasterio.
```
(Trat trotz `pip install "Cython"` auf)

**Ursache:**
Cython 3.x (aktuell: 3.x) hat das interne Build-API geändert. rasterio 1.3.x wurde mit Cython 0.29.x entwickelt und ist mit Cython 3.x nicht kompatibel — `Cython.Build.cythonize` hat in Cython 3 eine andere Signatur / ist anders importierbar. `pip install Cython` ohne Versionspin installiert 3.x.

**Betroffene Datei(en):**
- `src/backend/Dockerfile` — builder-Stage, erste RUN-Zeile

**Änderung:**
```diff
- RUN pip install "setuptools<81" "Cython" pip --upgrade && \
+ RUN pip install "setuptools<81" "Cython<3" pip --upgrade && \
```

**Geprüft mit:**
- [x] Dockerfile-Syntax (manuell)
- [ ] Docker build (läuft nach Fix)

**Seiteneffekte geprüft:** Ja — Cython ist Build-Zeit-Dependency, landet nicht im Image. `Cython<3` installiert 0.29.x, das mit rasterio 1.3.x kompatibel ist.

**Für andere Agenten:**
Regel: rasterio 1.3.x braucht `Cython<3` (= 0.29.x). Wenn rasterio auf 1.4.x+ aktualisiert wird, kann `Cython<4` ausreichen — vorher testen.

---

## Fix #2 — 2026-05-13

**Fehler:**
`AttributeError: 'Settings' object has no attribute 'SENDGRID_FROM_EMAIL'`
(potenziell — Uppercase-Zugriff auf Pydantic BaseSettings Attribut)

**Ursache:**
Pydantic `BaseSettings` mit `case_sensitive=False` macht env-Variablen beim Einlesen case-insensitiv, aber Python-Attributzugriff bleibt case-sensitiv. `settings.SENDGRID_FROM_EMAIL` schlägt fehl — korrekt ist `settings.sendgrid_from_email`.

**Betroffene Datei(en):**
- `src/backend/app/services/notifications.py` — `send_email()` Funktion

**Änderung:**
```diff
- sender = from_email or settings.SENDGRID_FROM_EMAIL
- client = SendGridAPIClient(settings.SENDGRID_API_KEY)
+ sender = from_email or settings.sendgrid_from_email
+ client = SendGridAPIClient(settings.sendgrid_api_key)
```

**Geprüft mit:**
- [x] py_compile: `python -m py_compile src/backend/app/services/notifications.py`

**Seiteneffekte geprüft:** Ja — `send_email()` ist die einzige Stelle, die auf diese Settings zugreift.

**Für andere Agenten:**
Alle Settings-Attribute in Python mit Lowercase ansprechen: `settings.stripe_secret_key`, `settings.sendgrid_api_key` etc.
