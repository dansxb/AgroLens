"""
AgroLens — Presenter Guide Generator
Produces: AgroLens_Presenter_Guide.docx
"""

from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy


# ─── Colour helpers ───────────────────────────────────────────────────────────

def hex_rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


C_PRIMARY  = hex_rgb("1B4D1F")
C_MID      = hex_rgb("2E7D32")
C_GOLD     = hex_rgb("F9A825")
C_RED      = hex_rgb("C62828")
C_DARK_TXT = hex_rgb("1A1A1A")
C_GRAY     = hex_rgb("546E54")
C_WHITE    = hex_rgb("FFFFFF")


def set_cell_bg(cell, hex_color):
    """Set a table cell background colour via XML."""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color.lstrip("#"))
    tcPr.append(shd)


def cell_text(cell, text, bold=False, color=None, size_pt=10.5, align=WD_ALIGN_PARAGRAPH.LEFT):
    para = cell.paragraphs[0]
    para.alignment = align
    run  = para.add_run(text)
    run.font.size  = Pt(size_pt)
    run.font.bold  = bold
    if color:
        run.font.color.rgb = color


# ─── Style helpers ────────────────────────────────────────────────────────────

def add_heading(doc, text, level=1, color=None):
    p = doc.add_heading(text, level=level)
    if color:
        for run in p.runs:
            run.font.color.rgb = color
    return p


def add_para(doc, text, bold=False, italic=False, color=None, size_pt=11, space_before=0, space_after=6, indent=False):
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(space_before)
    para.paragraph_format.space_after  = Pt(space_after)
    if indent:
        para.paragraph_format.left_indent = Inches(0.25)
    run = para.add_run(text)
    run.font.size   = Pt(size_pt)
    run.font.bold   = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color
    return para


def add_bullet(doc, text, level=0, color=None, size_pt=11):
    para = doc.add_paragraph(style="List Bullet")
    para.paragraph_format.left_indent   = Inches(0.25 + level * 0.25)
    para.paragraph_format.space_after   = Pt(3)
    para.paragraph_format.space_before  = Pt(0)
    run = para.add_run(text)
    run.font.size = Pt(size_pt)
    if color:
        run.font.color.rgb = color
    return para


def add_numbered(doc, text, color=None, size_pt=11):
    para = doc.add_paragraph(style="List Number")
    para.paragraph_format.left_indent  = Inches(0.25)
    para.paragraph_format.space_after  = Pt(3)
    para.paragraph_format.space_before = Pt(0)
    run = para.add_run(text)
    run.font.size = Pt(size_pt)
    if color:
        run.font.color.rgb = color
    return para


def add_tip_box(doc, tip_text, label="TIP"):
    """Adds a shaded tip paragraph."""
    para = doc.add_paragraph()
    para.paragraph_format.left_indent  = Inches(0.3)
    para.paragraph_format.right_indent = Inches(0.3)
    para.paragraph_format.space_before = Pt(4)
    para.paragraph_format.space_after  = Pt(8)
    run_label = para.add_run(f"{label}: ")
    run_label.font.bold        = True
    run_label.font.color.rgb   = C_GOLD
    run_label.font.size        = Pt(11)
    run_body = para.add_run(tip_text)
    run_body.font.size         = Pt(11)
    run_body.font.color.rgb    = hex_rgb("3E2E00")
    return para


def add_warning_box(doc, warn_text):
    para = doc.add_paragraph()
    para.paragraph_format.left_indent  = Inches(0.3)
    para.paragraph_format.space_before = Pt(4)
    para.paragraph_format.space_after  = Pt(8)
    run_label = para.add_run("⚠  WATCH OUT: ")
    run_label.font.bold      = True
    run_label.font.color.rgb = C_RED
    run_label.font.size      = Pt(11)
    run_body = para.add_run(warn_text)
    run_body.font.size       = Pt(11)
    run_body.font.color.rgb  = hex_rgb("7B1515")
    return para


def add_quote(doc, text, attribution=""):
    para = doc.add_paragraph()
    para.paragraph_format.left_indent  = Inches(0.5)
    para.paragraph_format.right_indent = Inches(0.5)
    para.paragraph_format.space_before = Pt(6)
    para.paragraph_format.space_after  = Pt(6)
    run = para.add_run(f'"{text}"')
    run.font.italic      = True
    run.font.size        = Pt(12)
    run.font.color.rgb   = C_MID
    if attribution:
        run2 = para.add_run(f"\n— {attribution}")
        run2.font.size     = Pt(10)
        run2.font.color.rgb = C_GRAY
    return para


def add_divider(doc):
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    p = doc.add_paragraph()
    run = p.add_run("─" * 90)
    run.font.color.rgb = hex_rgb("CCDDCC")
    run.font.size      = Pt(8)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def slide_section(doc, slide_num, title, time_note=""):
    doc.add_page_break()
    # Slide header bar (visual anchor)
    header_para = doc.add_paragraph()
    header_para.paragraph_format.space_before = Pt(0)
    header_para.paragraph_format.space_after  = Pt(4)
    run_num   = header_para.add_run(f"FOLIE {slide_num}  ")
    run_num.font.bold      = True
    run_num.font.size      = Pt(10)
    run_num.font.color.rgb = C_GOLD
    run_title = header_para.add_run(title.upper())
    run_title.font.bold      = True
    run_title.font.size      = Pt(10)
    run_title.font.color.rgb = C_PRIMARY
    if time_note:
        run_time = header_para.add_run(f"   ·   {time_note}")
        run_time.font.size      = Pt(10)
        run_time.font.color.rgb = C_GRAY
    h = doc.add_heading(title, level=2)
    for run in h.runs:
        run.font.color.rgb = C_PRIMARY


# ─── Document sections ────────────────────────────────────────────────────────

def build_intro(doc):
    add_heading(doc, "AgroLens — Investor Pitch Guide", level=1, color=C_PRIMARY)
    add_para(doc, "Alles, was du wissen musst, um die Präsentation zu halten.", italic=True, color=C_GRAY, size_pt=13)
    add_para(doc,
             "Dieses Dokument erklärt dir Folie für Folie, was du sagen sollst, welche Zahlen du "
             "kennen musst und wie du auf typische Investoren-Fragen reagierst. "
             "Lies es vollständig, bevor du die erste Präsentation hältst.", size_pt=11)

    add_heading(doc, "Kurzübersicht: Die Präsentation", level=2, color=C_PRIMARY)

    rows = [
        ("Folie",       "Titel",                        "Dauer"),
        ("1",           "Title — AgroLens",             "0:30"),
        ("2",           "The Problem",                  "1:30"),
        ("3",           "The Solution",                 "1:30"),
        ("4",           "How It Works",                 "2:00"),
        ("5",           "Product",                      "2:00"),
        ("6",           "Market Opportunity",           "2:00"),
        ("7",           "Business Model",               "2:00"),
        ("8",           "Financial Projections",        "2:00"),
        ("9",           "Unit Economics",               "1:30"),
        ("10",          "Competitive Landscape",        "2:00"),
        ("11",          "Regulatory Tailwinds",         "1:30"),
        ("12",          "Traction & Technology",        "1:30"),
        ("13",          "Investment Ask",               "2:00"),
        ("14",          "Contact & Next Steps",         "1:00"),
        ("GESAMT",      "",                             "~24 min"),
    ]

    tbl = doc.add_table(rows=len(rows), cols=3)
    tbl.style = "Table Grid"
    tbl.autofit = False
    col_widths = [Inches(0.6), Inches(3.8), Inches(1.0)]
    for i, row_data in enumerate(rows):
        row = tbl.rows[i]
        for j, (text, width) in enumerate(zip(row_data, col_widths)):
            row.cells[j].width = width
            is_header  = i == 0
            is_total   = row_data[0] == "GESAMT"
            bg = "1B4D1F" if is_header else ("F9A825" if is_total else ("F1F8F1" if i % 2 == 0 else "FFFFFF"))
            set_cell_bg(row.cells[j], bg)
            txt_col = C_WHITE if is_header else (C_PRIMARY if is_total else C_DARK_TXT)
            cell_text(row.cells[j], text, bold=(is_header or is_total), color=txt_col, size_pt=10.5)

    add_para(doc, "", size_pt=6)
    add_tip_box(doc,
                "Plane mindestens 10 Minuten für Fragen ein. Eine 24-Minuten-Präsentation + 10 Minuten Q&A "
                "passt perfekt in einen 35-Minuten-Slot.",
                label="TIMING")


