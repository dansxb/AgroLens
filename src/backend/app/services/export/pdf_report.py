"""PDF prescription report generator.

Generates a printable PDF summary of a Variable Rate Application prescription
map.  The report includes:
  - Field name, FLIK-Nummer, date of composite data used
  - Per-zone rates table (zone label, area ha, multiplier, rate L/ha)
  - Estimated total product consumption vs. uniform application
  - Mandatory agronomist disclaimer (§ software-developer.md Phase 3 Rules)

Requires the ``reportlab`` package.  Falls back gracefully if not installed
(raises ImportError with an explanatory message).
"""

from __future__ import annotations

import io
import logging
from datetime import date
from typing import Optional

from app.models.management_zone import ManagementZone
from app.models.prescription import Prescription

from ml.prescription.engine import DISCLAIMER_DE

logger = logging.getLogger(__name__)


def build_prescription_pdf(
    zones: list[ManagementZone],
    prescriptions: list[Prescription],
    field_name: str,
    application_type: str,
    base_rate_l_ha: float,
    composite_start: date,
    composite_end: date,
    flik: Optional[str] = None,
) -> bytes:
    """Generate a PDF prescription report as bytes.

    Args:
        zones: Management zones ordered by zone_index ascending.
        prescriptions: Prescription records, one per zone.
        field_name: Human-readable field name.
        application_type: Type of application (fungicide / herbicide / insecticide).
        base_rate_l_ha: Farmer's base application rate in L/ha.
        composite_start: First date of the NDVI composite window.
        composite_end: Last date of the NDVI composite window.
        flik: FLIK-Nummer (optional).

    Returns:
        Bytes of the generated PDF document.

    Raises:
        ImportError: If reportlab is not installed.
        ValueError: If zones and prescriptions have mismatched counts.
    """
    try:
        from reportlab.lib import colors  # type: ignore[import]
        from reportlab.lib.pagesizes import A4  # type: ignore[import]
        from reportlab.lib.styles import getSampleStyleSheet  # type: ignore[import]
        from reportlab.lib.units import cm  # type: ignore[import]
        from reportlab.platypus import (  # type: ignore[import]
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError as exc:
        raise ImportError(
            "reportlab is required for PDF report generation. "
            "Install it with: pip install reportlab"
        ) from exc

    if len(zones) != len(prescriptions):
        raise ValueError(
            f"zones ({len(zones)}) and prescriptions ({len(prescriptions)}) must be same length."
        )

    pres_by_zone_id = {p.management_zone_id: p for p in prescriptions}

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(
        Paragraph("AgroLens — Pflanzenschutz-Applikationskarte", styles["Title"])
    )
    story.append(Spacer(1, 0.4 * cm))

    # Field info
    info_lines = [
        f"<b>Schlag:</b> {field_name}",
        f"<b>FLIK:</b> {flik or '—'}",
        f"<b>Maßnahme:</b> {application_type.capitalize()}",
        f"<b>Basismenge:</b> {base_rate_l_ha:.2f} L/ha",
        f"<b>Satellitenbilder:</b> {composite_start} – {composite_end}",
    ]
    for line in info_lines:
        story.append(Paragraph(line, styles["Normal"]))
    story.append(Spacer(1, 0.6 * cm))

    # Rates table
    table_data = [
        ["Zone", "Fläche (ha)", "Faktor", "Menge (L/ha)", "Hinweis"],
    ]
    mean_rate = 0.0
    for zone in zones:
        pres = pres_by_zone_id.get(zone.id)
        if pres is None:
            continue
        mean_rate += float(pres.rate_l_ha)
        flag = "⚠ Mindestmenge prüfen" if pres.below_minimum_floor else ""
        table_data.append(
            [
                zone.zone_label,
                f"{float(zone.area_ha):.2f}" if zone.area_ha else "—",
                f"{float(pres.multiplier):.2f}×",
                f"{float(pres.rate_l_ha):.2f}",
                flag,
            ]
        )
    if zones:
        mean_rate /= len(zones)

    savings_pct = (
        (1.0 - mean_rate / base_rate_l_ha) * 100 if base_rate_l_ha > 0 else 0.0
    )
    table_data.append(["Durchschnitt", "—", "—", f"{mean_rate:.2f}", ""])

    t = Table(table_data, colWidths=[3.5 * cm, 2.5 * cm, 2.5 * cm, 3 * cm, 5 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))

    # Savings summary
    story.append(
        Paragraph(
            f"<b>Einsparung gegenüber Einheitsdosierung:</b> {savings_pct:.1f}%",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.8 * cm))

    # Disclaimer
    disclaimer_style = styles["Normal"].clone("disclaimer")
    disclaimer_style.fontSize = 8
    disclaimer_style.textColor = colors.HexColor("#555555")
    story.append(Paragraph(f"<i>{DISCLAIMER_DE}</i>", disclaimer_style))

    doc.build(story)
    return buffer.getvalue()
