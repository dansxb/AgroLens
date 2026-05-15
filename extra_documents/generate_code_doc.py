"""
Generates AgroLens_Code_Erklaerung.docx — a developer overview document.
Run: python generate_code_doc.py
"""

from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ── Page margins ──────────────────────────────────────────────────────────────
section = doc.sections[0]
section.top_margin    = Cm(2.5)
section.bottom_margin = Cm(2.5)
section.left_margin   = Cm(2.8)
section.right_margin  = Cm(2.8)

# ── Colour palette ────────────────────────────────────────────────────────────
GREEN      = RGBColor(0x16, 0xa3, 0x4a)   # agrolens-600
DARK_GREEN = RGBColor(0x05, 0x2e, 0x16)   # agrolens-950
GRAY       = RGBColor(0x6b, 0x72, 0x80)
CODE_BG    = RGBColor(0xf8, 0xfa, 0xfc)
BLACK      = RGBColor(0x11, 0x18, 0x27)

# ── Helpers ───────────────────────────────────────────────────────────────────

def h1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after  = Pt(6)
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(22)
    run.font.color.rgb = DARK_GREEN
    return p

def h2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(16)
    run.font.color.rgb = GREEN
    return p

def h3(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(3)
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(13)
    run.font.color.rgb = BLACK
    return p

def body(text):
    p = doc.add_paragraph(text)
    p.paragraph_format.space_after = Pt(6)
    for run in p.runs:
        run.font.size = Pt(11)
        run.font.color.rgb = BLACK
    return p

def bullet(text, level=0):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.left_indent = Cm(0.5 + level * 0.8)
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    run.font.size = Pt(11)
    run.font.color.rgb = BLACK
    return p

def code_block(lines, lang=""):
    """Render a monospaced code block with a light-gray background."""
    # Add a single paragraph per block, newline-joined
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after  = Pt(10)
    p.paragraph_format.left_indent  = Cm(0.5)

    # Gray shading on the paragraph
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  "F1F5F9")
    pPr.append(shd)

    run = p.add_run("\n".join(lines))
    run.font.name   = "Courier New"
    run.font.size   = Pt(9)
    run.font.color.rgb = RGBColor(0x1e, 0x29, 0x3b)
    return p

def divider():
    p = doc.add_paragraph("─" * 80)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(12)
    for run in p.runs:
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0xd1, 0xd5, 0xdb)
    return p