def build_general_tips(doc):
    doc.add_page_break()
    add_heading(doc, "Allgemeine Präsentationstipps", level=1, color=C_PRIMARY)

    add_heading(doc, "Die drei wichtigsten Dinge, die du vermitteln musst", level=2, color=C_PRIMARY)
    add_numbered(doc, "Problem ist real und groß — Bauern verschwenden €20–50/ha/Jahr durch gleichmäßige Ausbringung.", color=C_PRIMARY)
    add_numbered(doc, "Unser Vorteil ist strukturell — kostenlose ESA-Satellitendaten, die Wettbewerber nicht nutzen.", color=C_PRIMARY)
    add_numbered(doc, "ROI ist klar — Bauern sparen 5–10× mehr als sie bezahlen, wir haben 97% Datenschichtmarge.", color=C_PRIMARY)

    add_heading(doc, "Körpersprache & Energie", level=2, color=C_PRIMARY)
    add_bullet(doc, "Steh auf, wenn möglich. Stehend präsentieren wirkt überzeugender.")
    add_bullet(doc, "Mach Pausen nach Schlüsselsätzen — 2 Sekunden Stille lässt die Zahl sinken.")
    add_bullet(doc, 'Sag nie "ich glaube" oder "vielleicht". Benutze: "Wir wissen...", "Die Daten zeigen..."')
    add_bullet(doc, "Wenn du eine Frage nicht weißt: 'Gute Frage — das führen wir im Data Room detailliert aus.'")

    add_heading(doc, "Was Investoren WIRKLICH hören wollen", level=2, color=C_PRIMARY)
    add_bullet(doc, "Ist der Markt groß genug? → Ja: $24B Precision Ag, €264M SAM")
    add_bullet(doc, "Warum ihr? → Kostenloser Satellitendaten-Moat, EU-Regulierungsfokus, kein Interessenkonflikt")
    add_bullet(doc, "Können sie skalieren? → SaaS-Modell, €0.20/ha Infra-Kosten, API-Kanal ohne Grenzkosten")
    add_bullet(doc, "Was passiert mit meinem Geld? → 18 Monate Runway, klare Meilensteine, Month 30 EBITDA+")

    add_tip_box(doc,
                "Beginne die Präsentation mit einer persönlichen Geschichte: "
                "'Ich stand mit einem Bauern in Norddeutschland auf seinem Feld. Er hat gerade 200 Liter Pestizide "
                "auf 50 Hektar gespritzt — komplett gleichmäßig. Ein Drittel seines Feldes war kerngesund. "
                "Er wusste es nicht. AgroLens hätte es ihm gesagt.' "
                "Zahlen erinnert man, Geschichten erinnert man noch besser.",
                label="OPENER-TRICK")


def build_slide_01(doc):
    slide_section(doc, 1, "Title Slide — AgroLens", "0:30")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "Logo: '🌿 AgroLens'")
    add_bullet(doc, "Tagline: 'Precision Pesticide Intelligence via Satellite AI'")
    add_bullet(doc, "Subtitle: 'Reduce pesticide use by 20–40% through satellite-driven VRA maps'")
    add_bullet(doc, "Rechts: Farbige Feldkarte (NDVI Prescription Map) mit Zonen")
    add_bullet(doc, "Badges: €11.7B Market · 20–40% Input Savings · €0 Satellite Cost")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    add_quote(doc,
              "AgroLens ist eine Präzisions-Landwirtschaftsplattform, die Satellitendaten nutzt, "
              "um Bauern exakt zu sagen, wo sie Pestizide aufbringen sollen — und wo nicht. "
              "Das Ergebnis: 20 bis 40 Prozent weniger Pestizideinsatz, bei gleicher Ernte. "
              "Wir nutzen kostenlose ESA-Satellitendaten, die unsere Konkurrenten teuer bezahlen.")

    add_para(doc, "Key Points:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "Nenne die Zahl '20–40%' früh und langsam — das ist dein Hook.")
    add_bullet(doc, "Weise auf die Feldkarte rechts hin: 'Was Sie hier sehen, ist eine echte Prescription Map — rot = mehr spritzen, grün = weniger.'")
    add_bullet(doc, "Die Folie muss den Raum neugierig machen, nicht alles erklären.")


def build_slide_02(doc):
    slide_section(doc, 2, "The Problem", "1:30")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "Karte 1 — 'Wasted Money': Gleichmäßige Ausbringung kostet €20–50/ha zu viel")
    add_bullet(doc, "Karte 2 — 'Environmental Harm': EU Farm to Fork fordert −50% Pestizideinsatz bis 2030")
    add_bullet(doc, "Karte 3 — 'Compliance Burden': §67 PflSchG erfordert lückenlose Dokumentation")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    add_quote(doc,
              "Bauern in Deutschland und ganz Europa spritzen heute noch wie vor 40 Jahren: "
              "überall gleich viel. Das ist wie eine Pille verschreiben, ohne den Patienten zu untersuchen. "
              "Das kostet sie 20 bis 50 Euro pro Hektar zu viel — jede Saison. Bei einem 400-Hektar-Betrieb "
              "sind das bis zu 20.000 Euro verschwendet. Gleichzeitig drohen Bußgelder bis 50.000 Euro "
              "bei nicht ordnungsgemäßer Dokumentation nach §67 PflSchG.")

    add_para(doc, "Zahlen, die du auswendig kennen musst:", bold=True, color=C_PRIMARY)
    tbl = doc.add_table(rows=4, cols=2)
    tbl.style = "Table Grid"
    data = [
        ("Zahl",                                    "Quelle / Kontext"),
        ("€20–50 pro Hektar verschwendet",          "McKinsey Voice of the Global Farmer 2024"),
        ("50% Reduktionsziel der EU bis 2030",      "EU Farm to Fork Strategy, European Green Deal"),
        ("€50.000 Bußgeld bei Verstoß §67 PflSchG", "Pflanzenschutzgesetz Deutschland"),
    ]
    for i, (a, b) in enumerate(data):
        is_header = i == 0
        set_cell_bg(tbl.rows[i].cells[0], "1B4D1F" if is_header else ("F1F8F1" if i%2==0 else "FFFFFF"))
        set_cell_bg(tbl.rows[i].cells[1], "1B4D1F" if is_header else ("F1F8F1" if i%2==0 else "FFFFFF"))
        cell_text(tbl.rows[i].cells[0], a, bold=is_header, color=C_WHITE if is_header else C_PRIMARY, size_pt=10.5)
        cell_text(tbl.rows[i].cells[1], b, bold=is_header, color=C_WHITE if is_header else C_DARK_TXT, size_pt=10.5)

    add_para(doc, "", size_pt=4)
    add_tip_box(doc,
                "Pause nach 'bis 20.000 Euro verschwendet'. Lass die Zahl sitzen. Dann weiter.",
                label="PAUSE")


