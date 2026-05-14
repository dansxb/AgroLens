"""Prescription rate engine for variable-rate pesticide application.

Applies agronomist-validated multiplier rules to a base application rate,
producing per-zone prescription rates for a given application type.

## Multiplier table

| Application Type | Low   | Medium-Low | Medium | Medium-High | Very High |
|-----------------|-------|------------|--------|-------------|-----------|
| fungicide       | 0.60× | 1.00×      | 1.30×  | 1.50×       | 1.70×     |
| herbicide       | 0.70× | 1.00×      | 1.20×  | 1.40×       | 1.60×     |
| insecticide     | 0.50× | 1.00×      | 1.50×  | 1.80×       | 2.00×     |

Multipliers are based on crop-science literature reviewed by agronomists.
They are **not** trained from machine-learning data.

## Disclaimer (legally required for EU regulatory compliance)

All prescription outputs produced by this engine carry the following notice:

    "Die Applikationsmengen basieren auf agronomischen Faustregeln und wurden
    nicht für jeden Kulturtyp und jede Region validiert.  Bitte prüfen Sie die
    Empfehlungen mit einem zugelassenen Pflanzenschutzberater, bevor Sie die
    Applikation vornehmen."

This notice must appear in every PDF report, Shapefile attribute table, and
TASKDATA.XML document exported to farmers.

## Minimum rate guard

A prescription rate is never negative.  When the computed rate would be below
50% of the base rate, a warning is logged because this may conflict with the
minimum application rate stated in the pesticide product registration.  The
rate is still applied as computed — the farmer's agronomist must verify
compliance with the specific product registration.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)

ApplicationType = Literal["fungicide", "herbicide", "insecticide"]

# Ordered zone labels → multiplier index mapping
# Zones are ordered Low→High as produced by delineation.py
_MULTIPLIERS: dict[ApplicationType, list[float]] = {
    "fungicide": [0.60, 1.00, 1.30, 1.50, 1.70],
    "herbicide": [0.70, 1.00, 1.20, 1.40, 1.60],
    "insecticide": [0.50, 1.00, 1.50, 1.80, 2.00],
}

DISCLAIMER_DE = (
    "Die Applikationsmengen basieren auf agronomischen Faustregeln und wurden "
    "nicht für jeden Kulturtyp und jede Region validiert. "
    "Bitte prüfen Sie die Empfehlungen mit einem zugelassenen Pflanzenschutzberater, "
    "bevor Sie die Applikation vornehmen."
)


@dataclass(frozen=True)
class ZonePrescription:
    """Prescription rate for a single management zone.

    Attributes:
        zone_index: 0-based zone index (0 = lowest NDVI / least vigorous).
        zone_name: Human-readable zone label (e.g. "Low", "Medium", "High").
        multiplier: Rate multiplier applied to base_rate_l_ha.
        rate_l_ha: Computed application rate in litres per hectare.
        below_minimum_floor: True when the rate is below 50% of base rate,
            indicating possible conflict with pesticide registration minimums.
    """

    zone_index: int
    zone_name: str
    multiplier: float
    rate_l_ha: float
    below_minimum_floor: bool


@dataclass(frozen=True)
class PrescriptionResult:
    """Full prescription result for a field and application type.

    Attributes:
        application_type: One of "fungicide", "herbicide", "insecticide".
        base_rate_l_ha: Farmer-supplied base application rate in L/ha.
        zones: Ordered list of :class:`ZonePrescription` (Low → High).
        disclaimer: Mandatory agronomist disclaimer text (German).
        mean_rate_l_ha: Field-averaged rate (unweighted mean across zones,
            useful for calculating total product consumption estimate).
        savings_pct: Estimated product savings vs. uniform application
            at base_rate_l_ha, expressed as a percentage.
    """

    application_type: ApplicationType
    base_rate_l_ha: float
    zones: list[ZonePrescription]
    disclaimer: str
    mean_rate_l_ha: float
    savings_pct: float


def compute_prescription(
    application_type: ApplicationType,
    base_rate_l_ha: float,
    zone_names: list[str],
) -> PrescriptionResult:
    """Compute per-zone prescription rates for the given application type.

    Args:
        application_type: Type of pesticide application.
        base_rate_l_ha: Farmer's standard application rate in litres per hectare.
            Must be > 0.
        zone_names: Ordered list of zone names from
            :func:`~ml.zones.delineation.delineate_zones` (length 2–5,
            ordered Low → High).

    Returns:
        :class:`PrescriptionResult` with per-zone rates, disclaimer, and savings.

    Raises:
        ValueError: If ``base_rate_l_ha`` ≤ 0.
        ValueError: If ``application_type`` is not recognised.
        ValueError: If ``zone_names`` length is outside [2, 5].
    """
    if base_rate_l_ha <= 0:
        raise ValueError(f"base_rate_l_ha must be positive, got {base_rate_l_ha}")
    if application_type not in _MULTIPLIERS:
        raise ValueError(
            f"Unknown application_type '{application_type}'. "
            f"Must be one of: {list(_MULTIPLIERS.keys())}"
        )
    n_zones = len(zone_names)
    if not (2 <= n_zones <= 5):
        raise ValueError(f"zone_names must have 2–5 entries, got {n_zones}")

    multiplier_row = _MULTIPLIERS[application_type]
    # Use the first n_zones entries so fewer zones always map to lower-intensity tiers.
    selected_multipliers = multiplier_row[:n_zones]

    floor = base_rate_l_ha * 0.5
    zones: list[ZonePrescription] = []
    for idx, (name, multiplier) in enumerate(zip(zone_names, selected_multipliers)):
        rate = max(0.0, round(base_rate_l_ha * multiplier, 4))
        below_floor = rate < floor
        if below_floor:
            logger.warning(
                "Zone '%s' rate %.3f L/ha is below 50%% of base rate %.3f L/ha — "
                "verify against pesticide registration minimum.",
                name,
                rate,
                base_rate_l_ha,
            )
        zones.append(
            ZonePrescription(
                zone_index=idx,
                zone_name=name,
                multiplier=multiplier,
                rate_l_ha=rate,
                below_minimum_floor=below_floor,
            )
        )

    mean_rate = sum(z.rate_l_ha for z in zones) / n_zones
    savings_pct = round((1.0 - mean_rate / base_rate_l_ha) * 100.0, 2)

    return PrescriptionResult(
        application_type=application_type,
        base_rate_l_ha=base_rate_l_ha,
        zones=zones,
        disclaimer=DISCLAIMER_DE,
        mean_rate_l_ha=round(mean_rate, 4),
        savings_pct=savings_pct,
    )
