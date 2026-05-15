"""Unit tests for SentinelHubClient.

All Sentinel Hub API calls are mocked — no real credentials required.
Tests verify correct request construction and error handling.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import patch

import numpy as np
import pytest

from ml.sentinel.client import SentinelHubClient, SentinelHubError


@pytest.fixture()
def client() -> SentinelHubClient:
    return SentinelHubClient(
        client_id="test-client-id",
        client_secret="test-client-secret",
        instance_id="test-instance-id",
    )


class TestSearchScenes:
    def test_returns_scene_list(self, client: SentinelHubClient) -> None:
        fake_scenes = [
            {
                "id": "S2A_scene_1",
                "properties": {
                    "datetime": "2024-05-01T10:00:00Z",
                    "eo:cloud_cover": 5.0,
                },
            },
            {
                "id": "S2A_scene_2",
                "properties": {
                    "datetime": "2024-05-06T10:05:00Z",
                    "eo:cloud_cover": 12.0,
                },
            },
        ]

        with patch("ml.sentinel.client.SentinelHubCatalog") as MockCatalog:
            mock_catalog_instance = MockCatalog.return_value
            mock_catalog_instance.search.return_value = iter(fake_scenes)

            result = client.search_scenes(
                bbox=[13.4, 52.5, 13.5, 52.6],
                date_from=date(2024, 5, 1),
                date_to=date(2024, 5, 10),
                max_cloud_cover=80.0,
            )

        assert result == fake_scenes
        assert len(result) == 2

    def test_passes_cloud_filter(self, client: SentinelHubClient) -> None:
        with patch("ml.sentinel.client.SentinelHubCatalog") as MockCatalog:
            mock_catalog_instance = MockCatalog.return_value
            mock_catalog_instance.search.return_value = iter([])

            client.search_scenes(
                bbox=[13.4, 52.5, 13.5, 52.6],
                date_from=date(2024, 5, 1),
                date_to=date(2024, 5, 10),
                max_cloud_cover=30.0,
            )

            _, kwargs = mock_catalog_instance.search.call_args
            assert "30" in kwargs.get("filter", "")

    def test_raises_on_api_error(self, client: SentinelHubClient) -> None:
        with patch("ml.sentinel.client.SentinelHubCatalog") as MockCatalog:
            mock_catalog_instance = MockCatalog.return_value
            mock_catalog_instance.search.side_effect = RuntimeError(
                "Connection refused"
            )

            with pytest.raises(SentinelHubError, match="Scene search failed"):
                client.search_scenes(
                    bbox=[13.4, 52.5, 13.5, 52.6],
                    date_from=date(2024, 5, 1),
                    date_to=date(2024, 5, 10),
                )


class TestDownloadBands:
    def _make_band_data(self, bands: list[str], h: int = 100, w: int = 100) -> dict:
        """Build a fake get_data() response dict."""
        return {b: np.random.rand(h, w, 1).astype(np.float32) for b in bands}

    def test_returns_correct_band_shapes(self, client: SentinelHubClient) -> None:
        bands = ["B04", "B08"]
        fake_data = self._make_band_data(bands)

        with patch("ml.sentinel.client.SentinelHubRequest") as MockRequest:
            mock_req_instance = MockRequest.return_value
            mock_req_instance.get_data.return_value = [fake_data]

            with patch(
                "ml.sentinel.client.bbox_to_dimensions", return_value=(100, 100)
            ):
                result = client.download_bands(
                    scene_datetime="2024-05-01T10:00:00Z",
                    bbox=[13.4, 52.5, 13.5, 52.6],
                    bands=bands,
                )

        assert set(result.keys()) == {"B04", "B08"}
        assert result["B04"].shape == (100, 100)
        assert result["B08"].shape == (100, 100)

    def test_squeezes_channel_dimension(self, client: SentinelHubClient) -> None:
        bands = ["B04"]
        fake_data = {"B04": np.ones((50, 60, 1), dtype=np.float32)}

        with patch("ml.sentinel.client.SentinelHubRequest") as MockRequest:
            mock_req_instance = MockRequest.return_value
            mock_req_instance.get_data.return_value = [fake_data]

            with patch("ml.sentinel.client.bbox_to_dimensions", return_value=(50, 60)):
                result = client.download_bands(
                    scene_datetime="2024-05-01T10:00:00Z",
                    bbox=[13.4, 52.5, 13.5, 52.6],
                    bands=bands,
                )

        assert result["B04"].shape == (50, 60)

    def test_raises_on_download_error(self, client: SentinelHubClient) -> None:
        with patch("ml.sentinel.client.SentinelHubRequest") as MockRequest:
            mock_req_instance = MockRequest.return_value
            mock_req_instance.get_data.side_effect = RuntimeError("Timeout")

            with patch(
                "ml.sentinel.client.bbox_to_dimensions", return_value=(100, 100)
            ):
                with pytest.raises(SentinelHubError, match="Band download failed"):
                    client.download_bands(
                        scene_datetime="2024-05-01T10:00:00Z",
                        bbox=[13.4, 52.5, 13.5, 52.6],
                        bands=["B04", "B08"],
                    )

    def test_raises_when_band_missing_from_response(
        self, client: SentinelHubClient
    ) -> None:
        bands = ["B04", "B08"]
        # Only B04 in the response, B08 missing
        fake_data = {"B04": np.ones((10, 10, 1), dtype=np.float32)}

        with patch("ml.sentinel.client.SentinelHubRequest") as MockRequest:
            mock_req_instance = MockRequest.return_value
            mock_req_instance.get_data.return_value = [fake_data]

            with patch("ml.sentinel.client.bbox_to_dimensions", return_value=(10, 10)):
                with pytest.raises(
                    SentinelHubError, match="missing from downloaded data"
                ):
                    client.download_bands(
                        scene_datetime="2024-05-01T10:00:00Z",
                        bbox=[13.4, 52.5, 13.5, 52.6],
                        bands=bands,
                    )