def build_slide_03(doc):
    slide_section(doc, 3, "The Solution", "1:30")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "Linke Hälfte: Farbige Feldkarte mit 4 NDVI-Zonen (grün/gelb/orange/rot)")
    add_bullet(doc, "Rechte Hälfte: 4 Value Propositions (Sentinel-2, AI-Zonierung, VRA, ISOBUS-Export)")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    add_quote(doc,
              "AgroLens löst genau dieses Problem. Wir ziehen kostenlose Satellitendaten "
              "der Europäischen Weltraumagentur — täglich, für jeden Acker in Europa — "
              "und lassen unsere KI darüber laufen. Das Ergebnis ist diese Karte. "
              "Grün bedeutet: gesunde Pflanzen, weniger spritzen. Rot bedeutet: Stress, hier "
              "brauchen die Pflanzen mehr Aufmerksamkeit. Diese Karte geht direkt auf den "
              "ISOBUS-Schlepper-Terminal. Der Traktor regelt die Düse automatisch. "
              "Kein manueller Eingriff. Kein Papierkram.")

    add_para(doc, "Erkläre den Kernvorteil aktiv:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "Sentinel-2 ist KOSTENLOS — unsere Konkurrenten bezahlen €0.20–0.50 pro Hektar pro Szene für kommerzielle Daten. Wir nicht.")
    add_bullet(doc, "ISOBUS-Kompatibilität ist entscheidend: Nur TASKDATA.XML funktioniert auf allen modernen Traktorterminals. Shapefile allein reicht nicht (das übersehen viele Konkurrenten).")
    add_bullet(doc, "Wir sind herstellerunabhängig — kein Interessenkonflikt mit Pestizidverkäufern (anders als Climate FieldView von Bayer).")

    add_tip_box(doc,
                "Wenn du die Feldkarte zeigst, weise mit dem Finger/Laser auf die rote Zone: "
                "'Diese Fläche braucht mehr Behandlung. Diese Zone hier' — zeige auf grün — "
                "'ist kerngesund. Der Bauer weiß das heute nicht. AgroLens sagt es ihm.'",
                label="DEMO-MOMENT")


def build_slide_04(doc):
    slide_section(doc, 4, "How It Works", "2:00")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "5 Schritte als Boxen mit Pfeilen: Upload → Imagery → Index → Zonierung → Export")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    steps_script = [
        ("Schritt 1 — Feld hochladen",
         "Der Bauer zeichnet sein Feld auf einer Karte oder lädt eine GeoJSON-Datei hoch. "
         "Das dauert 3 Minuten. Keine Installation, keine spezielle Hardware."),
        ("Schritt 2 — Satellitendaten",
         "Unser System zieht automatisch die neuesten Sentinel-2-Bilder von der ESA. "
         "Alle 5 Tage gibt es neue Aufnahmen über Europa. Wir verarbeiten sie noch am selben Tag."),
        ("Schritt 3 — Indexberechnung",
         "Wir berechnen den NDVI und NDRE — das sind Vegetationsindizes, die aus den Spektralbändern "
         "des Satelliten errechnet werden. Vereinfacht gesagt: wie gesund sind die Pflanzen, "
         "auf den Quadratmeter genau."),
        ("Schritt 4 — KI-Zonierung",
         "Unser k-Means-Clustering-Algorithmus gruppiert jeden Quadratmeter im Feld "
         "in eine von drei Zonen: wenig Stress, mittlerer Stress, hoher Stress."),
        ("Schritt 5 — Export",
         "Die Prescription Map geht als TASKDATA.XML, Shapefile und PDF raus. "
         "Der Traktorfahrer lädt die Datei auf den Terminal — und das Feld wird "
         "automatisch variabel behandelt."),
    ]
    for title, script in steps_script:
        add_para(doc, f"→ {title}", bold=True, color=C_MID, size_pt=11)
        add_para(doc, script, indent=True, size_pt=11, space_before=0, space_after=4)

    add_para(doc, "Technische Anmerkungen für Rückfragen:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "Verarbeitungszeit: Ende-zu-Ende in unter 24 Stunden nach neuem Satellitenbild.")
    add_bullet(doc, "Cloud Cover: Norddeutschland hat oft Bewölkung. Wir verwenden 10-Tage-Median-Compositing und Sentinel-1-SAR-Daten (radar = wolkendurchdringend) als Backup.")
    add_bullet(doc, "NDVI-Formel: (NIR − Rot) / (NIR + Rot) — reine Physik, keine Black Box.")


def build_slide_05(doc):
    slide_section(doc, 5, "Product", "2:00")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "Links: NDVI Prescription Map (Feldkarte mit Farbzonen)")
    add_bullet(doc, "Rechts oben: NDVI-Zeitreihen-Chart (12 Monate, Balkendiagramm)")
    add_bullet(doc, "Rechts unten: Feature-Liste (Mapbox, Recharts, ISOBUS-Export, Alerts, PWA, API)")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    add_quote(doc,
              "Das ist unser Dashboard. Links siehst du die aktuelle Prescription Map eines Feldes — "
              "live aus Satellitendaten von dieser Woche. Rechts oben siehst du den NDVI-Verlauf "
              "der letzten 12 Monate. Du kannst sehen, wie die Pflanzengesundheit über die Saison "
              "schwankt — das ist wertvolles Wissen für die nächste Planung. "
              "Mit einem Klick exportiert der Bauer die Karte als ISOBUS-Datei. "
              "Das Ganze funktioniert auch auf dem Tablet im Feld — offline, wenn es kein Signal gibt.")

    add_para(doc, "Produkt-Features kurz erklären:", bold=True, color=C_PRIMARY)
    features = [
        ("Mapbox GL",         "Satelliten-Basiskarte mit NDVI-Overlay in Echtzeit"),
        ("Recharts",          "12-Monats-NDVI-Trendkurve pro Feld"),
        ("ISOBUS Export",     "TASKDATA.XML + Shapefile + PDF mit einem Klick"),
        ("Alerts",            "E-Mail/SMS wenn NDVI um >15% unter Monatsdurchschnitt fällt"),
        ("PWA / Offline",     "Progressive Web App — nach erstem Laden vollständig offline nutzbar"),
        ("REST API",          "Programmatischer Zugriff für ERP-Integrationen und Agrarhändler"),
    ]
    tbl = doc.add_table(rows=len(features)+1, cols=2)
    tbl.style = "Table Grid"
    set_cell_bg(tbl.rows[0].cells[0], "1B4D1F")
    set_cell_bg(tbl.rows[0].cells[1], "1B4D1F")
    cell_text(tbl.rows[0].cells[0], "Feature", bold=True, color=C_WHITE)
    cell_text(tbl.rows[0].cells[1], "Was es macht", bold=True, color=C_WHITE)
    for i, (feat, desc) in enumerate(features):
        bg = "F1F8F1" if i % 2 == 0 else "FFFFFF"
        set_cell_bg(tbl.rows[i+1].cells[0], bg)
        set_cell_bg(tbl.rows[i+1].cells[1], bg)
        cell_text(tbl.rows[i+1].cells[0], feat, bold=True, color=C_PRIMARY)
        cell_text(tbl.rows[i+1].cells[1], desc, color=C_DARK_TXT)