def callout(label, text):
    """A highlighted info box."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after  = Pt(8)
    p.paragraph_format.left_indent  = Cm(0.5)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  "DCFCE7")
    pPr.append(shd)
    r1 = p.add_run(f"{label}  ")
    r1.bold = True
    r1.font.size = Pt(10)
    r1.font.color.rgb = DARK_GREEN
    r2 = p.add_run(text)
    r2.font.size = Pt(10)
    r2.font.color.rgb = BLACK

# ══════════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ══════════════════════════════════════════════════════════════════════════════

title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
title_p.paragraph_format.space_before = Pt(60)
r = title_p.add_run("AgroLens")
r.bold = True
r.font.size = Pt(40)
r.font.color.rgb = DARK_GREEN

subtitle_p = doc.add_paragraph()
subtitle_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r2 = subtitle_p.add_run("Code-Erklärung & Architektur-Übersicht")
r2.font.size = Pt(18)
r2.font.color.rgb = GREEN

date_p = doc.add_paragraph()
date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
date_p.paragraph_format.space_before = Pt(20)
r3 = date_p.add_run("Mai 2026  ·  Erstellt von Claude Sonnet 4.6")
r3.font.size = Pt(11)
r3.font.color.rgb = GRAY

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 1. WAS IST AGROLENS?
# ══════════════════════════════════════════════════════════════════════════════

h1("1. Was ist AgroLens?")
body(
    "AgroLens ist eine Präzisionslandwirtschafts-Software (SaaS) für deutsche Landwirte. "
    "Das System lädt automatisch Satellitendaten des Copernicus Sentinel-2-Programms herunter, "
    "berechnet Vegetationsindizes (NDVI, NDRE), teilt Felder in Bewirtschaftungszonen ein und "
    "erzeugt daraus variable Ausbringungskarten (VRA — Variable Rate Application). "
    "Diese können direkt in ISOBUS-fähige Traktoren und Feldspritzen geladen werden."
)

h2("Das große Bild — von Satellit bis Traktor")
body("Der komplette Datenfluss in einem Satz:")
code_block([
    "Sentinel-2 Satellit",
    "    → Sentinel Hub API (Rohdaten abrufen)",
    "    → NDVI/NDRE berechnen (NumPy)",
    "    → k-Means Clustering (scikit-learn) → Bewirtschaftungszonen",
    "    → Prescription Engine → Ausbringungsmengen pro Zone",
    "    → ISOBUS TASKDATA.XML + Shapefile + PDF erzeugen",
    "    → S3-Speicher (AWS) → Farmer lädt herunter",
    "    → USB-Stick → ISOBUS-Maschine auf dem Feld",
])

h2("Tech-Stack im Überblick")
bullet("Backend:    FastAPI (Python) + SQLAlchemy 2 + PostgreSQL/PostGIS + Celery")
bullet("Frontend:   Next.js 14 + TypeScript + Tailwind CSS + Mapbox GL JS")
bullet("ML/Bildver: NumPy, rasterio, scikit-learn (k-Means), Sentinel Hub API")
bullet("Infrastruk: Docker Compose, Redis, AWS S3, Supabase Auth, Stripe")
bullet("Monitoring: Sentry (Fehler-Tracking), SendGrid (E-Mail-Alerts)")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 2. VERZEICHNISSTRUKTUR
# ══════════════════════════════════════════════════════════════════════════════

h1("2. Verzeichnisstruktur — Was liegt wo?")
body(
    "Das Repository ist in drei Hauptbereiche aufgeteilt: Backend (Python/FastAPI), "
    "Frontend (Next.js) und ML (Machine Learning Pipeline). Alle drei laufen in "
    "separaten Docker-Containern, kommunizieren aber über gemeinsame Datenbank und Redis."
)

code_block([
    "src/",
    "├── backend/                   Python FastAPI Anwendung",
    "│   ├── app/",
    "│   │   ├── api/routes/        REST-Endpunkte (fields, farms, billing …)",
    "│   │   ├── core/              Konfiguration, Security, Plan-Limits",
    "│   │   ├── db/                Datenbankverbindung, Basis-Klassen",
    "│   │   ├── models/            SQLAlchemy ORM-Modelle (Tabellen)",
    "│   │   ├── schemas/           Pydantic-Schemas (Request/Response-Typen)",
    "│   │   ├── services/          Geschäftslogik (Stripe, Prescription …)",
    "│   │   └── worker/tasks/      Celery Background-Tasks",
    "│   └── alembic/versions/      Datenbankmigrationen (0001–0007)",
    "│",
    "├── frontend/                  Next.js 14 Anwendung",
    "│   ├── app/",
    "│   │   ├── (auth)/            Login, Signup, Passwort-Reset",
    "│   │   ├── (dashboard)/       Geschützter Bereich nach Login",
    "│   │   │   ├── fields/        Feldverwaltung",
    "│   │   │   ├── billing/       Abonnement & Preise",
    "│   │   │   └── settings/      Kontoeinstellungen",
    "│   │   └── wie-es-funktioniert/ Öffentliche Erklärungsseite",
    "│   ├── components/            Wiederverwendbare UI-Bausteine",
    "│   ├── hooks/                 React Hooks (useAuth)",
    "│   └── lib/api/               API-Client-Funktionen",
    "│",
    "└── ml/                        Machine-Learning Pipeline",
    "    ├── indices/               NDVI/NDRE Berechnung",
    "    ├── delineation/           k-Means Zoneneinteilung",
    "    └── prescription/          Ausbringungsmengen-Engine",
])

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 3. DATENBANK-MODELLE
# ══════════════════════════════════════════════════════════════════════════════

h1("3. Datenbank-Modelle — Wie die Daten gespeichert werden")
body(
    "Die Datenbank ist PostgreSQL mit PostGIS-Erweiterung (für Geodaten wie Feldgrenzen). "
    "Jede Tabelle ist als Python-Klasse definiert (SQLAlchemy ORM). "
    "Änderungen an der Datenbankstruktur werden über Alembic-Migrationen versioniert."
)

h2("Beziehungen zwischen den Tabellen")
code_block([
    "User (Landwirt)",
    "  └── Farm (Betrieb)          Ein User hat einen oder mehrere Betriebe",
    "        └── Field (Feld)      Jeder Betrieb hat mehrere Felder (mit GPS-Grenzen)",
    "              ├── SatelliteScene     Satellitenaufnahmen für dieses Feld",
    "              ├── VegetationIndex    Berechnete NDVI/NDRE-Werte",
    "              ├── PipelineRun        Protokoll: wann wurde analysiert?",
    "              ├── ManagementZone     k-Means Zonen (Zone A, B, C …)",
    "              └── Prescription       Ausbringungskarte (kg/ha pro Zone)",
    "",
    "User",
    "  ├── ApiKey            API-Schlüssel für externe Systeme",
    "  ├── NotificationPref  E-Mail-Benachrichtigungseinstellungen",
    "  └── Subscription      Stripe-Abonnement (Basis/Starter/Farmer/Pro)",
])

h2("Beispiel: Das Field-Modell (src/backend/app/models/field.py)")
body(
    "Ein Feld hat eine Geometrie (GPS-Polygon), einen Namen, einen Feldfruchtyp "
    "und eine berechnete Fläche in Hektar. Die Geometrie wird von PostGIS verwaltet."
)
code_block([
    "class Field(Base):",
    '    __tablename__ = "fields"',
    "",
    "    id:           UUID           # eindeutige ID",
    "    farm_id:      UUID           # Fremdschlüssel → Farm",
    "    name:         str            # z.B. 'Schlag Nord'",
    "    crop_type:    str | None     # z.B. 'Winterweizen'",
    "    geometry:     Geometry       # GPS-Polygon (PostGIS)",
    "    area_ha:      float          # berechnet via ST_Area()",
    "    flik_number:  str | None     # InVeKoS-Feldkennnummer",
    "    created_at:   datetime       # Erstellungsdatum",
])

callout("Warum PostGIS?",
        "Normale Datenbanken können nicht mit GPS-Koordinaten rechnen. PostGIS ist eine "
        "Erweiterung für PostgreSQL, die Geodaten versteht: Flächen berechnen, "
        "Überlappungen prüfen, Koordinaten transformieren — alles direkt in der Datenbank.")

h2("Beispiel: Das Subscription-Modell (Phase 5)")
body(
    "Jeder Nutzer hat genau ein Abonnement. Neue Nutzer starten automatisch auf dem "
    "kostenlosen Basis-Plan (kein Datenbank-Eintrag nötig — wird als Standard angenommen)."
)
code_block([
    "class Subscription(Base):",
    '    __tablename__ = "subscriptions"',
    "",
    "    user_id:                UUID      # 1:1 mit User verknüpft",
    "    plan:                   str       # 'basis' | 'starter' | 'farmer' | 'pro'",
    "    status:                 str       # 'active' | 'past_due' | 'canceled' …",
    "    stripe_customer_id:     str       # Stripe-interne Kunden-ID",
    "    stripe_subscription_id: str       # Stripe-interne Abo-ID",
    "    current_period_end:     datetime  # Wann läuft das Abo ab?",
])

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 4. AUTHENTIFIZIERUNG
# ══════════════════════════════════════════════════════════════════════════════

h1("4. Authentifizierung — Wer darf was?")
body(
    "AgroLens nutzt Supabase als Authentifizierungsdienst. Supabase verwaltet Passwörter, "
    "E-Mail-Verifikation und OAuth (Google). Nach dem Login erhält der Nutzer einen "
    "JWT (JSON Web Token) — einen signierten Beweis seiner Identität."
)

h2("Login-Ablauf")
code_block([
    "1. Nutzer gibt E-Mail + Passwort auf /login ein",
    "2. Frontend sendet Daten an Supabase",
    "3. Supabase prüft Passwort und gibt JWT zurück",
    "4. JWT wird im Browser gespeichert (LocalStorage)",
    "5. Jede API-Anfrage schickt den JWT im Header mit:",
    "   Authorization: Bearer eyJhbGciOiJIUzI1NiIs...",
    "6. Backend prüft die JWT-Signatur (mit SUPABASE_JWT_SECRET)",
    "7. Ist der JWT gültig → Anfrage wird bearbeitet",
    "8. Ist er ungültig/abgelaufen → HTTP 401 Unauthorized",
])

h2("JWT-Prüfung im Backend (app/core/security.py)")
body(
    "Das Backend prüft jeden eingehenden JWT selbst — ohne Supabase anzufragen. "
    "Möglich, weil JWT kryptografisch signiert sind und die Signatur lokal geprüft werden kann."
)
code_block([
    "def verify_supabase_jwt(token: str) -> dict:",
    "    # Dekodiert und prüft den JWT",
    "    payload = jwt.decode(",
    "        token,",
    "        key=settings.supabase_jwt_secret,  # geheimer Schlüssel aus .env",
    "        algorithms=['HS256'],",
    "        options={'verify_exp': True},        # Ablaufdatum prüfen",
    "    )",
    "    return payload  # enthält user_id ('sub'), email, etc.",
])

h2("Dependency Injection (app/api/deps.py)")
body(
    "FastAPI nutzt 'Dependencies' — wiederverwendbare Funktionen, die vor jedem "
    "Route-Handler ausgeführt werden. get_current_user() stellt sicher, dass "
    "jeder geschützte Endpunkt nur mit gültigem JWT erreichbar ist."
)
code_block([
    "async def get_current_user(payload = Depends(get_current_user_payload),",
    "                           db = Depends(get_db)) -> User:",
    "    user_id = payload.get('sub')          # UUID aus dem JWT",
    "    user = await db.get(User, user_id)    # Nutzer aus DB laden",
    "    if user is None:",
    "        user = User(id=user_id, ...)      # Erstmaliger Login → anlegen",
    "        db.add(user)",
    "    return user",
    "",
    "# Verwendung in einem Route-Handler:",
    "@router.get('/fields')",
    "async def list_fields(current_user = Depends(get_current_user)):",
    "    # current_user ist garantiert ein eingeloggter User",
    "    ...",
])

callout("Sicherheitsprinzip:",
        "Kein Route-Handler vertraut dem Aufrufer blind. Durch Depends(get_current_user) "
        "wird die Authentifizierung automatisch bei jedem Aufruf geprüft — "
        "man kann es nicht vergessen.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 5. SATELLITEN-PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

h1("5. Satelliten-Pipeline — Von Rohdaten zu NDVI")
body(
    "Das Herzstück von AgroLens: Die automatische Analyse von Sentinel-2-Satellitendaten. "
    "Die Pipeline läuft täglich als Hintergrundprozess (Celery Task) und verarbeitet "
    "alle registrierten Felder."
)

h2("Was ist NDVI?")
body(
    "NDVI steht für Normalized Difference Vegetation Index. Pflanzen reflektieren "
    "rotes Licht (NIR = Near Infrared) stark, wenn sie gesund sind. Kranke oder "
    "gestresste Pflanzen reflektieren weniger. Der NDVI macht diesen Unterschied messbar."
)
code_block([
    "# NDVI-Formel (src/ml/indices/ndvi.py)",
    "def compute_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:",
    "    # nir = Nahinfrarot-Band (Band 8 bei Sentinel-2)",
    "    # red = Rot-Band (Band 4 bei Sentinel-2)",
    "    denominator = nir + red",
    "    denominator = np.where(denominator == 0, np.nan, denominator)",
    "    ndvi = (nir - red) / denominator",
    "    return ndvi.astype(np.float32)",
    "",
    "# Ergebnis: Array mit Werten zwischen -1 und +1",
    "# -1 bis 0:   Wasser, nackte Erde, Gebäude",
    "#  0 bis 0.3: wenig/kein Bewuchs, Stress",
    "#  0.3 - 0.6: mäßige Vegetation",
    "#  0.6 - 1.0: gesunde, dichte Vegetation",
])

h2("Schritt 1: Bilder von Sentinel Hub laden (app/worker/tasks/imagery.py)")
body(
    "Sentinel Hub ist ein kommerzieller Dienst, der Zugang zu Copernicus-Satellitendaten bietet. "
    "AgroLens fragt täglich per API an, ob neue Aufnahmen für jedes Feld vorliegen."
)
code_block([
    "@celery_app.task",
    "def fetch_sentinel_imagery(field_id: str):",
    "    # 1. Feldgrenzen aus DB laden",
    "    field = db.get(Field, field_id)",
    "    bbox = field.geometry.bounds   # Begrenzungsrahmen des Feldes",
    "",
    "    # 2. Sentinel Hub API anfragen",
    "    response = sentinelhub.process(",
    "        bbox=bbox,",
    "        time_interval=last_30_days,",
    "        bands=['B04', 'B08', 'SCL'],  # Rot, NIR, Wolkenmaske",
    "    )",
    "",
    "    # 3. Rohbild auf S3 speichern",
    "    s3.upload(response.image, f'scenes/{field_id}/{date}.tif')",
    "",
    "    # 4. SatelliteScene-Eintrag in DB erstellen",
    "    db.add(SatelliteScene(field_id=field_id, s3_key=..., date=...))",
])

h2("Schritt 2: Wolken maskieren und Komposit erstellen (src/ml/indices/composite.py)")
body(
    "Sentinel-2 liefert auch eine Wolkenklassifizierung (SCL = Scene Classification Layer). "
    "Bewölkte Pixel werden maskiert (auf NaN gesetzt) und dann mehrere Aufnahmen "
    "zu einem wolkenfreien Gesamtbild zusammengeführt (Median-Komposit)."
)
code_block([
    "def apply_scl_cloud_mask(scl: np.ndarray) -> np.ndarray:",
    "    # SCL-Werte: 4=Vegetation, 5=nackter Boden, 6=Wasser, 8-10=Wolken",
    "    valid_classes = {4, 5, 6, 7, 11}   # alles AUSSER Wolken",
    "    mask = np.isin(scl, list(valid_classes))",
    "    return mask   # True = gültiger Pixel, False = Wolke/Schatten",
    "",
    "def compute_composite(ndvi_scenes: list, method='median') -> np.ndarray:",
    "    # Mehrere Aufnahmen stapeln und Median nehmen",
    "    # NaN-Werte (Wolken) werden automatisch ignoriert",
    "    stack = np.stack(ndvi_scenes, axis=0)   # [N, Höhe, Breite]",
    "    return np.nanmedian(stack, axis=0)       # pro Pixel: Median aller N Aufnahmen",
])

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 6. K-MEANS ZONENEINTEILUNG
# ══════════════════════════════════════════════════════════════════════════════

h1("6. k-Means Zoneneinteilung — Das Feld aufteilen")
body(
    "Nachdem der NDVI-Wert für jeden Punkt des Feldes bekannt ist, teilt AgroLens "
    "das Feld in Bewirtschaftungszonen ein. Bereiche mit ähnlichem NDVI-Wert "
    "kommen in dieselbe Zone."
)

h2("Was ist k-Means Clustering?")
body(
    "k-Means ist ein mathematisches Verfahren, das Datenpunkte in k Gruppen einteilt, "
    "sodass die Punkte innerhalb einer Gruppe möglichst ähnlich sind. "
    "AgroLens verwendet k=2 bis k=5 Zonen (je nach Feldgröße und Nutzerplan)."
)
code_block([
    "# src/ml/delineation/kmeans.py (vereinfacht)",
    "from sklearn.cluster import KMeans",
    "import numpy as np",
    "",
    "def delineate_zones(ndvi: np.ndarray, n_zones: int = 3):",
    "    # 1. Nur gültige (nicht-NaN) Pixel verwenden",
    "    valid_mask = ~np.isnan(ndvi)",
    "    valid_pixels = ndvi[valid_mask].reshape(-1, 1)",
    "",
    "    # 2. k-Means anwenden",
    "    kmeans = KMeans(n_clusters=n_zones, random_state=42, n_init=10)",
    "    labels = kmeans.fit_predict(valid_pixels)",
    "",
    "    # 3. Zonen nach NDVI-Mittelwert sortieren (Zone 0 = niedrigster NDVI)",
    "    zone_means = [valid_pixels[labels == i].mean() for i in range(n_zones)]",
    "    order = np.argsort(zone_means)         # aufsteigend sortiert",
    "    sorted_labels = np.argsort(order)[labels]",
    "",
    "    # 4. Zonenkarte: jedem Pixel seine Zone zuweisen",
    "    zone_map = np.full(ndvi.shape, -1, dtype=int)",
    "    zone_map[valid_mask] = sorted_labels",
    "    return zone_map",
    "",
    "# Ergebnis: 2D-Array wie das Feld",
    "# Wert 0 = Zone A (niedrigster NDVI = meister Stress)",
    "# Wert 1 = Zone B (mittlerer NDVI)",
    "# Wert 2 = Zone C (höchster NDVI = gesündeste Zone)",
])

callout("Analogie:",
        "Stellen Sie sich vor, Sie malen ein Feld auf Papier, wobei jeder Punkt "
        "eine Farbe bekommt, die seinem NDVI-Wert entspricht. k-Means sucht dann "
        "automatisch die k Farbbereiche, die am besten zusammenpassen — "
        "ähnlich wie ein Maler, der Farben mischt.")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 7. PRESCRIPTION ENGINE
# ══════════════════════════════════════════════════════════════════════════════

h1("7. Prescription Engine — Ausbringungsmengen berechnen")
body(
    "Nachdem das Feld in Zonen eingeteilt wurde, berechnet die Prescription Engine "
    "für jede Zone die empfohlene Ausbringungsmenge. Die Grundlage sind agronomisch "
    "validierte Multiplikatoren — keine KI, sondern Fachwissen in Tabellenform."
)

h2("Die Multiplikatoren-Tabelle (src/ml/prescription/engine.py)")
body(
    "Für jeden Pflanzenschutzmitteltyp gibt es eine Tabelle mit Multiplikatoren "
    "je Vegetationszone. Zone A (niedrigster NDVI = höchster Stress) "
    "bekommt mehr, Zone C weniger."
)
code_block([
    "# Multiplier-Tabelle: Low → Medium-Low → Medium → Medium-High → Very High",
    "_MULTIPLIERS = {",
    "    'fungicide':   [0.60, 1.00, 1.30, 1.50, 1.70],",
    "    'herbicide':   [0.70, 1.00, 1.20, 1.40, 1.60],",
    "    'insecticide': [0.50, 1.00, 1.50, 1.80, 2.00],",
    "}",
    "",
    "# Beispiel mit 3 Zonen und Fungizid, Grundmenge 2.0 L/ha:",
    "#   Zone A (Low NDVI):    2.0 × 0.60 = 1.20 L/ha  ← wenig Fungizid nötig",
    "#   Zone B (Medium NDVI): 2.0 × 1.00 = 2.00 L/ha  ← Standardmenge",
    "#   Zone C (High NDVI):   2.0 × 1.30 = 2.60 L/ha  ← mehr Schutz nötig",
])

body(
    "Wichtig: Für k Zonen werden immer die ersten k Einträge der Tabelle verwendet. "
    "Bei 3 Zonen: [0.60, 1.00, 1.30]. Bei 2 Zonen: [0.60, 1.00]. "
    "Das stellt sicher, dass weniger Zonen immer die konservativere Strategie wählen."
)

h2("Berechnung und Ergebnis")
code_block([
    "def compute_prescription(application_type, base_rate_l_ha, zone_names):",
    "    n_zones = len(zone_names)",
    "    multiplier_row = _MULTIPLIERS[application_type]",
    "    selected = multiplier_row[:n_zones]   # erste n Einträge",
    "",
    "    floor = base_rate_l_ha * 0.5          # Mindestmenge: 50% der Grundmenge",
    "    zones = []",
    "    for name, multiplier in zip(zone_names, selected):",
    "        rate = max(0.0, round(base_rate_l_ha * multiplier, 4))",
    "        below_floor = rate < floor",
    "        if below_floor:",
    "            logger.warning('Rate %s L/ha unter Mindestmenge', rate)",
    "        zones.append(ZonePrescription(",
    "            zone_name=name,",
    "            multiplier=multiplier,",
    "            rate_l_ha=rate,",
    "            below_minimum_floor=below_floor,",
    "        ))",
    "",
    "    return PrescriptionResult(",
    "        zones=zones,",
    "        mean_rate_l_ha=...,",
    "        savings_pct=...,     # Einsparung vs. Pauschalausbringung",
    "        disclaimer=DISCLAIMER_DE,   # gesetzlich vorgeschriebener Hinweis",
    "    )",
])

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 8. EXPORT
# ══════════════════════════════════════════════════════════════════════════════

h1("8. Export — Von der Karte zur Maschine")
body(
    "Die Ausbringungskarte wird in drei Formaten exportiert, um verschiedene "
    "Maschinentypen und Arbeitsabläufe zu unterstützen."
)

h2("ISOBUS TASKDATA.XML (ISO 11783-10)")
body(
    "Das wichtigste Format: Eine XML-Datei, die von ISOBUS-fähigen Traktoren und "
    "Spritzen direkt gelesen werden kann. ISOBUS ist ein internationaler Standard, "
    "den fast alle modernen Landmaschinen unterstützen."
)
code_block([
    "<!-- Vereinfachtes TASKDATA.XML Beispiel -->",
    "<ISO11783_TaskData>",
    "  <TSK A='TSK1' B='Schlag Nord Fungizid' D='1'>",
    "    <TZN A='TZN1'>  <!-- Zone A: 1.20 L/ha -->",
    "      <PTN A='PTN1' D='0' E='1200' />   <!-- Ausbringmenge in ml/ha -->",
    "    </TZN>",
    "    <TZN A='TZN2'>  <!-- Zone B: 2.00 L/ha -->",
    "      <PTN A='PTN2' D='0' E='2000' />",
    "    </TZN>",
    "  </TSK>",
    "</ISO11783_TaskData>",
])

h2("Shapefile (.SHP)")
body(
    "Ein geografisches Vektorformat, das die Zonengrenzen als GPS-Polygone enthält. "
    "GIS-fähige Systeme (Trimble, John Deere Operations Center etc.) können dieses "
    "Format direkt importieren."
)

h2("PDF-Bericht")
body(
    "Für Betriebe ohne digitale Steuergeräte: Ein lesbarer Bericht mit "
    "Zonenkarte, Ausbringungsmengen und dem gesetzlich vorgeschriebenen "
    "Agronomendisclaimer (§67 PflSchG)."
)

callout("§67 PflSchG:",
        "Das Pflanzenschutzgesetz verpflichtet Landwirte, jede Ausbringung zu dokumentieren. "
        "AgroLens erzeugt automatisch ein konformes Protokoll. "
        "Alle Exporte enthalten außerdem den Hinweis: "
        "'Die Applikationsmengen basieren auf agronomischen Faustregeln und wurden nicht "
        "für jeden Kulturtyp validiert. Bitte prüfen Sie die Empfehlungen mit einem Berater.'")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 9. FRONTEND
# ══════════════════════════════════════════════════════════════════════════════

h1("9. Frontend — Was der Landwirt sieht")
body(
    "Das Frontend ist mit Next.js 14 gebaut — einem React-Framework, das serverseitiges "
    "Rendering und clientseitige Navigation kombiniert. "
    "Die Benutzeroberfläche ist vollständig auf Deutsch."
)

h2("Seitenstruktur")
code_block([
    "Öffentliche Seiten (kein Login nötig):",
    "  /                        Landing Page (Produktvorstellung)",
    "  /wie-es-funktioniert     Erklärungsseite für Landwirte",
    "  /login                   Login-Formular",
    "  /signup                  Registrierung",
    "",
    "Geschützte Seiten (Login erforderlich):",
    "  /dashboard               Feldübersicht mit Mapbox-Karte",
    "  /fields                  Liste aller Felder",
    "  /fields/new              Neues Feld einzeichnen",
    "  /fields/[id]             Felddetail mit NDVI-Chart",
    "  /billing                 Abonnement & Preise",
    "  /settings                Kontoeinstellungen, API-Keys",
])

h2("API-Kommunikation (src/frontend/lib/api/client.ts)")
body(
    "Das Frontend kommuniziert mit dem Backend über einen zentralen API-Client. "
    "Er fügt automatisch den Supabase-JWT-Token zu jeder Anfrage hinzu."
)
code_block([
    "// lib/api/client.ts",
    "const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'",
    "",
    "class ApiClient {",
    "  async get<T>(path: string): Promise<T> {",
    "    const token = await getSupabaseToken()    // JWT aus Browser-Session",
    "    const response = await fetch(`${API_BASE_URL}${path}`, {",
    "      headers: { Authorization: `Bearer ${token}` }",
    "    })",
    "    if (!response.ok) throw new ApiError(response.status, ...)",
    "    return response.json()",
    "  }",
    "",
    "  async post<T>(path: string, body: unknown): Promise<T> { ... }",
    "}",
    "",
    "export const apiClient = new ApiClient()",
])

h2("Authentifizierungs-Hook (src/frontend/hooks/useAuth.ts)")
body(
    "useAuth() ist ein React Hook — eine Funktion, die in jedem Komponenten "
    "aufgerufen werden kann, um den aktuellen Login-Status zu erhalten. "
    "Sie reagiert automatisch auf Änderungen (Login/Logout)."
)
code_block([
    "// Verwendung in einer Seite:",
    'function MyPage() {',
    '  const { user, loading, signOut } = useAuth()',
    '  if (loading) return <Spinner />',
    '  if (!user) return <Redirect to="/login" />',
    '  return <div>Willkommen, {user.email}</div>',
    '}',
    "",
    "// Was useAuth intern macht:",
    "// 1. Supabase-Session beim Start laden (getSession)",
    "// 2. Auf Login/Logout-Events lauschen (onAuthStateChange)",
    "// 3. user, session, loading als State zurückgeben",
    "// 4. signOut() macht window.location.href = '/login'",
    "//    (Hard-Navigation, damit Session-Cookie gelöscht wird)",
])

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 10. STRIPE BILLING
# ══════════════════════════════════════════════════════════════════════════════

h1("10. Stripe Billing — Abonnements & Bezahlung")
body(
    "AgroLens hat vier Tarife: Basis (kostenlos), Starter, Farmer und Pro. "
    "Stripe übernimmt die gesamte Zahlungsabwicklung — AgroLens speichert "
    "keine Kreditkartendaten, das macht alles Stripe."
)

h2("Wie ein Upgrade funktioniert")
code_block([
    "Nutzer klickt 'Upgrade auf Farmer' auf der Billing-Seite",
    "    ↓",
    "Frontend: createCheckoutSession({ plan: 'farmer', interval: 'monthly' })",
    "    ↓",
    "Backend POST /billing/checkout:",
    "  1. Stripe Customer erstellen (oder vorhandenen nehmen)",
    "  2. stripe.checkout.Session.create() → gibt URL zurück",
    "    ↓",
    "Frontend: window.location.href = url  (Weiterleitung zu Stripe)",
    "    ↓",
    "Nutzer gibt Kreditkartendaten auf Stripe-Seite ein",
    "    ↓",
    "Stripe sendet Webhook → POST /webhooks/stripe",
    "  Event: checkout.session.completed",
    "  AgroLens aktualisiert Subscription in DB → plan = 'farmer'",
    "    ↓",
    "Nutzer wird zu /billing?success=1 weitergeleitet",
])

h2("Webhook-Sicherheit (app/api/routes/webhooks.py)")
body(
    "Stripe sendet nach jeder Zahlung eine HTTP-Anfrage an AgroLens (Webhook). "
    "Um sicherzustellen, dass diese Anfrage wirklich von Stripe kommt und nicht "
    "von jemandem, der einen Plan gratis freischalten will, prüft AgroLens "
    "die kryptografische Signatur jeder Webhook-Anfrage."
)
code_block([
    "@router.post('/webhooks/stripe')",
    "async def stripe_webhook(request: Request, db = Depends(get_db)):",
    "    raw_body = await request.body()          # WICHTIG: Rohdaten, nicht JSON!",
    "    sig = request.headers.get('stripe-signature')",
    "",
    "    # Signatur prüfen — schlägt fehl, wenn Anfrage gefälscht ist",
    "    event = stripe.Webhook.construct_event(",
    "        raw_body, sig, settings.stripe_webhook_secret",
    "    )  # wirft Exception bei ungültiger Signatur",
    "",
    "    # Ereignis verarbeiten",
    "    if event['type'] == 'checkout.session.completed':",
    "        await handle_checkout_completed(event['data']['object'], db)",
    "    elif event['type'] == 'customer.subscription.deleted':",
    "        await handle_subscription_deleted(...)",
    "    # ... weitere Event-Typen",
])

h2("Plan-Limits durchsetzen (app/core/limits.py)")
body(
    "Sobald ein Nutzer ein neues Feld anlegen möchte, prüft das Backend "
    "automatisch, ob sein Plan das erlaubt. Das passiert transparent "
    "im Hintergrund — der Nutzer sieht nur eine Fehlermeldung mit "
    "dem Hinweis, seinen Plan zu upgraden."
)
code_block([
    "PLAN_LIMITS = {",
    "    'basis':   PlanLimits(max_fields=1,    max_ha=15.0,  prescriptions_allowed=False),",
    "    'starter': PlanLimits(max_fields=5,    max_ha=100.0, prescriptions_allowed=True),",
    "    'farmer':  PlanLimits(max_fields=50,   max_ha=500.0, prescriptions_allowed=True),",
    "    'pro':     PlanLimits(max_fields=None, max_ha=None,  prescriptions_allowed=True),",
    "}",
    "",
    "# In POST /fields — BEVOR das Feld gespeichert wird:",
    "await check_field_count_limit(current_user, db)",
    "await check_ha_limit(current_user, new_area_ha, db)",
    "# → wirft HTTP 402 Payment Required, wenn Limit überschritten",
])

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 11. HINTERGRUNDPROZESSE
# ══════════════════════════════════════════════════════════════════════════════

h1("11. Hintergrundprozesse — Celery & Redis")
body(
    "Die Satelliten-Pipeline, E-Mail-Alerts und andere zeitaufwändige Aufgaben "
    "laufen nicht direkt im API-Server, sondern als Hintergrundprozesse in Celery. "
    "Redis dient dabei als Warteschlange (Broker): Aufgaben werden dort eingereiht "
    "und von Celery-Workern abgearbeitet."
)

h2("Warum Hintergrundprozesse?")
code_block([
    "Problem: NDVI-Analyse dauert 10-30 Sekunden",
    "",
    "OHNE Celery:",
    "  Nutzer fragt API an → Server blockiert 30 Sek → Browser-Timeout",
    "",
    "MIT Celery:",
    "  Nutzer fragt API an → Server antwortet sofort: 'Analyse gestartet'",
    "  → Celery Worker arbeitet die Analyse im Hintergrund",
    "  → Nutzer bekommt E-Mail wenn fertig",
])

h2("Der tägliche Zeitplan (app/worker/celery_app.py)")
code_block([
    "# Automatisch ausgeführte Tasks",
    "beat_schedule = {",
    "    'fetch-imagery-daily': {",
    "        'task': 'app.worker.tasks.imagery.fetch_all_fields',",
    "        'schedule': crontab(hour=3, minute=0),  # täglich um 3:00 Uhr",
    "    },",
    "    'check-stress-alerts': {",
    "        'task': 'app.worker.tasks.notifications.check_stress_alerts',",
    "        'schedule': crontab(hour=7, minute=0),  # täglich um 7:00 Uhr",
    "    },",
    "}",
])

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 12. ALLES ZUSAMMEN
# ══════════════════════════════════════════════════════════════════════════════

h1("12. Alles zusammen — Der komplette Ablauf")
body(
    "Hier ist der vollständige Weg einer Analyse — von der Feldregistrierung "
    "bis zur fertigen Ausbringungskarte im Traktor:"
)

code_block([
    "PHASE 1: Registrierung & Feldanlage",
    "  Landwirt registriert sich → Supabase erstellt Account",
    "  → JWT wird ausgestellt",
    "  → Landwirt zeichnet Feld auf Mapbox-Karte ein",
    "  → Frontend sendet GeoJSON-Polygon an POST /fields",
    "  → Backend: Farmbesitz prüfen, Plan-Limit prüfen, Fläche via PostGIS berechnen",
    "  → Field-Eintrag in Datenbank erstellt",
    "",
    "PHASE 2: Satellitenaufnahme (automatisch, täglich 3:00 Uhr)",
    "  → Celery Beat startet fetch_all_fields Task",
    "  → Für jedes Feld: Sentinel Hub API anfragen",
    "  → Rohdaten (GeoTIFF) auf S3 speichern",
    "  → SatelliteScene-Eintrag in DB erstellen",
    "",
    "PHASE 3: NDVI-Analyse (direkt nach Download)",
    "  → compute_ndvi(nir_band, red_band) → NDVI-Array",
    "  → apply_scl_cloud_mask() → Wolken ausblenden",
    "  → compute_composite() → Monatskomposit (wolkenfrei)",
    "  → VegetationIndex-Eintrag in DB: mean_ndvi, min_ndvi, max_ndvi",
    "",
    "PHASE 4: Stresskontrolle & Alert (täglich 7:00 Uhr)",
    "  → check_stress_alerts Task startet",
    "  → Für jedes Feld: aktuellen NDVI mit Vorwoche vergleichen",
    "  → NDVI-Abfall > Schwellwert? → SendGrid-E-Mail an Landwirt",
    "",
    "PHASE 5: Ausbringungskarte erstellen (auf Anfrage)",
    "  → Landwirt klickt 'Karte erstellen' im Dashboard",
    "  → POST /fields/{id}/prescriptions",
    "  → check_prescription_limit() → Plan-Check",
    "  → delineate_zones(ndvi, n_zones=3) → k-Means Clustering",
    "  → compute_prescription('fungicide', 2.0, zones)",
    "  → Prescription + ManagementZone-Einträge in DB",
    "",
    "PHASE 6: Export & Download",
    "  → Landwirt klickt 'ISOBUS herunterladen'",
    "  → GET /fields/{id}/prescriptions/{pid}/export?format=taskdata",
    "  → generate_taskdata_xml() → XML-Datei",
    "  → Datei auf S3 hochladen → S3-Link zurückgeben",
    "  → Landwirt lädt Datei herunter, kopiert auf USB-Stick",
    "  → USB-Stick in Traktor → ISOBUS liest Karte → Spritze regelt Menge",
])

divider()

h2("Sicherheitsschichten")
bullet("Jeder API-Aufruf: JWT-Authentifizierung (Supabase)")
bullet("Datenzugriff: Nutzer sieht nur eigene Felder (farm.user_id == current_user.id)")
bullet("Plan-Limits: HTTP 402 bei Überschreitung, vor jedem DB-Insert geprüft")
bullet("Webhooks: HMAC-Signaturprüfung gegen Manipulation")
bullet("Daten: Ausschließlich auf EU-Servern (S3 eu-central-1, DSGVO)")
bullet("Secrets: Nur in .env-Dateien, nie in Git-Repository")

doc.add_page_break()

# ══════════════════════════════════════════════════════════════════════════════
# 13. PHASEN DER ENTWICKLUNG
# ══════════════════════════════════════════════════════════════════════════════

h1("13. Wie alles entstanden ist — Entwicklungsphasen")
body(
    "AgroLens wurde in sechs Phasen aufgebaut, jede Phase auf der vorherigen aufbauend."
)

h2("Phase 0 — Infrastruktur (Docker & Datenbank)")
bullet("Docker Compose: Backend, Frontend, PostgreSQL, Redis in Containern")
bullet("Alembic: Datenbankmigrations-Framework aufgesetzt")
bullet("Grundlegende FastAPI-App mit Health-Check-Endpunkt")

h2("Phase 1 — Benutzer, Betriebe, Felder & Auth")
bullet("User/Farm/Field ORM-Modelle und Migrations (0001)")
bullet("Supabase JWT-Authentifizierung implementiert")
bullet("REST-API: CRUD für Felder (anlegen, auflesen, bearbeiten, löschen)")
bullet("API-Key-Auth für externe Integrationen (Phase 1.5)")
bullet("Rate Limiting: max. X Anfragen pro Minute pro IP/API-Key")

h2("Phase 2 — Satelliten-Pipeline")
bullet("Sentinel Hub Integration: Bilder automatisch abrufen")
bullet("NDVI/NDRE-Berechnung mit NumPy (ohne KI — reine Mathematik)")
bullet("Wolkenmaskierung über SCL-Layer")
bullet("Median-Komposit aus mehreren Aufnahmen")
bullet("Ergebnisse in S3 (AWS) und DB speichern")

h2("Phase 3 — Zoneneinteilung & Ausbringungskarten")
bullet("k-Means Clustering mit scikit-learn")
bullet("Prescription Engine mit validierten Multiplikatoren")
bullet("ISOBUS TASKDATA.XML Export")
bullet("Shapefile Export (mit rasterio/fiona)")
bullet("PDF-Bericht mit ReportLab")

h2("Phase 4 — Dashboard UI")
bullet("Next.js Dashboard mit Mapbox GL JS (interaktive Karte)")
bullet("NDVI-Zeitreihen-Chart mit Recharts")
bullet("Feldverwaltung: Zeichnen, Importieren, Bearbeiten")
bullet("Benachrichtigungseinstellungen")
bullet("Progressive Web App (PWA) für mobile Nutzung")

h2("Phase 5 — Stripe Billing")
bullet("Subscription-Modell mit 4 Tarifen")
bullet("Stripe Checkout & Billing Portal")
bullet("Webhook-Handler für alle Zahlungsereignisse")
bullet("Plan-Limits in fields.py und prescriptions.py")
bullet("Billing-Dashboard im Frontend")

divider()

# FOOTER
footer_p = doc.add_paragraph()
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = footer_p.add_run(
    "AgroLens Code-Dokumentation  ·  Mai 2026  ·  Erstellt mit Claude Sonnet 4.6"
)
r.font.size = Pt(9)
r.font.color.rgb = GRAY

# ── Speichern ─────────────────────────────────────────────────────────────────
output_path = "/Users/danielschaller/Desktop/CS Haus & Garten/Winter…/Claude Agents/AgroLens_Code_Erklaerung.docx"
doc.save(output_path)
print(f"Gespeichert: {output_path}")
