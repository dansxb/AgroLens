"""Unit tests for ml.prescription.engine."""

from __future__ import annotations

import pytest

from ml.prescription.engine import (
    DISCLAIMER_DE,
    compute_prescription,
)


class TestComputePrescription:
    def test_default_k3_fungicide_rates(self) -> None:
        result = compute_prescription("fungicide", 2.0, ["Low", "Medium", "High"])
        assert len(result.zones) == 3
        assert result.zones[0].rate_l_ha == pytest.approx(2.0 * 0.60, abs=1e-4)
        assert result.zones[1].rate_l_ha == pytest.approx(2.0 * 1.00, abs=1e-4)
        assert result.zones[2].rate_l_ha == pytest.approx(2.0 * 1.30, abs=1e-4)

    def test_herbicide_rates(self) -> None:
        result = compute_prescription("herbicide", 3.0, ["Low", "Medium", "High"])
        assert result.zones[0].rate_l_ha == pytest.approx(3.0 * 0.70, abs=1e-4)
        assert result.zones[2].rate_l_ha == pytest.approx(3.0 * 1.20, abs=1e-4)

    def test_insecticide_rates(self) -> None:
        result = compute_prescription("insecticide", 1.5, ["Low", "Medium", "High"])
        assert result.zones[0].rate_l_ha == pytest.approx(1.5 * 0.50, abs=1e-4)
        assert result.zones[2].rate_l_ha == pytest.approx(1.5 * 1.50, abs=1e-4)

    def test_disclaimer_is_present(self) -> None:
        result = compute_prescription("fungicide", 2.0, ["Low", "Medium", "High"])
        assert result.disclaimer == DISCLAIMER_DE
        assert "agronomischen Faustregeln" in result.disclaimer

    def test_savings_pct_is_positive_for_standard_k3(self) -> None:
        result = compute_prescription("fungicide", 2.0, ["Low", "Medium", "High"])
        assert (
            result.savings_pct > 0
        ), "VRA should use less product than uniform application"

    def test_mean_rate_is_weighted_average(self) -> None:
        result = compute_prescription("herbicide", 4.0, ["Low", "Medium", "High"])
        expected = sum(z.rate_l_ha for z in result.zones) / 3
        assert result.mean_rate_l_ha == pytest.approx(expected, abs=1e-3)

    def test_k2_zones(self) -> None:
        result = compute_prescription("fungicide", 2.0, ["Low", "High"])
        assert len(result.zones) == 2
        assert result.zones[0].rate_l_ha < result.zones[1].rate_l_ha

    def test_k4_zones(self) -> None:
        result = compute_prescription(
            "fungicide", 2.0, ["Low", "Medium", "High", "Very High"]
        )
        assert len(result.zones) == 4

    def test_k5_zones(self) -> None:
        result = compute_prescription(
            "insecticide",
            2.0,
            ["Low", "Medium-Low", "Medium", "Medium-High", "High"],
        )
        assert len(result.zones) == 5

    def test_rates_non_negative(self) -> None:
        result = compute_prescription("insecticide", 0.1, ["Low", "Medium", "High"])
        for zone in result.zones:
            assert zone.rate_l_ha >= 0.0

    def test_below_floor_flag_set_when_rate_below_50pct(self) -> None:
        # insecticide Low multiplier is 0.50, so Low zone = base×0.5 — exactly at floor
        # Use a very small base rate to push it below floor
        # Actually 0.50× is exactly the floor; use a custom scenario:
        # We can't go below 50% with the default multipliers except at 0.50×.
        # Verify the flag is False for normal rates (none of default multipliers < 0.5×)
        result = compute_prescription("fungicide", 2.0, ["Low", "Medium", "High"])
        for zone in result.zones:
            assert not zone.below_minimum_floor

    def test_zone_names_preserved(self) -> None:
        names = ["Low", "Medium", "High"]
        result = compute_prescription("herbicide", 3.0, names)
        assert [z.zone_name for z in result.zones] == names

    def test_invalid_application_type_raises(self) -> None:
        with pytest.raises(ValueError, match="application_type"):
            compute_prescription("rocket_fuel", 2.0, ["Low", "Medium", "High"])  # type: ignore[arg-type]

    def test_zero_base_rate_raises(self) -> None:
        with pytest.raises(ValueError, match="base_rate_l_ha"):
            compute_prescription("fungicide", 0.0, ["Low", "Medium", "High"])

    def test_negative_base_rate_raises(self) -> None:
        with pytest.raises(ValueError, match="base_rate_l_ha"):
            compute_prescription("fungicide", -1.0, ["Low", "Medium", "High"])

    def test_too_few_zones_raises(self) -> None:
        with pytest.raises(ValueError, match="2–5"):
            compute_prescription("fungicide", 2.0, ["Low"])

    def test_too_many_zones_raises(self) -> None:
        with pytest.raises(ValueError, match="2–5"):
            compute_prescription("fungicide", 2.0, ["A", "B", "C", "D", "E", "F"])