def build_slide_06(doc):
    slide_section(doc, 6, "Market Opportunity", "2:00")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "TAM/SAM/SOM konzentrische Kreise (links)")
    add_bullet(doc, "5 Wachstumstreiber (rechts)")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    add_quote(doc,
              "Precision Agriculture ist heute ein 11,7-Milliarden-Dollar-Markt "
              "und wächst mit 13% pro Jahr. Bis 2030 wird er auf 24 Milliarden geschätzt. "
              "Unser SAM — das sind die Bauern in der EU und den USA, die bereit sind, "
              "digitale Lösungen zu kaufen — hat ein ARR-Potenzial von 264 Millionen Euro. "
              "Bis Jahr 3 wollen wir 400.000 Hektar managen und knapp 4 Millionen Euro ARR erwirtschaften. "
              "Das ist 1,2 Prozent unseres SAM — sehr konservativ.")

    add_para(doc, "Markt-Zahlen auswendig kennen:", bold=True, color=C_PRIMARY)
    market_data = [
        ("TAM",  "$24.1B",     "Globale Precision Agriculture bis 2030 (Grand View Research, 13.1% CAGR)"),
        ("SAM",  "€264M ARR",  "33 Mio. ha digital adressierbar in EU + USA bei €8/ha Blended ARPU"),
        ("SOM",  "€3.95M ARR", "400.000 ha bis Ende Jahr 3 · 1,2% des SAM · sehr konservativ"),
        ("AI-Segment", "$5.68B", "AI in Precision Agriculture bis 2035 · CAGR 20% (InsightAce Analytic)"),
    ]
    for segment, value, context in market_data:
        add_bullet(doc, f"{segment}: {value} — {context}")

    add_para(doc, "Wachstumstreiber kurz erklären:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "13,1% CAGR: Schnellstes Wachstum im digitalen Agrar-Segment global")
    add_bullet(doc, "EU Farm to Fork: Bindende 50%-Reduktionsziele schaffen dauerhaften Bedarf")
    add_bullet(doc, "CAP Eco-Schemes: EU zahlt Bauern direkt für dokumentierte Präzisionsausbringung")
    add_bullet(doc, "Freie ESA-Satellitendaten: Unser Datenvorteil wächst mit dem Markt, nicht unsere Kosten")
    add_bullet(doc, "Input-Preisinflation post-2022: Pestizidkosten +40–60%, ROI für VRA-Tools verdoppelt sich")

    add_tip_box(doc,
                "Wenn Investoren fragen 'Ist der Markt nicht überfüllt?': "
                "Antwort: 'Der Markt für generisches Crop Monitoring ist kompetitiv. "
                "Der Markt für reinen Pestizid-VRA mit EU-Compliance-Workflow ist faktisch leer. "
                "Das ist unser Segment — und genau das differenziert uns.'",
                label="Q&A VORBEREITUNG")


def build_slide_07(doc):
    slide_section(doc, 7, "Business Model", "2:00")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "4 Preis-Tiers: Basis (kostenlos), Starter (€49/mo), Farmer (€149/mo), Pro (€599/mo)")
    add_bullet(doc, "3 Revenue Streams: SaaS, API Licensing, Government Contracts")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    add_quote(doc,
              "Unser Geschäftsmodell ist einfach: Pro-Hektar-SaaS-Abo. "
              "Der Bauer zahlt €49 im Monat für bis zu 5 Felder und 100 Hektar — "
              "das entspricht etwa €4,70 pro Hektar und Jahr. "
              "Er spart damit 20 bis 50 Euro pro Hektar an Pestizidkosten. "
              "Der ROI liegt bei Faktor 4 bis 10 — schon im ersten Jahr. "
              "Unser empfohlener Tarif ist Farmer bei €149 — für 500 Hektar. "
              "Für Lohnunternehmer gibt es unbegrenzte Felder für €599 im Monat. "
              "Neben dem Basisgeschäft lizenzieren wir unsere Daten-API an Agrarhändler "
              "und erhalten Verträge von Behörden zur Flächenüberwachung.")

    add_para(doc, "Preisgestaltung im Detail:", bold=True, color=C_PRIMARY)
    pricing = [
        ("Basis",   "Kostenlos",  "1 Feld, 15 ha, nur NDVI, kein Export",     "Akquisitions-Tool, kein Umsatz"),
        ("Starter", "€49/mo",     "5 Felder, 100 ha, alle Exports",           "Kleine Betriebe, erster Paid-Plan"),
        ("Farmer",  "€149/mo",    "50 Felder, 500 ha, komplettes Suite",      "Empfohlen — 400 ha Durchschnittsbetrieb"),
        ("Pro",     "€599/mo",    "Unbegrenzt, Lohnunternehmer-Pricing",      "Contractors, große Betriebe"),
    ]
    tbl = doc.add_table(rows=len(pricing)+1, cols=4)
    tbl.style = "Table Grid"
    headers_p = ["Plan", "Preis", "Umfang", "Zielkunde"]
    for j, h in enumerate(headers_p):
        set_cell_bg(tbl.rows[0].cells[j], "1B4D1F")
        cell_text(tbl.rows[0].cells[j], h, bold=True, color=C_WHITE)
    for i, (plan, price, scope, target) in enumerate(pricing):
        bg = "FFF9E6" if plan == "Farmer" else ("F1F8F1" if i%2==0 else "FFFFFF")
        for j, text in enumerate([plan, price, scope, target]):
            set_cell_bg(tbl.rows[i+1].cells[j], bg)
            cell_text(tbl.rows[i+1].cells[j], text,
                      bold=(plan == "Farmer"),
                      color=C_GOLD if plan == "Farmer" else C_DARK_TXT)

    add_para(doc, "", size_pt=4)
    add_para(doc, "Weitere Revenue Streams:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "API Licensing: €2,50/ha/Jahr an Agrarhändler und Beratungsplattformen. Mindestvertrag €10.000. Quasi null Grenzkosten.")
    add_bullet(doc, "Government Contracts: €100.000–500.000/Vertrag für regionale Überwachungsdaten. EU-Behörden brauchen skalierbare Monitoring-Tools.")
    add_bullet(doc, "Künftig Carbon MRV: Provision auf Pestizidreduktions-Kreditpunkte für Voluntary Carbon Markets.")


def build_slide_08(doc):
    slide_section(doc, 8, "Financial Projections", "2:00")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "3-Jahres-Tabelle: Hektar, ARR nach Kanal, Gross Profit, OpEx, EBITDA")
    add_bullet(doc, "Key Assumptions darunter")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    add_quote(doc,
              "Im ersten Jahr erwirtschaften wir 160.000 Euro ARR mit 20.000 Hektar — "
              "das sind unsere 10 Pilotbetriebe und erste Direktkunden. "
              "Im zweiten Jahr skalieren wir auf 120.000 Hektar und 1,2 Millionen ARR, "
              "dann kommt der API-Kanal und erste Regierungsverträge dazu. "
              "Im dritten Jahr bei 400.000 Hektar und 3,95 Millionen ARR "
              "erreichen wir EBITDA-Break-Even — Monat 30, drittes Quartal 2028. "
              "Unsere Bruttomargen: 72% im ersten Jahr, steigend auf 83% — "
              "weil Infrastrukturkosten nur €0,20 pro Hektar betragen "
              "und jede neue Fläche kaum Mehrkosten verursacht.")

    add_para(doc, "Zahlen die du auswendig können musst:", bold=True, color=C_PRIMARY)
    fin_data = [
        ("Year 1 ARR",          "€160.000",     "20.000 ha · 10 Pilotbetriebe"),
        ("Year 2 ARR",          "€1,2 Mio.",    "120.000 ha · API-Kanal startet"),
        ("Year 3 ARR",          "€3,95 Mio.",   "400.000 ha · Regierungsverträge"),
        ("Gross Margin Year 1", "72%",           "Steigt auf 83% durch Skaleneffekte"),
        ("EBITDA Breakeven",    "Monat 30",      "Q3 2028 — konservative Schätzung"),
        ("Infra-Kosten",        "€0,20/ha/Jahr", "Compute + Storage — extrem skalierbar"),
    ]
    for key, val, context in fin_data:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        r1 = p.add_run(f"{key}: ")
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = C_PRIMARY
        r2 = p.add_run(f"{val}")
        r2.font.bold = True
        r2.font.size = Pt(11)
        r2.font.color.rgb = C_MID
        r3 = p.add_run(f"  —  {context}")
        r3.font.size = Pt(11)
        r3.font.color.rgb = C_GRAY

    add_warning_box(doc,
                    "Wenn Investoren die Wachstumsrate von 6× (Year 1→2) als unrealistisch kommentieren: "
                    "'Wir haben in Year 2 Cooperative Partnerships, die uns Zugang zu 50.000+ ha ihrer Mitgliedsbetriebe "
                    "geben — daher der Sprung. Das ist kein organisches Wachstum, das ist Vertriebshebel.'")


