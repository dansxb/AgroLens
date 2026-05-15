"""
AgroLens — Investor Pitch Deck Generator
Produces: AgroLens_Investor_Deck.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
from pptx.chart.data import ChartData
from pptx.enum.chart import XL_CHART_TYPE
import copy
import math

# ─── Brand Palette ────────────────────────────────────────────────────────────
C_DARK        = RGBColor(0x0D, 0x1F, 0x0D)   # near-black green
C_PRIMARY     = RGBColor(0x1B, 0x4D, 0x1F)   # deep forest green
C_MID         = RGBColor(0x2E, 0x7D, 0x32)   # medium green
C_ACCENT      = RGBColor(0x66, 0xBB, 0x6A)   # bright green
C_GOLD        = RGBColor(0xF9, 0xA8, 0x25)   # wheat gold
C_LIGHT_GOLD  = RGBColor(0xFF, 0xEE, 0x58)   # light gold
C_WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
C_OFF_WHITE   = RGBColor(0xF1, 0xF8, 0xE9)   # very light green tint
C_GRAY        = RGBColor(0x78, 0x90, 0x78)   # muted green-gray
C_LIGHT_GRAY  = RGBColor(0xEC, 0xF5, 0xEC)
C_RED_ZONE    = RGBColor(0xC6, 0x28, 0x28)   # stressed crop
C_ORANGE_ZONE = RGBColor(0xE6, 0x5C, 0x00)   # moderate stress
C_YELLOW_ZONE = RGBColor(0xF9, 0xA8, 0x25)   # slight stress
C_GREEN_ZONE  = RGBColor(0x33, 0x8A, 0x3E)   # healthy crop
C_DARK_TEXT   = RGBColor(0x1A, 0x1A, 0x1A)
C_SUBTLE_TEXT = RGBColor(0x55, 0x6B, 0x55)

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)


def prs() -> Presentation:
    p = Presentation()
    p.slide_width  = SLIDE_W
    p.slide_height = SLIDE_H
    return p


# ─── Low-level helpers ────────────────────────────────────────────────────────

def blank_layout(prs_obj):
    return prs_obj.slide_layouts[6]   # completely blank


def fill_bg(slide, color: RGBColor):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, fill_color=None, line_color=None, line_width_pt=0):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        left, top, width, height
    )
    shape.line.fill.background()
    if fill_color:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill_color
    else:
        shape.fill.background()
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(line_width_pt)
    else:
        shape.line.fill.background()
    return shape


def add_textbox(slide, text, left, top, width, height,
                font_size=18, bold=False, color=C_WHITE,
                align=PP_ALIGN.LEFT, italic=False, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font_name
    return txBox


def add_multiline_textbox(slide, lines, left, top, width, height,
                          font_size=14, color=C_WHITE, bold=False,
                          align=PP_ALIGN.LEFT, line_spacing=1.2, font_name="Calibri"):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(4)
        run = p.add_run()
        run.text = line
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.name = font_name
    return txBox


def add_pill(slide, text, left, top, width, height, bg=C_ACCENT, fg=C_WHITE, font_size=11):
    """Rounded rectangle pill badge."""
    shape = slide.shapes.add_shape(
        5,  # MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE
        left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg
    shape.line.fill.background()
    tf = shape.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = True
    run.font.color.rgb = fg
    run.font.name = "Calibri"
    return shape


def dark_header_band(slide, height=Inches(1.15)):
    """Full-width dark green header bar."""
    add_rect(slide, 0, 0, SLIDE_W, height, fill_color=C_PRIMARY)
    # thin gold accent line at bottom of header
    add_rect(slide, 0, height - Pt(3), SLIDE_W, Pt(3), fill_color=C_GOLD)


def slide_label(slide, text, top=Inches(0.2), left=Inches(0.45), color=C_WHITE):
    add_textbox(slide, text, left, top, Inches(12), Inches(0.7),
                font_size=28, bold=True, color=color,
                align=PP_ALIGN.LEFT, font_name="Calibri")


def slide_subtitle(slide, text, top=Inches(0.8), left=Inches(0.45), color=C_OFF_WHITE):
    add_textbox(slide, text, left, top, Inches(12), Inches(0.4),
                font_size=14, color=color, align=PP_ALIGN.LEFT, font_name="Calibri")


# ─── Field Map visual (polygon approximation via many thin rectangles) ────────

def draw_field_map(slide, left, top, width, height):
    """
    Draws a stylised precision-agriculture field map showing NDVI management
    zones using layered shapes to simulate a real prescription map.
    """
    # Outer field boundary (dark border)
    add_rect(slide, left, top, width, height, fill_color=RGBColor(0x1A, 0x23, 0x1A),
             line_color=C_GOLD, line_width_pt=2)

    W = width
    H = height

    # Satellite dark-blue-green base
    add_rect(slide, left, top, W, H, fill_color=RGBColor(0x12, 0x1F, 0x15))

    # Zone polygons — approximate with rectangles at slight offsets
    # Zone: HIGH STRESS (red) — top-right cluster
    add_rect(slide, left + W*0.58, top + H*0.05,
             W*0.30, H*0.32, fill_color=C_RED_ZONE)
    add_rect(slide, left + W*0.70, top + H*0.30,
             W*0.18, H*0.18, fill_color=C_RED_ZONE)

    # Zone: MODERATE STRESS (orange) — centre-right
    add_rect(slide, left + W*0.45, top + H*0.10,
             W*0.20, H*0.40, fill_color=C_ORANGE_ZONE)
    add_rect(slide, left + W*0.55, top + H*0.38,
             W*0.25, H*0.22, fill_color=C_ORANGE_ZONE)

    # Zone: SLIGHT STRESS (yellow) — centre
    add_rect(slide, left + W*0.28, top + H*0.15,
             W*0.25, H*0.45, fill_color=C_YELLOW_ZONE)
    add_rect(slide, left + W*0.42, top + H*0.52,
             W*0.20, H*0.20, fill_color=C_YELLOW_ZONE)

    # Zone: HEALTHY (green) — left side
    add_rect(slide, left + W*0.04, top + H*0.08,
             W*0.30, H*0.65, fill_color=C_GREEN_ZONE)
    add_rect(slide, left + W*0.22, top + H*0.60,
             W*0.25, H*0.20, fill_color=C_GREEN_ZONE)

    # Overlay semi-transparent field boundary outline (just a border rect)
    add_rect(slide, left + W*0.02, top + H*0.04,
             W*0.92, H*0.82,
             fill_color=None,
             line_color=RGBColor(0xFF, 0xFF, 0xFF), line_width_pt=1.5)

    # Legend
    legend_top = top + H * 0.88
    legend_items = [
        (C_GREEN_ZONE,  "Healthy — 60% rate"),
        (C_YELLOW_ZONE, "Slight stress — 100% rate"),
        (C_ORANGE_ZONE, "Moderate — 120% rate"),
        (C_RED_ZONE,    "High stress — 130% rate"),
    ]
    lx = left + W * 0.04
    for color, label in legend_items:
        add_rect(slide, lx, legend_top, Inches(0.15), Inches(0.15), fill_color=color)
        add_textbox(slide, label, lx + Inches(0.18), legend_top - Pt(2),
                    Inches(1.4), Inches(0.22), font_size=8, color=C_WHITE)
        lx += Inches(1.65)

    # Title bar above map
    add_rect(slide, left, top, W, Inches(0.32), fill_color=RGBColor(0x0A, 0x14, 0x0A))
    add_textbox(slide, "  NDVI Prescription Map — Field: Schaller-West  |  2026-05-10  |  Rapeseed",
                left, top + Pt(3), W, Inches(0.28),
                font_size=9, color=C_GOLD, bold=False, font_name="Calibri")


# ─── NDVI Time-Series chart simulation ───────────────────────────────────────

def draw_ndvi_chart(slide, left, top, width, height):
    """Draws a simulated NDVI time-series as a bar + line area chart using shapes."""
    chart_bg = RGBColor(0x0F, 0x1A, 0x0F)
    add_rect(slide, left, top, width, height, fill_color=chart_bg,
             line_color=C_ACCENT, line_width_pt=1)

    # Title
    add_textbox(slide, "NDVI Trend — 12-Month Rolling Average",
                left + Inches(0.1), top + Inches(0.08), width - Inches(0.2), Inches(0.3),
                font_size=10, bold=True, color=C_GOLD)

    # Axes
    axis_left  = left + Inches(0.35)
    axis_bottom = top + height - Inches(0.45)
    axis_width = width - Inches(0.5)
    axis_height = height - Inches(0.85)

    add_rect(slide, axis_left, top + Inches(0.42), Pt(1.5), axis_height,
             fill_color=C_GRAY)
    add_rect(slide, axis_left, axis_bottom, axis_width, Pt(1.5),
             fill_color=C_GRAY)

    # NDVI values per month (simulated — realistic crop cycle)
    ndvi_vals = [0.32, 0.28, 0.41, 0.65, 0.72, 0.78, 0.81, 0.75, 0.62, 0.48, 0.35, 0.29]
    months    = ["J","F","M","A","M","J","J","A","S","O","N","D"]
    n = len(ndvi_vals)
    bar_w = (axis_width - Inches(0.1)) / n
    max_v = 1.0

    for i, (v, m) in enumerate(zip(ndvi_vals, months)):
        bx = axis_left + Inches(0.05) + i * bar_w
        bh = axis_height * v / max_v
        by = axis_bottom - bh
        # colour: green when healthy, yellow/orange when low
        if v >= 0.65:
            bc = C_GREEN_ZONE
        elif v >= 0.45:
            bc = C_YELLOW_ZONE
        else:
            bc = C_ORANGE_ZONE
        add_rect(slide, bx, by, bar_w - Pt(3), bh, fill_color=bc)
        add_textbox(slide, m, bx, axis_bottom + Pt(3), bar_w, Inches(0.2),
                    font_size=7, color=C_GRAY, align=PP_ALIGN.CENTER)

    # Y-axis labels
    for label, frac in [("1.0", 1.0), ("0.6", 0.6), ("0.3", 0.3)]:
        ly = axis_bottom - axis_height * frac
        add_textbox(slide, label, left, ly - Pt(6), Inches(0.32), Pt(14),
                    font_size=7, color=C_GRAY, align=PP_ALIGN.RIGHT)
        add_rect(slide, axis_left, ly, axis_width, Pt(0.5),
                 fill_color=RGBColor(0x33, 0x44, 0x33))


# ─── Slide builders ──────────────────────────────────────────────────────────

def slide_01_title(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, C_DARK)

    # Full-height left green panel
    add_rect(slide, 0, 0, Inches(5.6), SLIDE_H, fill_color=C_PRIMARY)
    # Gold accent stripe
    add_rect(slide, Inches(5.6), 0, Inches(0.08), SLIDE_H, fill_color=C_GOLD)

    # Logo text + leaf icon (text-based)
    add_textbox(slide, "🌿 AgroLens", Inches(0.4), Inches(0.6), Inches(5), Inches(1.0),
                font_size=44, bold=True, color=C_WHITE, font_name="Calibri")

    add_textbox(slide, "Precision Pesticide Intelligence\nvia Satellite AI",
                Inches(0.4), Inches(1.6), Inches(5), Inches(1.4),
                font_size=22, bold=False, color=C_OFF_WHITE, font_name="Calibri")

    # Divider line
    add_rect(slide, Inches(0.4), Inches(3.1), Inches(2.8), Pt(2), fill_color=C_GOLD)

    add_textbox(slide, "Reduce pesticide use by 20–40%\nthrough satellite-driven VRA maps.",
                Inches(0.4), Inches(3.2), Inches(5), Inches(1.0),
                font_size=14, color=C_ACCENT, italic=True, font_name="Calibri")

    # Bottom-left info
    add_textbox(slide, "Seed Round  |  May 2026  |  Confidential",
                Inches(0.4), Inches(6.6), Inches(5), Inches(0.4),
                font_size=11, color=C_GRAY, font_name="Calibri")

    # Right panel: field map visual
    draw_field_map(slide, Inches(5.9), Inches(0.5), Inches(7.1), Inches(5.8))

    # Overlay stats badges
    add_pill(slide, "€11.7B Market", Inches(6.3), Inches(6.45), Inches(1.8), Inches(0.42),
             bg=C_GOLD, fg=C_DARK, font_size=12)
    add_pill(slide, "20–40% Input Savings", Inches(8.4), Inches(6.45), Inches(2.4), Inches(0.42),
             bg=C_ACCENT, fg=C_WHITE, font_size=12)
    add_pill(slide, "€0 Satellite Cost", Inches(11.1), Inches(6.45), Inches(1.9), Inches(0.42),
             bg=C_MID, fg=C_WHITE, font_size=12)

    return slide


def slide_02_problem(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, RGBColor(0xF7, 0xF3, 0xEA))

    dark_header_band(slide)
    slide_label(slide, "The Problem")
    slide_subtitle(slide, "Farmers are flying blind — and paying for it.")

    # Three problem cards
    cards = [
        ("💸", "Wasted Money",
         "Farmers apply pesticides uniformly across entire fields — even where crops\nare healthy and don't need treatment.",
         "€20–50 wasted\nper hectare, per season"),
        ("🌍", "Environmental Harm",
         "Over-application leaches into groundwater, harms biodiversity,\nand violates EU Farm to Fork targets.",
         "EU mandates 50% reduction\nin pesticide use by 2030"),
        ("📋", "Compliance Burden",
         "German law §67 PflSchG requires full documentation of every\napplication — manual records are error-prone and time-consuming.",
         "Fines up to €50,000\nfor non-compliance"),
    ]

    for i, (icon, title, body, stat) in enumerate(cards):
        cx = Inches(0.4) + i * Inches(4.27)
        cy = Inches(1.45)
        cw = Inches(4.0)
        ch = Inches(5.5)

        # Card shadow
        add_rect(slide, cx + Pt(4), cy + Pt(4), cw, ch,
                 fill_color=RGBColor(0xCC, 0xC5, 0xB2))
        # Card body
        add_rect(slide, cx, cy, cw, ch,
                 fill_color=C_WHITE, line_color=RGBColor(0xDD, 0xD5, 0xBB), line_width_pt=1)
        # Card top accent strip
        add_rect(slide, cx, cy, cw, Inches(0.08), fill_color=C_GOLD)

        # Icon
        add_textbox(slide, icon, cx + Inches(0.15), cy + Inches(0.18),
                    Inches(0.7), Inches(0.7), font_size=34, color=C_DARK_TEXT)
        # Title
        add_textbox(slide, title, cx + Inches(0.15), cy + Inches(0.92),
                    cw - Inches(0.3), Inches(0.42),
                    font_size=18, bold=True, color=C_PRIMARY, font_name="Calibri")
        # Body
        add_textbox(slide, body, cx + Inches(0.15), cy + Inches(1.42),
                    cw - Inches(0.3), Inches(2.0),
                    font_size=13, color=C_DARK_TEXT, font_name="Calibri")
        # Stat badge at bottom
        add_rect(slide, cx + Inches(0.15), cy + Inches(3.8),
                 cw - Inches(0.3), Inches(1.35), fill_color=C_OFF_WHITE)
        add_textbox(slide, stat, cx + Inches(0.2), cy + Inches(3.92),
                    cw - Inches(0.4), Inches(1.2),
                    font_size=14, bold=True, color=C_PRIMARY, font_name="Calibri")

    # Source note
    add_textbox(slide, "Sources: McKinsey Voice of the Global Farmer 2024 · EU Farm to Fork Strategy · §67 PflSchG",
                Inches(0.4), Inches(7.15), Inches(12), Inches(0.3),
                font_size=8, color=C_GRAY, font_name="Calibri")

    return slide


def slide_03_solution(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, C_DARK)

    dark_header_band(slide)
    slide_label(slide, "The Solution")
    slide_subtitle(slide, "AgroLens turns free satellite data into actionable pesticide prescription maps.")

    # Left: field map
    draw_field_map(slide, Inches(0.4), Inches(1.35), Inches(5.8), Inches(5.6))

    # Right: value props
    props = [
        ("🛰️", "Sentinel-2 Satellite Imagery",
         "ESA provides free multispectral imagery every 5 days. Zero data cost — a structural advantage competitors can't match."),
        ("🧠", "AI Zone Detection",
         "Our ML pipeline computes NDVI & NDRE indices and runs k-means clustering to split every field into stress zones automatically."),
        ("🗺️", "Variable Rate Prescription",
         "Each zone gets a precise spray rate (60%–130% of base). Spray less where healthy, more where stressed."),
        ("📲", "ISOBUS-Ready Export",
         "Prescription maps export as TASKDATA.XML (ISO 11783-10) for direct upload to any modern tractor terminal. No manual entry."),
    ]

    for i, (icon, title, body) in enumerate(props):
        py = Inches(1.45) + i * Inches(1.45)
        add_rect(slide, Inches(6.5), py, Inches(6.5), Inches(1.28),
                 fill_color=RGBColor(0x1A, 0x2E, 0x1A),
                 line_color=C_ACCENT, line_width_pt=1)

        add_textbox(slide, icon, Inches(6.65), py + Inches(0.2),
                    Inches(0.55), Inches(0.55), font_size=24, color=C_GOLD)
        add_textbox(slide, title, Inches(7.2), py + Inches(0.1),
                    Inches(5.6), Inches(0.35),
                    font_size=14, bold=True, color=C_GOLD, font_name="Calibri")
        add_textbox(slide, body, Inches(7.2), py + Inches(0.48),
                    Inches(5.6), Inches(0.72),
                    font_size=12, color=C_OFF_WHITE, font_name="Calibri")

    return slide


def slide_04_how_it_works(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, RGBColor(0xF4, 0xF9, 0xF4))

    dark_header_band(slide)
    slide_label(slide, "How It Works")
    slide_subtitle(slide, "Five steps from satellite orbit to tractor terminal — fully automated.")

    steps = [
        ("1", "Field Upload", "Farmer draws field boundary on map or uploads GeoJSON/KML", "🗺️"),
        ("2", "Imagery Fetch", "Sentinel-2 L2A scenes retrieved automatically via Copernicus API every 5 days", "🛰️"),
        ("3", "Index Computation", "NDVI & NDRE computed per pixel. Cloud masking and 10-day median compositing", "📊"),
        ("4", "Zone Delineation", "k-means clustering splits each field into management zones (low/mid/high stress)", "🔬"),
        ("5", "Prescription Export", "VRA rates assigned per zone → TASKDATA.XML + Shapefile + PDF report generated", "📥"),
    ]

    box_top = Inches(1.5)
    box_h   = Inches(4.8)
    box_w   = Inches(2.28)
    arrow_w = Inches(0.25)

    for i, (num, title, body, icon) in enumerate(steps):
        bx = Inches(0.35) + i * (box_w + arrow_w)

        # Box
        add_rect(slide, bx, box_top, box_w, box_h,
                 fill_color=C_WHITE,
                 line_color=C_PRIMARY, line_width_pt=2)
        # Top accent
        add_rect(slide, bx, box_top, box_w, Inches(0.06), fill_color=C_PRIMARY)
        # Number circle (simulated with bold text)
        add_rect(slide, bx + box_w/2 - Inches(0.32), box_top + Inches(0.15),
                 Inches(0.64), Inches(0.64), fill_color=C_PRIMARY)
        add_textbox(slide, num,
                    bx + box_w/2 - Inches(0.32), box_top + Inches(0.15),
                    Inches(0.64), Inches(0.64),
                    font_size=20, bold=True, color=C_WHITE,
                    align=PP_ALIGN.CENTER)

        # Icon
        add_textbox(slide, icon,
                    bx + box_w/2 - Inches(0.5), box_top + Inches(0.95),
                    Inches(1.0), Inches(0.8), font_size=32, align=PP_ALIGN.CENTER)

        # Title
        add_textbox(slide, title,
                    bx + Inches(0.12), box_top + Inches(1.85),
                    box_w - Inches(0.24), Inches(0.5),
                    font_size=14, bold=True, color=C_PRIMARY,
                    align=PP_ALIGN.CENTER, font_name="Calibri")

        # Body
        add_textbox(slide, body,
                    bx + Inches(0.12), box_top + Inches(2.45),
                    box_w - Inches(0.24), Inches(2.0),
                    font_size=11, color=C_DARK_TEXT,
                    align=PP_ALIGN.CENTER, font_name="Calibri")

        # Arrow (except last)
        if i < len(steps) - 1:
            ax = bx + box_w + Inches(0.04)
            ay = box_top + box_h / 2 - Inches(0.18)
            add_textbox(slide, "→", ax, ay, Inches(0.22), Inches(0.4),
                        font_size=20, bold=True, color=C_PRIMARY, align=PP_ALIGN.CENTER)

    # Bottom note
    add_textbox(slide, "⏱  End-to-end processing completes within 24 hours of new imagery becoming available.",
                Inches(0.5), Inches(6.6), Inches(12), Inches(0.35),
                font_size=12, bold=True, color=C_PRIMARY, font_name="Calibri")

    return slide


def slide_05_product(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, C_DARK)

    dark_header_band(slide)
    slide_label(slide, "Product")
    slide_subtitle(slide, "Dashboard · Prescription Map · NDVI Analytics · Mobile-Ready PWA")

    # Large field map (left)
    draw_field_map(slide, Inches(0.35), Inches(1.35), Inches(6.8), Inches(5.4))

    # Right panel: NDVI chart (top)
    draw_ndvi_chart(slide, Inches(7.4), Inches(1.35), Inches(5.6), Inches(2.7))

    # Right panel: feature list (bottom)
    feature_panel_top = Inches(4.2)
    add_rect(slide, Inches(7.4), feature_panel_top, Inches(5.6), Inches(2.55),
             fill_color=RGBColor(0x12, 0x22, 0x12),
             line_color=C_ACCENT, line_width_pt=1)

    features = [
        "✓  Mapbox GL satellite basemap with live NDVI overlay",
        "✓  Recharts time-series with 12-month NDVI history",
        "✓  One-click ISOBUS export (TASKDATA.XML + Shapefile + PDF)",
        "✓  Email/SMS alerts on crop stress threshold breach",
        "✓  Progressive Web App — works offline in the field",
        "✓  API access for ERP / farm management integrations",
    ]
    for j, feat in enumerate(features):
        add_textbox(slide, feat, Inches(7.6), feature_panel_top + Inches(0.15) + j * Inches(0.37),
                    Inches(5.2), Inches(0.35),
                    font_size=11, color=C_OFF_WHITE, font_name="Calibri")

    return slide


def slide_06_market(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, RGBColor(0xF4, 0xF9, 0xF4))

    dark_header_band(slide)
    slide_label(slide, "Market Opportunity")
    slide_subtitle(slide, "Precision agriculture is a $24B market growing at 13% CAGR — we target the highest-value segment.")

    # Three concentric circle simulation via nested rectangles
    cx = Inches(3.7)
    cy = Inches(4.4)
    circles = [
        (Inches(5.8), RGBColor(0xC8, 0xE6, 0xC9), "TAM", "$24.1B", "Global Precision Ag by 2030\n(Grand View Research, 13.1% CAGR)"),
        (Inches(4.0), RGBColor(0x81, 0xC7, 0x84), "SAM", "€264M ARR",  "33M ha digitally addressable\nin EU + US at €8/ha"),
        (Inches(2.2), C_PRIMARY,                   "SOM", "€3.95M",  "400K ha by Year 3 — \n1.2% of SAM"),
    ]
    for diam, color, label, value, desc in circles:
        r = diam / 2
        add_rect(slide, cx - r, cy - r, diam, diam, fill_color=color)
        # white label in shape (simulated)

    # Labels for circles (outside)
    label_data = [
        (Inches(0.3), Inches(2.5), "TAM", "$24.1B by 2030", "Global precision agriculture\n(Grand View Research, 13.1% CAGR)"),
        (Inches(0.3), Inches(3.8), "SAM", "€264M ARR potential", "33M digitally addressable hectares\nin EU + US at €8/ha blended"),
        (Inches(0.3), Inches(5.1), "SOM", "€3.95M ARR by Year 3", "400,000 ha managed · 1.2% of SAM"),
    ]
    tam_colors = [C_PRIMARY, C_MID, C_ACCENT]
    for k, (lx, ly, tag, val, desc) in enumerate(label_data):
        add_rect(slide, lx, ly, Inches(0.22), Inches(0.22), fill_color=tam_colors[k])
        add_textbox(slide, f"{tag}: {val}",
                    lx + Inches(0.3), ly - Pt(3), Inches(3.0), Inches(0.3),
                    font_size=13, bold=True, color=C_PRIMARY, font_name="Calibri")
        add_textbox(slide, desc,
                    lx + Inches(0.3), ly + Inches(0.28), Inches(3.0), Inches(0.55),
                    font_size=11, color=C_DARK_TEXT, font_name="Calibri")

    # Circle text overlays
    add_textbox(slide, "TAM", cx - Inches(2.5), cy - Inches(0.2), Inches(0.8), Inches(0.5),
                font_size=13, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_textbox(slide, "SAM", cx - Inches(1.5), cy - Inches(0.2), Inches(0.8), Inches(0.5),
                font_size=13, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_textbox(slide, "SOM", cx - Inches(0.5), cy - Inches(0.15), Inches(0.8), Inches(0.4),
                font_size=11, bold=True, color=C_GOLD, align=PP_ALIGN.CENTER)

    # Right: growth drivers
    rx = Inches(7.8)
    add_textbox(slide, "Why Now?", rx, Inches(1.45), Inches(5.2), Inches(0.45),
                font_size=18, bold=True, color=C_PRIMARY, font_name="Calibri")

    drivers = [
        ("📈", "13.1% CAGR", "Fastest-growing segment of digital agriculture globally"),
        ("🌍", "EU Farm to Fork", "Binding target: −50% pesticide use by 2030 — compliance tools are mandatory"),
        ("💶", "CAP Eco-Schemes", "Direct EU subsidy payments for documented precision application"),
        ("🛰️", "Open Satellite Data", "ESA Copernicus provides free 5-day imagery — our zero-cost data moat"),
        ("⚡", "Input Price Inflation", "Pesticide costs surged 40–60% post-2022 — ROI for VRA tools doubled"),
    ]
    for j, (icon, title, desc) in enumerate(drivers):
        dy = Inches(2.0) + j * Inches(0.95)
        add_rect(slide, rx, dy, Inches(5.2), Inches(0.82),
                 fill_color=C_WHITE, line_color=RGBColor(0xBB, 0xDD, 0xBB), line_width_pt=1)
        add_textbox(slide, icon, rx + Inches(0.1), dy + Inches(0.12),
                    Inches(0.5), Inches(0.5), font_size=20)
        add_textbox(slide, title, rx + Inches(0.65), dy + Inches(0.06),
                    Inches(1.6), Inches(0.3),
                    font_size=12, bold=True, color=C_PRIMARY)
        add_textbox(slide, desc, rx + Inches(0.65), dy + Inches(0.4),
                    Inches(4.4), Inches(0.35),
                    font_size=11, color=C_DARK_TEXT)

    add_textbox(slide, "Source: Grand View Research 2024 · EU Commission DG AGRI · GMInsights",
                Inches(0.4), Inches(7.2), Inches(12), Inches(0.25),
                font_size=8, color=C_GRAY)

    return slide


def slide_07_business_model(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, C_DARK)

    dark_header_band(slide)
    slide_label(slide, "Business Model")
    slide_subtitle(slide, "Per-hectare SaaS subscription + API licensing + government contracts.")

    # Pricing tiers
    tiers = [
        ("Basis",   "Free",         "1 field · 15 ha · NDVI only",    False, C_GRAY),
        ("Starter", "€49 /mo",      "5 fields · 100 ha · All exports", False, C_MID),
        ("Farmer",  "€149 /mo",     "50 fields · 500 ha · Full suite", True,  C_GOLD),
        ("Pro",     "€599 /mo",     "Unlimited · Lohnunternehmer",     False, C_ACCENT),
    ]

    for i, (name, price, desc, highlight, color) in enumerate(tiers):
        tx = Inches(0.35) + i * Inches(3.22)
        ty = Inches(1.55)
        tw = Inches(3.0)
        th = Inches(3.5)

        bg_col = RGBColor(0x1A, 0x30, 0x1A) if not highlight else RGBColor(0x2B, 0x4A, 0x15)
        add_rect(slide, tx, ty, tw, th, fill_color=bg_col,
                 line_color=color, line_width_pt=2 if highlight else 1)
        add_rect(slide, tx, ty, tw, Inches(0.06), fill_color=color)

        if highlight:
            add_pill(slide, "RECOMMENDED", tx + Inches(0.6), ty - Inches(0.35),
                     Inches(1.8), Inches(0.3), bg=C_GOLD, fg=C_DARK, font_size=9)

        add_textbox(slide, name, tx + Inches(0.15), ty + Inches(0.2),
                    tw - Inches(0.3), Inches(0.4),
                    font_size=16, bold=True, color=color, font_name="Calibri")
        add_textbox(slide, price, tx + Inches(0.15), ty + Inches(0.65),
                    tw - Inches(0.3), Inches(0.65),
                    font_size=28, bold=True, color=C_WHITE, font_name="Calibri")
        add_textbox(slide, desc, tx + Inches(0.15), ty + Inches(1.4),
                    tw - Inches(0.3), Inches(0.6),
                    font_size=12, color=C_OFF_WHITE, font_name="Calibri")

        # Annual discount note
        if price != "Free":
            monthly_val = int(price.replace("€","").replace(" /mo",""))
            annual_val = monthly_val * 10  # ~20% off approx
            add_textbox(slide, f"€{annual_val:,} /yr  (save 20%)",
                        tx + Inches(0.15), ty + Inches(2.1),
                        tw - Inches(0.3), Inches(0.4),
                        font_size=11, color=C_GRAY, italic=True, font_name="Calibri")

    # Revenue streams
    add_textbox(slide, "Revenue Streams", Inches(0.35), Inches(5.35),
                Inches(12), Inches(0.45),
                font_size=18, bold=True, color=C_GOLD, font_name="Calibri")

    streams = [
        ("Primary: SaaS Subscriptions",
         "Per-farm, per-hectare recurring revenue. Predictable, scalable, high-margin (72–83% gross margin)."),
        ("Secondary: API Licensing",
         "Agri-retailers embed AgroLens data at €2.50/ha/yr. Minimum €10K/contract. Near-zero marginal cost."),
        ("Tertiary: Government Contracts",
         "National agencies & research institutions pay €100K–500K/yr for regional monitoring data."),
    ]

    for j, (title, body) in enumerate(streams):
        sx = Inches(0.35) + j * Inches(4.32)
        add_rect(slide, sx, Inches(5.9), Inches(4.1), Inches(1.3),
                 fill_color=RGBColor(0x1A, 0x30, 0x1A),
                 line_color=C_ACCENT, line_width_pt=1)
        add_textbox(slide, title, sx + Inches(0.12), Inches(5.98),
                    Inches(3.86), Inches(0.38),
                    font_size=12, bold=True, color=C_ACCENT, font_name="Calibri")
        add_textbox(slide, body, sx + Inches(0.12), Inches(6.42),
                    Inches(3.86), Inches(0.72),
                    font_size=10, color=C_OFF_WHITE, font_name="Calibri")

    return slide


def slide_08_financials(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, RGBColor(0xF4, 0xF9, 0xF4))

    dark_header_band(slide)
    slide_label(slide, "Financial Projections")
    slide_subtitle(slide, "Conservative path to EBITDA breakeven at Month 30 (Q3 2028).")

    # Table
    headers = ["Metric", "Year 1 — 2026", "Year 2 — 2027", "Year 3 — 2028"]
    rows = [
        ["Subscribed Hectares",        "20,000 ha",    "120,000 ha",   "400,000 ha"],
        ["SaaS ARR",                   "€160,000",     "€960,000",     "€3,200,000"],
        ["API Licensing",              "—",            "€90,000",      "€300,000"],
        ["Government Contracts",       "—",            "€150,000",     "€450,000"],
        ["Total ARR",                  "€160,000",     "€1,200,000",   "€3,950,000"],
        ["Gross Profit (72–83% GM)",   "€115,000",     "€936,000",     "€3,279,000"],
        ["Operating Expenses",         "€480,000",     "€1,100,000",   "€2,200,000"],
        ["EBITDA",                     "−€365,000",    "−€164,000",    "+€1,079,000"],
    ]

    col_widths = [Inches(3.1), Inches(2.9), Inches(2.9), Inches(3.2)]
    col_starts = [Inches(0.35)]
    for w in col_widths[:-1]:
        col_starts.append(col_starts[-1] + w)

    row_h = Inches(0.54)
    table_top = Inches(1.42)

    # Header row
    for j, (hdr, cx, cw) in enumerate(zip(headers, col_starts, col_widths)):
        bg = C_PRIMARY if j == 0 else RGBColor(0x2E, 0x7D, 0x32)
        add_rect(slide, cx, table_top, cw - Pt(2), row_h, fill_color=bg)
        add_textbox(slide, hdr, cx + Inches(0.08), table_top + Pt(6),
                    cw - Inches(0.16), row_h - Pt(6),
                    font_size=13, bold=True, color=C_WHITE,
                    align=PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT, font_name="Calibri")

    for i, row in enumerate(rows):
        ry = table_top + (i + 1) * row_h
        is_highlight = row[0] in ("Total ARR", "EBITDA")
        for j, (cell, cx, cw) in enumerate(zip(row, col_starts, col_widths)):
            if is_highlight:
                bg = C_PRIMARY if j == 0 else RGBColor(0xE8, 0xF5, 0xE9)
            elif i % 2 == 0:
                bg = C_WHITE
            else:
                bg = RGBColor(0xF1, 0xF8, 0xF1)
            add_rect(slide, cx, ry, cw - Pt(2), row_h, fill_color=bg,
                     line_color=RGBColor(0xCC, 0xDD, 0xCC), line_width_pt=0.5)
            text_color = C_PRIMARY if is_highlight else C_DARK_TEXT
            is_negative = cell.startswith("−")
            if is_negative:
                text_color = RGBColor(0xB7, 0x1C, 0x1C)
            if cell == "+€1,079,000":
                text_color = C_MID
            add_textbox(slide, cell, cx + Inches(0.08), ry + Pt(4),
                        cw - Inches(0.16), row_h - Pt(4),
                        font_size=13, bold=is_highlight, color=text_color,
                        align=PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT, font_name="Calibri")

    # Key assumptions
    assume_top = Inches(6.42)
    add_textbox(slide, "Key Assumptions",
                Inches(0.35), assume_top, Inches(12), Inches(0.3),
                font_size=12, bold=True, color=C_PRIMARY, font_name="Calibri")
    add_textbox(slide,
                "Average farm: 400 ha  ·  Blended ARPU: €8/ha/yr  ·  Annual churn: 15% Y1 → 7% Y3  ·  Infra cost: €0.20/ha/yr  ·  Team: 4 FTE Y1",
                Inches(0.35), assume_top + Inches(0.32), Inches(12.5), Inches(0.3),
                font_size=10, color=C_SUBTLE_TEXT, font_name="Calibri")

    return slide


def slide_09_unit_economics(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, C_DARK)

    dark_header_band(slide)
    slide_label(slide, "Unit Economics")
    slide_subtitle(slide, "Strong LTV:CAC ratio and a 6-month payback period from day one.")

    metrics = [
        ("13.3×", "LTV : CAC", "Target is >3×\nWe are 4× above benchmark"),
        ("6 mo",  "CAC Payback", "€1,200 CAC recovered in\n6 months at 72% gross margin"),
        ("€16K",  "LTV (EU farm)", "400 ha farm · €3,200 ACV\n5-year avg. lifetime"),
        ("97%",   "Data-Layer GM", "Sentinel-2 cost = €0\nInfra cost = €0.20/ha/yr"),
        ("€0.20", "Infra per ha", "Total compute + storage\nper hectare per year"),
    ]

    for i, (value, label, note) in enumerate(metrics):
        mx = Inches(0.35) + i * Inches(2.58)
        my = Inches(1.65)
        mw = Inches(2.4)
        mh = Inches(3.8)

        add_rect(slide, mx, my, mw, mh,
                 fill_color=RGBColor(0x12, 0x22, 0x12),
                 line_color=C_GOLD, line_width_pt=1.5)
        add_rect(slide, mx, my, mw, Inches(0.06), fill_color=C_GOLD)

        add_textbox(slide, value,
                    mx + Inches(0.1), my + Inches(0.3), mw - Inches(0.2), Inches(1.1),
                    font_size=38, bold=True, color=C_GOLD,
                    align=PP_ALIGN.CENTER, font_name="Calibri")
        add_textbox(slide, label,
                    mx + Inches(0.1), my + Inches(1.5), mw - Inches(0.2), Inches(0.5),
                    font_size=14, bold=True, color=C_WHITE,
                    align=PP_ALIGN.CENTER, font_name="Calibri")
        add_textbox(slide, note,
                    mx + Inches(0.1), my + Inches(2.1), mw - Inches(0.2), Inches(1.3),
                    font_size=11, color=C_GRAY,
                    align=PP_ALIGN.CENTER, font_name="Calibri")

    # Bottom: CAC by channel
    add_textbox(slide, "Customer Acquisition by Channel",
                Inches(0.35), Inches(5.7), Inches(12), Inches(0.38),
                font_size=15, bold=True, color=C_GOLD)

    channels = [
        ("Content / Inbound", "€400–800 / customer", "Lowest cost · scales automatically"),
        ("Cooperative Partners", "€600–1,200 / customer", "Shared cost · high volume access"),
        ("Direct Outbound", "€1,500–3,000 / customer", "Large farms · high ACV offsets cost"),
        ("Blended Y1 / Y2", "€1,200 / €800", "Improves as brand awareness builds"),
    ]
    for j, (ch, cac, note) in enumerate(channels):
        cx2 = Inches(0.35) + j * Inches(3.22)
        add_rect(slide, cx2, Inches(6.15), Inches(3.1), Inches(1.1),
                 fill_color=RGBColor(0x1A, 0x30, 0x1A),
                 line_color=C_MID, line_width_pt=1)
        add_textbox(slide, ch, cx2 + Inches(0.12), Inches(6.22),
                    Inches(2.86), Inches(0.3), font_size=11, bold=True, color=C_ACCENT)
        add_textbox(slide, cac, cx2 + Inches(0.12), Inches(6.56),
                    Inches(2.86), Inches(0.28), font_size=13, bold=True, color=C_WHITE)
        add_textbox(slide, note, cx2 + Inches(0.12), Inches(6.87),
                    Inches(2.86), Inches(0.28), font_size=10, color=C_GRAY)

    return slide


def slide_10_competition(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, RGBColor(0xF4, 0xF9, 0xF4))

    dark_header_band(slide)
    slide_label(slide, "Competitive Landscape")
    slide_subtitle(slide, "We sit at the intersection of open data, regulatory alignment, and pure-play focus.")

    # Positioning matrix
    matrix_left   = Inches(0.35)
    matrix_top    = Inches(1.45)
    matrix_width  = Inches(6.8)
    matrix_height = Inches(5.6)

    # Background
    add_rect(slide, matrix_left, matrix_top, matrix_width, matrix_height,
             fill_color=C_WHITE, line_color=RGBColor(0xCC, 0xDD, 0xCC), line_width_pt=1)

    # Quadrant lines
    mx_mid_x = matrix_left + matrix_width / 2
    mx_mid_y = matrix_top + matrix_height / 2
    add_rect(slide, mx_mid_x, matrix_top, Pt(1), matrix_height, fill_color=C_GRAY)
    add_rect(slide, matrix_left, mx_mid_y, matrix_width, Pt(1), fill_color=C_GRAY)

    # Axis labels
    add_textbox(slide, "← Higher Data Cost", matrix_left + Inches(0.1), matrix_top + matrix_height + Pt(4),
                matrix_width / 2, Inches(0.3), font_size=9, color=C_GRAY, italic=True)
    add_textbox(slide, "Lower Data Cost →", matrix_left + matrix_width / 2 + Inches(0.1), matrix_top + matrix_height + Pt(4),
                matrix_width / 2, Inches(0.3), font_size=9, color=C_PRIMARY, italic=True, bold=True)
    add_textbox(slide, "↑ Pesticide VRA Focus",
                matrix_left - Inches(0.12), matrix_top + Inches(0.1), Inches(0.25), Inches(3.0),
                font_size=9, color=C_PRIMARY, italic=True, bold=True)
    add_textbox(slide, "General Purpose ↓",
                matrix_left - Inches(0.12), matrix_top + matrix_height / 2 + Inches(0.1), Inches(0.25), Inches(2.5),
                font_size=9, color=C_GRAY, italic=True)

    # Competitor bubbles: (name, x_frac, y_frac, color, size_pt)
    competitors = [
        ("AgroLens",  0.78, 0.15, C_PRIMARY,     42, True),
        ("Taranis",   0.25, 0.35, C_ORANGE_ZONE, 28, False),
        ("FieldView", 0.3,  0.75, C_RED_ZONE,    36, False),
        ("EOSDA",     0.55, 0.55, C_YELLOW_ZONE, 24, False),
        ("F.Edge",    0.2,  0.6,  C_GRAY,        22, False),
    ]
    for (name, xf, yf, color, size, is_us) in competitors:
        bx = matrix_left + matrix_width * xf
        by = matrix_top  + matrix_height * yf
        r  = Inches(size / 144)
        add_rect(slide, bx - r, by - r, r*2, r*2, fill_color=color)
        label_col = C_WHITE if is_us else C_DARK_TEXT
        add_textbox(slide, name, bx - Inches(0.6), by + r + Pt(2), Inches(1.2), Inches(0.3),
                    font_size=10, bold=is_us, color=C_PRIMARY if is_us else C_DARK_TEXT,
                    align=PP_ALIGN.CENTER)
        if is_us:
            add_textbox(slide, "★ You are here", bx - Inches(0.7), by - r - Inches(0.35),
                        Inches(1.5), Inches(0.3), font_size=9, bold=True, color=C_GOLD,
                        align=PP_ALIGN.CENTER)

    # Right: competitor table
    comp_table_left = Inches(7.4)
    col_headers = ["", "AgroLens", "Taranis", "FieldView", "EOSDA"]
    comp_rows = [
        ("Satellite data cost",     "Free ✓",  "Paid ✗",    "Mixed",    "Paid ✗"),
        ("VRA pesticide focus",     "Pure ✓",  "Partial",   "Minimal ✗","Partial"),
        ("EU regulatory tools",     "Built-in ✓","Limited ✗","Limited ✗","Limited ✗"),
        ("Independent of sellers",  "Yes ✓",   "Yes",       "No ✗",     "Yes"),
        ("Price (€/ha/yr)",         "€4–12",   "€15–25",   "€7–12",    "€5–15"),
        ("Hardware required",       "No ✓",    "Partial",   "No",       "No"),
    ]

    cw_list = [Inches(1.7), Inches(1.2), Inches(1.2), Inches(1.2), Inches(1.2)]
    cs_list = [comp_table_left]
    for w in cw_list[:-1]:
        cs_list.append(cs_list[-1] + w)

    crh = Inches(0.45)
    crt = Inches(1.5)

    for j, hdr in enumerate(col_headers):
        bg = C_PRIMARY if j == 0 else (C_GOLD if j == 1 else RGBColor(0x4A, 0x6A, 0x4A))
        add_rect(slide, cs_list[j], crt, cw_list[j] - Pt(1), crh, fill_color=bg)
        add_textbox(slide, hdr, cs_list[j] + Pt(3), crt + Pt(4),
                    cw_list[j] - Pt(6), crh - Pt(4),
                    font_size=10, bold=True, color=C_WHITE,
                    align=PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT)

    for i, row in enumerate(comp_rows):
        ry2 = crt + (i+1) * crh
        for j, (cell, cx2, cw2) in enumerate(zip(row, cs_list, cw_list)):
            bg = C_WHITE if i % 2 == 0 else C_LIGHT_GRAY
            if j == 1:  # AgroLens column highlight
                bg = RGBColor(0xE8, 0xF5, 0xE9)
            add_rect(slide, cx2, ry2, cw2 - Pt(1), crh, fill_color=bg,
                     line_color=RGBColor(0xCC, 0xDD, 0xCC), line_width_pt=0.5)
            col = C_PRIMARY if j == 1 else C_DARK_TEXT
            if "✗" in str(cell):
                col = RGBColor(0xB7, 0x1C, 0x1C)
            if "✓" in str(cell):
                col = C_MID
            add_textbox(slide, str(cell), cx2 + Pt(3), ry2 + Pt(3),
                        cw2 - Pt(6), crh - Pt(3),
                        font_size=9, color=col,
                        align=PP_ALIGN.CENTER if j > 0 else PP_ALIGN.LEFT)

    return slide


def slide_11_regulatory(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, C_DARK)

    dark_header_band(slide)
    slide_label(slide, "Regulatory Tailwinds")
    slide_subtitle(slide, "Three independent mandates create structural demand for AgroLens.")

    tailwinds = [
        (
            "🇪🇺",
            "EU Farm to Fork Strategy",
            "Target: −50% pesticide use by 2030",
            [
                "Embedded in the European Green Deal — politically unmovable",
                "Individual Member States (Germany, France, Netherlands) advancing national plans",
                "AgroLens VRA maps serve as compliance documentation for eco-scheme payments",
                "CAP 2023–2027 eco-scheme payments directly reward documented precision application",
            ],
            "€32B in CAP eco-scheme\npayments available to farmers",
        ),
        (
            "🇩🇪",
            "German §67 PflSchG",
            "Pesticide application must be documented by law",
            [
                "Every spray event requires field ID, product, rate, date, applicator name",
                "AgroLens SprayingRecord model auto-generates §67-compliant documentation",
                "FLIK field identifier pre-filled from German InVeKoS database",
                "Fines up to €50,000 for non-compliance — compliance tool is non-negotiable",
            ],
            "600,000+ farms in Germany\nrequired to comply",
        ),
        (
            "🇺🇸",
            "US EPA ESA Pesticide Strategies",
            "Herbicide Strategy (Aug 2024) + Insecticide Strategy (Apr 2025)",
            [
                "Mitigation requirements for pesticide use near endangered species habitats",
                "Farmers in ESA zones face legal risk from blanket application",
                "VRA prescription maps provide defensible compliance record",
                "EPA consultations expected to extend into the 2030s",
            ],
            "130M+ acres of US row crops\naffected by ESA mitigation zones",
        ),
    ]

    for i, (flag, title, subtitle, bullets, stat) in enumerate(tailwinds):
        tx = Inches(0.35) + i * Inches(4.3)
        ty = Inches(1.5)
        tw = Inches(4.1)
        th = Inches(5.6)

        add_rect(slide, tx, ty, tw, th,
                 fill_color=RGBColor(0x12, 0x22, 0x12),
                 line_color=C_GOLD, line_width_pt=1)
        add_rect(slide, tx, ty, tw, Inches(0.06), fill_color=C_GOLD)

        add_textbox(slide, flag, tx + Inches(0.12), ty + Inches(0.15),
                    Inches(0.5), Inches(0.45), font_size=26)
        add_textbox(slide, title, tx + Inches(0.65), ty + Inches(0.18),
                    tw - Inches(0.8), Inches(0.4),
                    font_size=14, bold=True, color=C_GOLD, font_name="Calibri")
        add_textbox(slide, subtitle, tx + Inches(0.12), ty + Inches(0.72),
                    tw - Inches(0.24), Inches(0.38),
                    font_size=11, color=C_ACCENT, italic=True, font_name="Calibri")

        for j, bullet in enumerate(bullets):
            add_textbox(slide, f"• {bullet}",
                        tx + Inches(0.12), ty + Inches(1.2) + j * Inches(0.68),
                        tw - Inches(0.24), Inches(0.6),
                        font_size=11, color=C_OFF_WHITE, font_name="Calibri")

        add_rect(slide, tx + Inches(0.12), ty + th - Inches(1.15),
                 tw - Inches(0.24), Inches(0.92), fill_color=RGBColor(0x1B, 0x38, 0x1B))
        add_textbox(slide, stat,
                    tx + Inches(0.18), ty + th - Inches(1.05),
                    tw - Inches(0.36), Inches(0.8),
                    font_size=12, bold=True, color=C_GOLD, font_name="Calibri")

    return slide


def slide_12_traction(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, RGBColor(0xF4, 0xF9, 0xF4))

    dark_header_band(slide)
    slide_label(slide, "Traction & Technology")
    slide_subtitle(slide, "Full-stack MVP built in 5 phases — production-ready, validator-approved.")

    phases = [
        ("Phase 0", "Foundation", "Docker, PostgreSQL + PostGIS, Redis, Alembic migrations, CI/CD", True),
        ("Phase 1", "Auth & Data Models", "User/Farm/Field ORM models, Supabase JWT auth, API key auth, rate limiting", True),
        ("Phase 2", "Satellite Pipeline", "Sentinel-2 imagery ingestion, NDVI/NDRE computation, cloud masking, AWS S3 storage", True),
        ("Phase 3", "AI Prescription Engine", "k-means zone delineation, VRA prescription rules, TASKDATA.XML + Shapefile + PDF export", True),
        ("Phase 4", "Dashboard UI", "Mapbox GL dashboard, Recharts NDVI analytics, notification preferences, API keys, PWA", True),
        ("Phase 5", "Billing (in build)", "Stripe subscriptions, plan enforcement, billing portal — currently under development", False),
    ]

    ph_top = Inches(1.5)
    ph_h   = Inches(0.78)
    ph_w   = Inches(12.6)

    for i, (phase, title, desc, done) in enumerate(phases):
        py = ph_top + i * (ph_h + Pt(5))
        bg = RGBColor(0xE8, 0xF5, 0xE9) if done else RGBColor(0xFF, 0xF9, 0xE6)
        border = C_MID if done else C_GOLD
        add_rect(slide, Inches(0.35), py, ph_w, ph_h,
                 fill_color=bg, line_color=border, line_width_pt=1.5)

        # Status badge
        status_text = "✅ DONE" if done else "🔧 IN BUILD"
        status_bg   = C_MID if done else C_GOLD
        status_fg   = C_WHITE if done else C_DARK
        add_pill(slide, status_text,
                 Inches(11.8), py + Inches(0.2), Inches(1.0), Inches(0.38),
                 bg=status_bg, fg=status_fg, font_size=9)

        add_textbox(slide, phase, Inches(0.48), py + Pt(6),
                    Inches(1.0), Inches(0.35),
                    font_size=10, bold=True, color=C_GRAY, font_name="Calibri")
        add_textbox(slide, title, Inches(1.6), py + Pt(5),
                    Inches(2.5), Inches(0.35),
                    font_size=14, bold=True, color=C_PRIMARY, font_name="Calibri")
        add_textbox(slide, desc, Inches(4.3), py + Pt(5),
                    Inches(7.4), Inches(0.35),
                    font_size=11, color=C_DARK_TEXT, font_name="Calibri")

    # Tech stack pills
    add_textbox(slide, "Tech Stack:", Inches(0.35), Inches(7.0), Inches(1.2), Inches(0.3),
                font_size=11, bold=True, color=C_PRIMARY)
    stack_items = ["FastAPI", "Next.js 14", "PostgreSQL+PostGIS", "Celery+Redis",
                   "scikit-learn", "Mapbox GL", "Supabase Auth", "AWS S3", "Stripe", "Sentry"]
    pill_x = Inches(1.6)
    for item in stack_items:
        pill_w = Inches(len(item) * 0.1 + 0.4)
        add_pill(slide, item, pill_x, Inches(7.0), pill_w, Inches(0.3),
                 bg=C_PRIMARY, fg=C_WHITE, font_size=9)
        pill_x += pill_w + Pt(5)

    return slide


def slide_13_ask(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, C_DARK)

    dark_header_band(slide)
    slide_label(slide, "Investment Ask")
    slide_subtitle(slide, "Seed round to reach 120,000 ha under management and EBITDA breakeven.")

    # Big ask number
    add_rect(slide, Inches(0.35), Inches(1.5), Inches(5.4), Inches(2.5),
             fill_color=RGBColor(0x12, 0x22, 0x12),
             line_color=C_GOLD, line_width_pt=2)
    add_textbox(slide, "€500K – €1.5M",
                Inches(0.5), Inches(1.7), Inches(5.1), Inches(1.1),
                font_size=38, bold=True, color=C_GOLD,
                align=PP_ALIGN.CENTER, font_name="Calibri")
    add_textbox(slide, "Seed Round  ·  18–24 months runway",
                Inches(0.5), Inches(2.8), Inches(5.1), Inches(0.45),
                font_size=15, color=C_OFF_WHITE,
                align=PP_ALIGN.CENTER, font_name="Calibri")

    # Use of funds
    add_textbox(slide, "Use of Funds", Inches(6.2), Inches(1.5), Inches(6.8), Inches(0.45),
                font_size=18, bold=True, color=C_GOLD)

    funds = [
        ("40%", "€600K",  "Product & Engineering",
         "Backend, ML pipeline, ISOBUS integrations, mobile app, EU cloud infra"),
        ("25%", "€375K",  "Sales & Marketing",
         "Cooperative partnerships, trade shows (Agritechnica), content, pilots"),
        ("20%", "€300K",  "Team",
         "CEO + 2 engineers + 1 agronomist advisor (18-month plan)"),
        ("15%", "€225K",  "Operations & Legal",
         "Entity formation, GDPR compliance, SOC 2, professional indemnity insurance"),
    ]
    for i, (pct, amount, category, detail) in enumerate(funds):
        fy = Inches(2.1) + i * Inches(1.1)
        add_rect(slide, Inches(6.2), fy, Inches(0.55), Inches(0.85), fill_color=C_GOLD)
        add_textbox(slide, pct, Inches(6.2), fy + Pt(8), Inches(0.55), Inches(0.55),
                    font_size=14, bold=True, color=C_DARK,
                    align=PP_ALIGN.CENTER, font_name="Calibri")
        add_textbox(slide, f"{amount}  —  {category}",
                    Inches(6.85), fy + Pt(4), Inches(6.0), Inches(0.35),
                    font_size=13, bold=True, color=C_WHITE, font_name="Calibri")
        add_textbox(slide, detail,
                    Inches(6.85), fy + Inches(0.45), Inches(6.0), Inches(0.35),
                    font_size=11, color=C_GRAY, font_name="Calibri")

    # Milestones funded
    add_textbox(slide, "Milestones This Round Funds", Inches(0.35), Inches(4.2),
                Inches(5.5), Inches(0.45), font_size=16, bold=True, color=C_GOLD)

    milestones = [
        "10 paid pilot farms onboarded (October 2026)",
        "Sentinel-2 pipeline live — first ISOBUS prescription delivered",
        "One cooperative partnership signed (50,000+ ha reach)",
        "120,000 ha under management by end of Year 2",
        "EU EIC Accelerator grant application submitted (co-investment)",
        "SOC 2 Type I audit initiated (Month 12)",
    ]
    for j, ms in enumerate(milestones):
        add_textbox(slide, f"→  {ms}",
                    Inches(0.35), Inches(4.8) + j * Inches(0.36),
                    Inches(5.5), Inches(0.34),
                    font_size=11, color=C_OFF_WHITE, font_name="Calibri")

    # Target investors
    add_textbox(slide, "Target Investors", Inches(6.2), Inches(4.8), Inches(6.8), Inches(0.35),
                font_size=13, bold=True, color=C_GOLD)
    investors = "Anterra Capital  ·  Astanor Ventures  ·  SYSTEMIQ Capital  ·  EIC Accelerator (EU)\nImpact-focused family offices  ·  Agri-tech corporate strategics"
    add_textbox(slide, investors, Inches(6.2), Inches(5.2), Inches(6.8), Inches(0.65),
                font_size=11, color=C_OFF_WHITE)

    return slide


def slide_14_contact(prs_obj):
    slide = prs_obj.slides.add_slide(blank_layout(prs_obj))
    fill_bg(slide, C_DARK)

    # Full-height left green panel
    add_rect(slide, 0, 0, Inches(5.6), SLIDE_H, fill_color=C_PRIMARY)
    add_rect(slide, Inches(5.6), 0, Inches(0.08), SLIDE_H, fill_color=C_GOLD)

    add_textbox(slide, "🌿 AgroLens", Inches(0.4), Inches(1.5), Inches(5), Inches(0.9),
                font_size=40, bold=True, color=C_WHITE, font_name="Calibri")
    add_textbox(slide, "Precision Pesticide Intelligence\nvia Satellite AI",
                Inches(0.4), Inches(2.5), Inches(5), Inches(1.0),
                font_size=18, color=C_OFF_WHITE, font_name="Calibri")

    add_rect(slide, Inches(0.4), Inches(3.7), Inches(2.8), Pt(2), fill_color=C_GOLD)

    summary_points = [
        "€11.7B precision ag market · 13.1% CAGR",
        "Free satellite data = structural cost moat",
        "20–40% pesticide reduction proven",
        "€3.95M ARR projected by Year 3",
        "Breakeven at Month 30 (Q3 2028)",
        "Seeking €500K–€1.5M seed round",
    ]
    for j, pt in enumerate(summary_points):
        add_textbox(slide, f"✓  {pt}",
                    Inches(0.4), Inches(3.9) + j * Inches(0.45),
                    Inches(5.0), Inches(0.42),
                    font_size=13, color=C_OFF_WHITE, font_name="Calibri")

    # Right: contact + next steps
    add_textbox(slide, "Let's Talk", Inches(6.1), Inches(1.5), Inches(7.0), Inches(0.65),
                font_size=34, bold=True, color=C_GOLD, font_name="Calibri")

    contact_lines = [
        "Daniel Schaller — Founder & CEO",
        "daniel.philipp.schaller@gmail.com",
        "agrolens.io",
        "Germany · May 2026",
    ]
    for j, line in enumerate(contact_lines):
        add_textbox(slide, line, Inches(6.1), Inches(2.3) + j * Inches(0.5),
                    Inches(7.0), Inches(0.45),
                    font_size=16 if j == 0 else 14,
                    bold=(j == 0), color=C_WHITE if j < 2 else C_GRAY,
                    font_name="Calibri")

    add_rect(slide, Inches(6.1), Inches(4.5), Inches(6.8), Pt(1.5), fill_color=C_ACCENT)

    add_textbox(slide, "Next Steps", Inches(6.1), Inches(4.65), Inches(6.8), Inches(0.4),
                font_size=16, bold=True, color=C_ACCENT, font_name="Calibri")

    next_steps = [
        "1.  30-minute product demo (live dashboard walkthrough)",
        "2.  Share data room: full financial model, cap table, IP overview",
        "3.  Reference calls: pilot farm contacts available on request",
        "4.  Term sheet target: August 2026",
    ]
    for j, ns in enumerate(next_steps):
        add_textbox(slide, ns, Inches(6.1), Inches(5.15) + j * Inches(0.45),
                    Inches(6.8), Inches(0.4),
                    font_size=13, color=C_OFF_WHITE, font_name="Calibri")

    add_textbox(slide, "This document is confidential and intended solely for accredited investors.",
                Inches(6.1), Inches(7.1), Inches(6.8), Inches(0.28),
                font_size=9, color=C_GRAY, italic=True, font_name="Calibri")

    return slide


# ─── Build & save ─────────────────────────────────────────────────────────────

def build_deck(output_path: str):
    p = prs()
    slide_01_title(p)
    slide_02_problem(p)
    slide_03_solution(p)
    slide_04_how_it_works(p)
    slide_05_product(p)
    slide_06_market(p)
    slide_07_business_model(p)
    slide_08_financials(p)
    slide_09_unit_economics(p)
    slide_10_competition(p)
    slide_11_regulatory(p)
    slide_12_traction(p)
    slide_13_ask(p)
    slide_14_contact(p)
    p.save(output_path)
    print(f"✅  Saved: {output_path}  ({len(p.slides)} slides)")


if __name__ == "__main__":
    import os
    out = os.path.join(os.path.dirname(__file__), "AgroLens_Investor_Deck.pptx")
    build_deck(out)
