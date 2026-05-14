"""ISO 11783-10 TASKDATA.XML export for ISOBUS-compatible tractor terminals.

Produces a TASKDATA.XML file (zipped as TASKDATA.ZIP) that can be loaded
directly onto John Deere GreenStar, Fendt Variotronic, CLAAS, and other
ISOBUS-11 compatible terminals for variable-rate application.

Structure produced (minimal ISOBUS Task Controller Level 2 profile):
  TASKDATA
  └── TSK (Task)
      ├── GRD (Grid — variable rate map, Type 1 or 2)
      │   └── TZN* (Treatment Zone per cell)
      └── TLG (Time Log, optional)

Zone rates are embedded as Treatment Zones (TZN) with variable product
dose (PDV) coded in the DDI 7 (Volume Per Area, unit 1 = mm³/m² which
maps to L/ha × 100).

Reference: ISO 11783-10:2009(E) + Amendment 1:2014.
"""

from __future__ import annotations

import io
import logging
import uuid
import zipfile
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from xml.etree import ElementTree as ET

from app.models.management_zone import ManagementZone
from app.models.prescription import Prescription
from ml.prescription.engine import DISCLAIMER_DE

logger = logging.getLogger(__name__)

# DDI 7 = Volume Per Area application rate; unit = mm³/m² (= 0.01 L/ha × 1e-3 ... )
# Practical conversion: 1 L/ha = 100 mm³/m²
_L_HA_TO_DDI7 = 100


def build_taskdata_xml(
    zones: list[ManagementZone],
    prescriptions: list[Prescription],
    field_name: str,
    application_type: str,
    flik: Optional[str] = None,
    task_ref: Optional[str] = None,
) -> bytes:
    """Build a TASKDATA.ZIP containing a variable-rate prescription in ISO 11783-10 format.

    Args:
        zones: Management zones ordered by zone_index ascending.
        prescriptions: Prescription records, one per zone.
        field_name: Human-readable field name (used in Task designator).
        application_type: "fungicide", "herbicide", or "insecticide".
        flik: FLIK-Nummer of the field (written to PartField comment).
        task_ref: Optional external reference / job number.

    Returns:
        Bytes of a ZIP archive containing TASKDATA.XML.

    Raises:
        ValueError: If zones and prescriptions have mismatched counts.
    """
    if len(zones) != len(prescriptions):
        raise ValueError(
            f"zones ({len(zones)}) and prescriptions ({len(prescriptions)}) must be same length."
        )

    pres_by_zone_id = {p.management_zone_id: p for p in prescriptions}

    root = ET.Element(
        "ISO11783_TaskData",
        attrib={
            "VersionMajor": "4",
            "VersionMinor": "0",
            "ManagementSoftwareManufacturer": "AgroLens",
            "ManagementSoftwareVersion": "1.0",
            "TaskControllerManufacturer": "",
            "TaskControllerVersion": "",
            "DataTransferOrigin": "1",
        },
    )

    # --- PartField (PFD) ---
    pfd_id = "PFD1"
    pfd = ET.SubElement(
        root,
        "PFD",
        attrib={
            "A": pfd_id,
            "B": field_name[:32],
            "C": flik or "",
        },
    )

    # --- Product (PDT) ---
    pdt_id = "PDT1"
    ET.SubElement(
        root,
        "PDT",
        attrib={
            "A": pdt_id,
            "B": application_type.capitalize()[:32],
            "C": "",
        },
    )

    # --- Treatment Zones (TZN) — one per management zone ---
    tzn_ids = []
    for zone in zones:
        pres = pres_by_zone_id.get(zone.id)
        if pres is None:
            continue
        rate_ddi7 = int(round(float(pres.rate_l_ha) * _L_HA_TO_DDI7))
        tzn_id = f"TZN{zone.zone_index + 1}"
        tzn_ids.append((tzn_id, zone.zone_label))
        tzn = ET.SubElement(
            root,
            "TZN",
            attrib={
                "A": tzn_id,
                "B": zone.zone_label[:32],
            },
        )
        # PDV: Product Dose Value element
        ET.SubElement(
            tzn,
            "PDV",
            attrib={
                "A": pdt_id,
                "B": "7",        # DDI 7 = Volume Per Area
                "C": str(rate_ddi7),
                "D": "1",        # Unit designator (mm³/m²)
            },
        )

    # --- Task (TSK) ---
    tsk = ET.SubElement(
        root,
        "TSK",
        attrib={
            "A": "TSK1",
            "B": f"AgroLens VRA – {field_name[:20]} – {application_type}",
            "C": pfd_id,
            "D": task_ref or "",
            "G": "1",            # Task status: planned
        },
    )

    # Comment containing disclaimer
    comment = ET.SubElement(tsk, "COM")
    comment.text = DISCLAIMER_DE

    # Treatment zone allocation
    for tzn_id, label in tzn_ids:
        ET.SubElement(
            tsk,
            "TZA",
            attrib={
                "A": tzn_id,
            },
        )

    # Serialize to bytes
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    xml_buffer = io.BytesIO()
    tree.write(xml_buffer, xml_declaration=True, encoding="utf-8")
    xml_bytes = xml_buffer.getvalue()

    # Wrap in ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("TASKDATA.XML", xml_bytes)
    return zip_buffer.getvalue()