def build_slide_09(doc):
    slide_section(doc, 9, "Unit Economics", "1:30")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "5 Metriken: 13.3× LTV:CAC, 6 Monate Payback, €16K LTV, 97% Data-Layer-GM, €0.20/ha Infra")
    add_bullet(doc, "CAC-Tabelle nach Kanal")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    add_quote(doc,
              "Unsere Unit Economics sind stark. "
              "Ein Durchschnittskunde in der EU — 400 Hektar, €3.200 Jahresvertrag — "
              "kostet uns €1.200 zu gewinnen und bringt €16.000 über 5 Jahre. "
              "LTV zu CAC: 13,3 zu 1. Die Benchmark für gute SaaS-Companies ist 3 zu 1 — "
              "wir sind viermal besser. Unsere Infrastrukturkosten sind nur 20 Cent pro Hektar pro Jahr. "
              "Satellitenbilder kosten uns nichts. Das ist strukturell günstiger als jeder Wettbewerber.")

    add_para(doc, "Alle Unit-Economic-Zahlen:", bold=True, color=C_PRIMARY)
    ue_data = [
        ("LTV:CAC",        "13,3×",      "Benchmark SaaS: >3×. Wir: 4× über dem Benchmark."),
        ("CAC Payback",    "6 Monate",   "€1.200 CAC / (€3.200 × 72% GM) = 5,2 Monate"),
        ("LTV EU Farm",    "€16.000",    "400 ha × €8/ha/yr × 5 Jahre Lifetime"),
        ("LTV US Farm",    "$216.000",   "3.000 ha × $12/ha/yr × 6 Jahre Lifetime"),
        ("LTV API Händler","€875.000",   "50.000 ha × €2.50/ha/yr × 7 Jahre Lifetime"),
        ("Data-Layer GM",  "97%",        "Sentinel-2 = €0. Infra = €0.20/ha/yr."),
        ("Blended GM Y1",  "72%",        "Steigt auf 83% in Year 3"),
        ("Blended CAC Y1", "€1.200",     "Fällt auf €800 in Year 2+ (Brand + Referrals)"),
    ]
    for key, val, context in ue_data:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        r1 = p.add_run(f"{key}: ")
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = C_PRIMARY
        r2 = p.add_run(val)
        r2.font.bold = True
        r2.font.size = Pt(12)
        r2.font.color.rgb = hex_rgb("F9A825")
        r3 = p.add_run(f"  — {context}")
        r3.font.size = Pt(10.5)
        r3.font.color.rgb = C_GRAY


def build_slide_10(doc):
    slide_section(doc, 10, "Competitive Landscape", "2:00")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "Positioning Matrix: Datenkosten (X) vs. VRA-Fokus (Y) — AgroLens oben rechts (bestes Segment)")
    add_bullet(doc, "Vergleichstabelle: AgroLens vs. Taranis, FieldView, EOSDA")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    add_quote(doc,
              "Wir haben vier wesentliche Wettbewerber — keiner hat unsere Kombination. "
              "Taranis hat $100 Millionen Funding, aber bezahlt für kommerzielle Satellitendaten "
              "und ist US-zentriert. Climate FieldView hat 250 Millionen Hektar, "
              "aber gehört Bayer — einem Pestizidverkäufer. Das schafft einen fundamentalen Interessenkonflikt. "
              "EOSDA ist technisch kompetent, aber kein reiner Pestizid-VRA-Anbieter "
              "und hat keine EU-Compliance-Workflows. "
              "Wir sind die einzige reine Pestizid-VRA-Plattform mit: "
              "freien Satellitendaten, EU-Regulierungs-Compliance, "
              "und voller Unabhängigkeit von Pestizidherstellern.")

    add_para(doc, "Wettbewerber-Details die du kennen solltest:", bold=True, color=C_PRIMARY)
    competitors = [
        ("Taranis",           "$35.1M ARR, 234 MA, $100M+ Funding",
         "Schwäche: Teure kommerzielle Bilder, US-fokussiert, kein reiner Pestizid-VRA"),
        ("Farmers Edge",      "Privat (Fairfax Financial), IPO-Desaster: C$17 → C$0.35 (−98%)",
         "Schwäche: Hardware-Modell, finanzielle Probleme — Warnung für uns: KEIN Hardware-Modell"),
        ("Climate FieldView", "250M+ Hektar, 23 Länder, Bayer-Tochter",
         "Schwäche: Interessenkonflikt (Bayer = Pestizidverkäufer), kein reiner VRA-Fokus"),
        ("EOSDA",             "Geschätzt $10–30M ARR, breit aufgestellt",
         "Schwäche: Kein reiner Pestizid-VRA, kein EU-Compliance-Workflow, komplexe UI"),
    ]
    for name, status, weakness in competitors:
        add_para(doc, name, bold=True, color=C_MID, size_pt=11)
        add_bullet(doc, f"Status: {status}", level=1)
        add_bullet(doc, f"Schwäche: {weakness}", level=1, color=C_RED)


def build_slide_11(doc):
    slide_section(doc, 11, "Regulatory Tailwinds", "1:30")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "3 Karten: EU Farm to Fork / §67 PflSchG / US EPA ESA")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    add_quote(doc,
              "Wir haben Rückenwind aus drei voneinander unabhängigen Regulierungsrichtungen. "
              "In der EU muss der Pestizideinsatz bis 2030 um 50 Prozent sinken — "
              "CAP Eco-Schemes zahlen Bauern bereits heute Subventionen für dokumentierte Präzisionsausbringung. "
              "In Deutschland schreibt §67 PflSchG lückenlose Dokumentation vor. "
              "In den USA schafft die EPA-ESA-Strategie Haftungsrisiken für Pauschalierer. "
              "Diese drei Mandaten existieren unabhängig voneinander. "
              "Selbst wenn eine Regulierung sich ändert, bleibt der wirtschaftliche Druck — "
              "Pestizidkosten sind nach 2022 um 40–60% gestiegen.")

    add_para(doc, "Regulierungsrisiko ansprechen (wird gefragt werden):", bold=True, color=C_PRIMARY)
    add_warning_box(doc,
                    "FRAGE: 'Die EU SUR (Sustainable Use Regulation) wurde 2024 zurückgezogen — "
                    "ist das nicht ein Problem für euren Regulierungsteil?' "
                    "ANTWORT: 'Nein. Erstens: Unser primäres Value Prop ist Kosteneinsparung, "
                    "nicht Compliance. Bauern sparen €20–50/ha — das braucht keine Regulierung. "
                    "Zweitens: CAP Eco-Schemes zahlen Bauern schon heute. "
                    "Drittens: Deutschland, Frankreich und Niederlande haben eigene nationale Reduktionspläne.'")


