"""Shapefile export for VRA prescription maps.

Generates an ESRI Shapefile (ZIP archive containing .shp/.shx/.dbf/.prj)
from a list of management zones and their prescription rates.

The attribute table includes:
  - zone_index, zone_label, rate_l_ha, multiplier, below_floor, area_ha
  - flik (FLIK-Nummer from the parent Field, if set)
  - disclaimer (agronomist advisory text)

Note: Shapefiles cannot be directly loaded by ISOBUS tractor terminals.
For machine-compatible export use :mod:`app.services.export.taskdata_xml`
which produces ISO 11783-10 TASKDATA.XML format.
"""

from __future__ import annotations

import io
import logging
import os
import tempfile
import zipfile
from typing import Optional

from app.models.management_zone import ManagementZone
from app.models.prescription import Prescription

from ml.prescription.engine import DISCLAIMER_DE

logger = logging.getLogger(__name__)


def build_prescription_shapefile(
    zones: list[ManagementZone],
    prescriptions: list[Prescription],
    field_name: str,
    flik: Optional[str] = None,
) -> bytes:
    """Build a zipped Shapefile from prescription zones.

    Args:
        zones: List of :class:`ManagementZone` ORM objects ordered by
            zone_index ascending.  Each zone must have a ``geometry``
            attribute (WKBElement in EPSG:4326).
        prescriptions: List of :class:`Prescription` ORM objects, one per
            zone, with matching ``management_zone_id``.
        field_name: Human-readable field name for the ZIP filename.
        flik: FLIK-Nummer of the field (optional).

    Returns:
        Bytes of a ZIP archive containing the Shapefile components.

    Raises:
        ImportError: If geopandas or fiona are not installed.
        ValueError: If zones and prescriptions have mismatched counts.
    """
    try:
        import geopandas as gpd  # type: ignore[import]
        import shapely.wkb  # type: ignore[import]
        from shapely.geometry import MultiPolygon, Polygon  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "geopandas and shapely are required for Shapefile export."
        ) from exc

    if len(zones) != len(prescriptions):
        raise ValueError(
            f"zones ({len(zones)}) and prescriptions ({len(prescriptions)}) must be same length."
        )

    pres_by_zone_id = {p.management_zone_id: p for p in prescriptions}

    records = []
    geometries = []
    for zone in zones:
        pres = pres_by_zone_id.get(zone.id)
        if pres is None:
            logger.warning("No prescription found for zone %s — skipping.", zone.id)
            continue

        geom = None
        if zone.geometry is not None:
            try:
                geom = shapely.wkb.loads(bytes(zone.geometry.data), hex=False)
            except Exception:
                logger.warning("Could not parse geometry for zone %s.", zone.id)

        geometries.append(geom)
        records.append(
            {
                "zone_idx": zone.zone_index,
                "zone_lbl": zone.zone_label[:10],  # DBF field length limit
                "rate_l_ha": float(pres.rate_l_ha),
                "multiplier": float(pres.multiplier),
                "blw_floor": int(pres.below_minimum_floor),
                "area_ha": float(zone.area_ha) if zone.area_ha else None,
                "flik": (flik or "")[:18],
                "disclaimer": DISCLAIMER_DE[:254],  # DBF max string length
            }
        )

    gdf = gpd.GeoDataFrame(records, geometry=geometries, crs="EPSG:4326")

    with tempfile.TemporaryDirectory() as tmpdir:
        shp_base = os.path.join(tmpdir, "prescription")
        gdf.to_file(shp_base + ".shp", driver="ESRI Shapefile")

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for ext in (".shp", ".shx", ".dbf", ".prj", ".cpg"):
                path = shp_base + ext
                if os.path.exists(path):
                    zf.write(path, arcname=f"prescription{ext}")

    return zip_buffer.getvalue()