def build_slide_12(doc):
    slide_section(doc, 12, "Traction & Technology", "1:30")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "6 Phasen als Fortschrittsbalken — 5 abgeschlossen, Phase 5 im Build")
    add_bullet(doc, "Tech-Stack-Badges")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    add_quote(doc,
              "Wir sind nicht bei null. Wir haben in fünf Phasen eine vollständige "
              "produktionsreife Plattform aufgebaut — von der Datenbankinfrastruktur "
              "bis zum Farmer-Dashboard. Die KI-Pipeline verarbeitet Sentinel-2-Bilder "
              "und generiert ISOBUS-kompatible Prescription Maps. "
              "Das Dashboard läuft auf Mapbox GL mit Recharts-Analytics "
              "und ist als Progressive Web App auch offline im Feld nutzbar. "
              "Wir implementieren jetzt gerade Stripe-Billing für Subscriptions — "
              "das ist Phase 5, unsere letzte vor dem Launch.")

    add_para(doc, "Phasen-Details für Nachfragen:", bold=True, color=C_PRIMARY)
    phases = [
        ("Phase 0 ✅", "Foundation",
         "Docker, PostgreSQL+PostGIS, Redis, Alembic Migrations, CI/CD"),
        ("Phase 1 ✅", "Auth & Data Models",
         "User/Farm/Field ORM-Modelle, Supabase JWT Auth, API-Key Auth, Rate Limiting"),
        ("Phase 2 ✅", "Satellite Pipeline",
         "Sentinel-2 Imagery Ingestion, NDVI/NDRE-Berechnung, Cloud Masking, AWS S3"),
        ("Phase 3 ✅", "AI Prescription Engine",
         "k-Means Zone Delineation, VRA Prescription Rules, TASKDATA.XML + Shapefile + PDF Export"),
        ("Phase 4 ✅", "Dashboard UI",
         "Mapbox GL, Recharts NDVI-Analytics, Notification Preferences, API Keys, PWA"),
        ("Phase 5 🔧", "Billing (in Build)",
         "Stripe Subscriptions, Plan Enforcement, Billing Portal"),
    ]
    for phase, title, detail in phases:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_after = Pt(3)
        r1 = p.add_run(f"{phase}  {title}: ")
        r1.font.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = C_MID if "✅" in phase else hex_rgb("F9A825")
        r2 = p.add_run(detail)
        r2.font.size = Pt(11)
        r2.font.color.rgb = C_DARK_TXT

    add_para(doc, "Tech Stack — kurze Erklärung falls gefragt:", bold=True, color=C_PRIMARY)
    tech_stack = [
        ("FastAPI (Python)",   "Backend API — schnell, typsicher, auto-generierte OpenAPI-Doku"),
        ("Next.js 14",         "Frontend — Server-Side Rendering, TypeScript, Tailwind CSS"),
        ("PostgreSQL+PostGIS", "Datenbank mit nativer Geodaten-Unterstützung"),
        ("scikit-learn",       "k-Means Clustering für Management-Zonen"),
        ("Celery + Redis",     "Background-Jobs für asynchrone Bild-Verarbeitung"),
        ("Supabase Auth",      "JWT-basierte Authentifizierung, Google OAuth"),
        ("AWS S3",             "Objekt-Speicher für Satellitenbilder und Export-Dateien"),
    ]
    for tech, desc in tech_stack:
        add_bullet(doc, f"{tech}: {desc}")


def build_slide_13(doc):
    slide_section(doc, 13, "Investment Ask", "2:00")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "€500K–€1,5M Seed Round · 18–24 Monate Runway")
    add_bullet(doc, "Use of Funds: 40% Produkt, 25% Sales, 20% Team, 15% Operations")
    add_bullet(doc, "6 Meilensteine · Target Investoren")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    add_quote(doc,
              "Wir suchen 500.000 bis 1,5 Millionen Euro in einer Seed-Runde. "
              "Das gibt uns 18 bis 24 Monate Runway — lange genug, um 10 bezahlte Pilotbetriebe "
              "zu onboarden, eine Cooperative Partnership zu unterschreiben "
              "und die ersten 120.000 Hektar unter Management zu bringen. "
              "Damit sind wir auf dem Weg zu 1,2 Millionen ARR in Year 2. "
              "40 Prozent der Mittel gehen direkt in Produkt und Engineering — "
              "Pipeline-Optimierung, mobile App, EU-Cloud-Infrastruktur. "
              "25 Prozent in Sales — Agritechnica-Messeauftritt, Cooperative Outreach. "
              "Der Rest deckt Team, Rechtliches und Compliance.")

    add_para(doc, "Meilensteine die du klar kennen musst:", bold=True, color=C_PRIMARY)
    milestones = [
        "Oktober 2026: 10 bezahlte Pilotbetriebe aktiv",
        "Oktober 2026: Erste ISOBUS Prescription Map live delivered",
        "September 2026: Eine Genossenschaft als Vertriebspartner signed (50.000+ ha Reichweite)",
        "Ende Year 2: 120.000 ha unter Management",
        "Month 12: SOC 2 Type I Audit initiiert",
        "2026: EIC Accelerator Grant-Antrag eingereicht",
    ]
    for ms in milestones:
        add_bullet(doc, f"→  {ms}")

    add_para(doc, "Auf die Frage 'Warum diese Bewertung?':", bold=True, color=C_PRIMARY)
    add_tip_box(doc,
                "Falls Valuation-Fragen kommen: 'Die genaue Valuation diskutieren wir im Data-Room-Gespräch. "
                "Was ich hier zeigen will ist: Bei €3,95M ARR in Year 3 und 5× ARR-Multiple "
                "sind wir bei ~€20M Enterprise Value. Eine Seed-Valuation heute zwischen €2M–5M "
                "gibt dem Investor ein klares 4–10× Potenzial.' "
                "(Nur sagen wenn direkt gefragt — nicht vorher.)",
                label="VALUATION Q&A")


def build_slide_14(doc):
    slide_section(doc, 14, "Contact & Next Steps", "1:00")
    add_para(doc, "Was auf der Folie steht:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "Summary der 6 Schlüssel-Facts")
    add_bullet(doc, "Kontakt: Daniel Schaller, daniel.philipp.schaller@gmail.com")
    add_bullet(doc, "Next Steps: 30-min Demo, Data Room, Reference Calls, Term Sheet August 2026")

    add_para(doc, "Was du sagst:", bold=True, color=C_PRIMARY)
    add_quote(doc,
              "Um das zusammenzufassen: AgroLens ist eine Precision Agriculture SaaS "
              "in einem $24 Milliarden Markt, mit 13% Wachstum, starkem regulatorischen Rückenwind "
              "und einem strukturellen Datenvorteil, den kein Wettbewerber replizieren kann. "
              "Wir haben eine vollständige Plattform gebaut, die 20–40% Pestizideinsatz einspart "
              "und bei 400.000 Hektar unter Management fast 4 Millionen Euro ARR generiert. "
              "Ich freue mich auf das nächste Gespräch. "
              "Lasst uns einen 30-minütigen Demo-Call vereinbaren — "
              "dann können Sie unsere Pipeline live in Aktion sehen.")

    add_para(doc, "Nach der Präsentation:", bold=True, color=C_PRIMARY)
    add_bullet(doc, "Sofort: Visitenkarte/Kontaktdaten austauschen")
    add_bullet(doc, "24 Stunden: Follow-up E-Mail mit Pitch Deck PDF und Einladung zum Data Room")
    add_bullet(doc, "48 Stunden: Demo-Call-Einladung versenden (Calendly-Link)")
    add_bullet(doc, "1 Woche: Falls keine Rückmeldung — eine freundliche Follow-up-E-Mail")


def build_qa_section(doc):
    doc.add_page_break()
    add_heading(doc, "Q&A — Typische Investoren-Fragen", level=1, color=C_PRIMARY)
    add_para(doc,
             "Dies sind die 15 häufigsten Fragen, die Investoren bei AgriTech Seed-Rounds stellen. "
             "Lerne diese Antworten auswendig.", size_pt=11, italic=True, color=C_GRAY)

    qa_pairs = [
        (
            "Wie groß ist euer Markt wirklich — ist €264M SAM nicht zu optimistisch?",
            "Wir haben den SAM sehr konservativ berechnet: nur 15% der EU + US Ackerfläche als 'digital addressable'. "
            "Selbst wenn es 10% sind, bleibt der SAM bei €176M. Unser SOM Year 3 (€3.95M) ist 2,2% davon — "
            "extrem konservativ. Taranis erreicht $35M ARR mit einem ähnlichen Ansatz."
        ),
        (
            "Warum sollten Bauern 10€/ha bezahlen, wenn sie bisher nichts bezahlt haben?",
            "Bauern zahlen heute indirekt: Sie verschwenden €20–50/ha pro Saison durch Überausbringung. "
            "Unser Tool kostet €4–12/ha. ROI ist 2× bis 10× — bereits im ersten Jahr. "
            "Der Entscheidungsprozess ist kein 'Soll ich ausgeben?' sondern 'Warum würde ich NICHT sparen?'"
        ),
        (
            "Sentinel-2 hat nur 10m Auflösung — ist das präzise genug für VRA?",
            "Für Managementzonen-Delineation auf Feldebene: Ja, absolut. "
            "10m Pixel sind ausreichend für 3–5 Zonen auf 50–500 ha Feldern. "
            "Wir bieten Planet Labs 3m Daily als Premium-Add-on für höhere Präzision in V1. "
            "Aber für 80% der Anwendungsfälle ist Sentinel-2 das perfekte Preis-Leistungs-Verhältnis."
        ),
        (
            "Wie ist eure IP-Situation? Kann jemand euren Algorithmus kopieren?",
            "Der NDVI-Algorithmus selbst ist öffentlich bekannt — das ist Physik. "
            "Unser Moat liegt erstens im Workflow: EU-Regulierungs-Compliance, ISOBUS-Export, §67-PflSchG-Doku. "
            "Das bauen Nicht-EU-Firmen nicht einfach nach. Zweitens in den Daten: "
            "Sobald wir tausende Felder über mehrere Saisons haben, haben wir proprietäre ground-truth-Daten "
            "für Model-Verbesserung. Drittens in den Kundenbeziehungen: "
            "Switching Cost ist hoch wenn ein Bauer alle Felder eingepflegt und Maschinerie kalibriert hat."
        ),
        (
            "Was ist euer Go-to-Market im ersten Jahr?",
            "Direct outreach an 20 Betriebe in Deutschland und Frankreich (400–800 ha). "
            "Parallel: Ein Genossenschafts-Partner signed bis September 2026. "
            "Eine Genossenschaft gibt uns Zugang zu 200–500 Mitgliedsbetrieben. "
            "Wir nehmen Revenue Share 10–20% auf Subscriptions für Coop-Members. "
            "Content Marketing auf AgrarHeute und La France Agricole. "
            "Präsenz auf Agritechnica Hannover (November 2026)."
        ),
        (
            "Warum glaubt ihr, 400.000 Hektar bis Year 3 erreichen zu können?",
            "Year 1: 20.000 ha — 10 Pilotkunden, ~2.000 ha Durchschnitt. Sehr realistisch. "
            "Year 2: 120.000 ha — ein Genossenschaftspartner mit 50.000 ha Mitgliederfläche beschleunigt massiv. "
            "Year 3: 400.000 ha — 3 Genossenschaftspartner + API-Kanal + erste Direktkunden USA. "
            "Zum Vergleich: EOSDA hat in 5 Jahren mehrere Millionen Hektar erreicht."
        ),
        (
            "Was passiert wenn Bayer / FieldView einen kostenlosen VRA-Service launcht?",
            "FieldView kann kein glaubwürdiger Pestizid-Reduktions-Berater sein — "
            "das ist structurally unmöglich für einen Pestizidverkäufer. "
            "Wir nutzen genau diesen Interessenkonflikt aktiv in unserem Marketing. "
            "Außerdem: Kopieren kostet Zeit. Wir bauen in dieser Zeit Kundenbeziehungen und Daten. "
            "Und EU-spezifische Compliance-Workflows (§67 PflSchG, FLIK-Nummer, CAP) "
            "bauen US-zentrierte Konzerne typischerweise nicht kurzfristig."
        ),
        (
            "Wie hoch ist eure Churn-Rate?",
            "Wir planen konservativ: 15% Year 1, 10% Year 2, 7% Year 3. "
            "Zum Vergleich: SaaS-Median liegt bei 6–10% für SMB. "
            "Wir erwarten niedrigeren Churn weil: Wechselkosten hoch (Felder eingepflegt, Maschinen kalibriert), "
            "und ROI ist direkt messbar — das schafft Loyalität."
        ),
        (
            "Was macht ihr wenn die Bewölkung zu stark ist?",
            "Wir haben drei Fallbacks: 1) 10-Tage Median-Compositing (mehrere Szenen kombiniert). "
            "2) Sentinel-1 SAR — radar-basiert, durchdringt Wolken zu 100%. "
            "3) Für Premium-Kunden: Planet Labs 3m Daily als Gap-Filler. "
            "Und falls wirklich kein Bild möglich: System empfiehlt automatisch Standard-Ausbringungsrate "
            "statt eine fehlerhafte VRA-Karte zu liefern."
        ),
        (
            "Wer haftet wenn eine falsche VRA-Map zu Ernteschäden führt?",
            "Alle Maps werden als 'Decision Support' kommuniziert, nicht als automatische Anweisung. "
            "Wir haben klare Confidence-Score-Indikatoren und Agronomie-Disclaimer. "
            "Wir schließen professionelle Berufshaftpflicht und Produkthaftpflichtversicherung ab. "
            "In MVP: Human-in-the-loop Review durch Agronomen vor Delivery. "
            "Das ist Standard in der Branche."
        ),
        (
            "Was sind eure Funding-Meilensteine?",
            "Bis Monat 4 (August 2026): Term Sheet signed. "
            "Bis Monat 5 (September 2026): Funding received. "
            "Parallel: EIC Accelerator Grant-Antrag (€0.5M–2.5M EU-Zuschuss, nicht-dilutiv). "
            "Mit EIC als Co-Investment ist unser Funding-Risiko deutlich reduziert."
        ),
        (
            "Wie ist das Team?",
            "Aktuell: Founder/CEO mit Agrar- und Tech-Background. "
            "Geplant mit Funding: +2 Engineers (Backend + ML), +1 Agronomy Advisor (externer Berater). "
            "Pipeline für Year 2: Head of Sales, Customer Success Manager. "
            "Wir halten das Team lean — 4 FTE im ersten Jahr ist die SaaS-Benchmark für Seed Stage."
        ),
        (
            "Habt ihr schon Umsatz?",
            "Wir sind Pre-Revenue — die Plattform ist gebaut, die Pilot-Onboarding-Phase beginnt jetzt. "
            "Wir haben konkrete Gespräche mit [X] Betrieben in [Region]. "
            "Das Funding beschleunigt den Pilot-Launch."
        ),
        (
            "Warum Germany first und nicht sofort EU-weit oder USA?",
            "Germany hat den stärksten Regulierungsdruck (§67 PflSchG, FLIK-System, CAP Eco-Schemes) "
            "und ist der größte Agrarmarkt in der EU. Das gibt uns den besten Traction-Nachweis. "
            "Wir rollen Frankreich und Niederlande in Year 2 aus, USA in Year 2–3. "
            "Focus beats breadth in Seed Stage."
        ),
        (
            "Was ist euer Exit-Szenario?",
            "Drei glaubwürdige Exit-Wege: "
            "1) Strategic Acquisition durch Bayer, BASF, Syngenta oder Corteva — alle bauen digitale Ag-Portfolios. "
            "2) Acquisition durch Farm Management Plattformen: John Deere, CNH, AGCO wollen VRA-Kapazitäten. "
            "3) Series B und IPO wenn wir 5M+ ha und €20M+ ARR erreichen — EOSDA-Weg. "
            "Taranis wurde für ~$50M übernommen. Wir zielen auf >€50M."
        ),
    ]

    for i, (question, answer) in enumerate(qa_pairs):
        q_para = doc.add_paragraph()
        q_para.paragraph_format.space_before = Pt(10)
        q_para.paragraph_format.space_after  = Pt(2)
        q_run = q_para.add_run(f"F{i+1}:  {question}")
        q_run.font.bold      = True
        q_run.font.size      = Pt(11.5)
        q_run.font.color.rgb = C_PRIMARY

        a_para = doc.add_paragraph()
        a_para.paragraph_format.left_indent = Inches(0.3)
        a_para.paragraph_format.space_after = Pt(4)
        a_run = a_para.add_run(answer)
        a_run.font.size      = Pt(11)
        a_run.font.color.rgb = C_DARK_TXT

        if i < len(qa_pairs) - 1:
            add_divider(doc)


def build_cheat_sheet(doc):
    doc.add_page_break()
    add_heading(doc, "Spickzettel — Alle Zahlen auf einen Blick", level=1, color=C_PRIMARY)
    add_para(doc, "Drucke diese Seite aus. Lerne alle Zahlen auswendig.", bold=True, color=C_RED, size_pt=12)

    cheat_data = [
        ("MARKT",          [
            ("Precision Ag TAM 2030",   "$24.1B",       "Grand View Research, 13.1% CAGR"),
            ("SAM (EU + USA)",           "€264M ARR",    "33M ha adressierbar bei €8/ha"),
            ("SOM Year 3",              "€3.95M ARR",   "400.000 ha, 1.2% SAM"),
            ("Crop Protection Market",  "$88–100B",     "Spend den wir direkt reduzieren"),
            ("AI in Precision Ag 2035", "$5.68B",       "CAGR 20% (InsightAce Analytic)"),
        ]),
        ("FINANCIALS",     [
            ("ARR Year 1",              "€160.000",     "20.000 ha"),
            ("ARR Year 2",              "€1,2M",        "120.000 ha"),
            ("ARR Year 3",              "€3,95M",       "400.000 ha"),
            ("EBITDA Breakeven",        "Monat 30",     "Q3 2028"),
            ("Gross Margin Year 1",     "72%",          "Steigt auf 83% Year 3"),
        ]),
        ("UNIT ECONOMICS",  [
            ("LTV:CAC",                 "13.3×",        "Benchmark: >3×"),
            ("CAC Payback",             "6 Monate",     "Sehr schnell für SaaS"),
            ("LTV EU Farm (400 ha)",    "€16.000",      "5-Year Lifetime"),
            ("Infra Cost",              "€0.20/ha/yr",  "Total compute + storage"),
            ("Data Layer GM",           "97%",          "Sentinel-2 = kostenlos"),
        ]),
        ("PRICING",         [
            ("Basis",                   "Kostenlos",    "1 Feld, 15 ha, kein Export"),
            ("Starter",                 "€49/mo",       "5 Felder, 100 ha"),
            ("Farmer (Empfohlen)",      "€149/mo",      "50 Felder, 500 ha"),
            ("Pro",                     "€599/mo",      "Unbegrenzt, Lohnunternehmer"),
        ]),
        ("REGULIERUNG",     [
            ("EU Farm to Fork Ziel",    "−50% bis 2030","Pestizideinsatz"),
            ("§67 PflSchG Bußgeld",     "bis €50.000",  "Bei Nicht-Dokumentation"),
            ("CAP Eco-Scheme Budget",   "€32B+",        "EU-Zahlungen für Nachhaltigkeit"),
            ("US EPA ESA",              "Herbizid (2024) + Insektizid (2025)", "Strategie"),
        ]),
        ("WETTBEWERB",      [
            ("Taranis ARR",             "$35.1M",       "234 MA, $100M+ Funding — bezahlen für Bilder"),
            ("FieldView Hektar",        "250M+ acres",  "Bayer-Tochter — Interessenkonflikt"),
            ("Farmers Edge IPO",        "C$17 → C$0.35","−98% — Hardware-Modell gescheitert"),
            ("Unser Preis vs. Taranis", "€4–12 vs. €15–25","Wir sind 2–3× günstiger"),
        ]),
        ("FUNDING",         [
            ("Seed Round",              "€500K–€1.5M",  "18–24 Monate Runway"),
            ("Produkt & Engineering",   "40% (€600K)",  "Pipeline, Mobile, EU-Infra"),
            ("Sales & Marketing",       "25% (€375K)",  "Coop-Partnerships, Agritechnica"),
            ("Team",                    "20% (€300K)",  "+2 Engineers + 1 Agronomist"),
            ("Operations & Legal",      "15% (€225K)",  "GDPR, SOC2, Versicherung"),
        ]),
    ]

    for category, items in cheat_data:
        add_heading(doc, category, level=2, color=C_PRIMARY)
        tbl = doc.add_table(rows=len(items)+1, cols=3)
        tbl.style = "Table Grid"
        set_cell_bg(tbl.rows[0].cells[0], "1B4D1F")
        set_cell_bg(tbl.rows[0].cells[1], "1B4D1F")
        set_cell_bg(tbl.rows[0].cells[2], "1B4D1F")
        for col_h, txt in enumerate(["Metrik", "Wert", "Kontext"]):
            cell_text(tbl.rows[0].cells[col_h], txt, bold=True, color=C_WHITE)
        for i, (metric, value, context) in enumerate(items):
            bg = "F1F8F1" if i % 2 == 0 else "FFFFFF"
            for j, (cell_txt, col) in enumerate([(metric, C_PRIMARY), (value, C_MID), (context, C_GRAY)]):
                set_cell_bg(tbl.rows[i+1].cells[j], bg)
                cell_text(tbl.rows[i+1].cells[j], cell_txt,
                          bold=(j == 1), color=col, size_pt=10.5)
        doc.add_paragraph().paragraph_format.space_after = Pt(6)


# ─── Build & save ─────────────────────────────────────────────────────────────

def build_guide(output_path: str):
    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin    = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.5)

    # Adjust default font
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)

    build_intro(doc)
    build_general_tips(doc)
    build_slide_01(doc)
    build_slide_02(doc)
    build_slide_03(doc)
    build_slide_04(doc)
    build_slide_05(doc)
    build_slide_06(doc)
    build_slide_07(doc)
    build_slide_08(doc)
    build_slide_09(doc)
    build_slide_10(doc)
    build_slide_11(doc)
    build_slide_12(doc)
    build_slide_13(doc)
    build_slide_14(doc)
    build_qa_section(doc)
    build_cheat_sheet(doc)

    doc.save(output_path)
    print(f"✅  Saved: {output_path}")


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "AgroLens_Presenter_Guide.docx")
    build_guide(out)
