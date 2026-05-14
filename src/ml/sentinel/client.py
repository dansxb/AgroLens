"""Sentinel Hub API client for AgroLens.

Provides OAuth2-authenticated access to the Sentinel Hub API for
scene search and Sentinel-2 L2A band raster download.  Uses the
official ``sentinelhub`` Python SDK (v3.10+).
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

import numpy as np
from sentinelhub import (
    BBox,
    CRS,
    DataCollection,
    MimeType,
    MosaickingOrder,
    SHConfig,
    SentinelHubCatalog,
    SentinelHubRequest,
    bbox_to_dimensions,
)

logger = logging.getLogger(__name__)


class SentinelHubError(Exception):
    """Raised when the Sentinel Hub API returns an error or download fails."""


class SentinelHubClient:
    """Thin, stateless wrapper around the sentinelhub SDK.

    Each instance shares a single :class:`SHConfig` for OAuth2 credentials.
    No token caching is needed — the SDK handles token refresh internally.

    Args:
        client_id: Sentinel Hub OAuth2 client ID.
        client_secret: Sentinel Hub OAuth2 client secret.
        instance_id: Sentinel Hub configuration/instance ID.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        instance_id: str,
    ) -> None:
        self._config = SHConfig()
        self._config.sh_client_id = client_id
        self._config.sh_client_secret = client_secret
        self._config.instance_id = instance_id

    def search_scenes(
        self,
        bbox: list[float],
        date_from: date,
        date_to: date,
        max_cloud_cover: float = 80.0,
    ) -> list[dict[str, Any]]:
        """Search for available Sentinel-2 L2A scenes within a bounding box.

        Args:
            bbox: ``[min_lon, min_lat, max_lon, max_lat]`` in EPSG:4326.
            date_from: Start date of the search window (inclusive).
            date_to: End date of the search window (inclusive).
            max_cloud_cover: Maximum cloud cover percentage (0–100).

        Returns:
            List of scene metadata dicts from the STAC catalog.  Each dict
            contains at least ``id``, ``properties.datetime``, and
            ``properties.eo:cloud_cover``.

        Raises:
            SentinelHubError: If the catalog API request fails.
        """
        sh_bbox = BBox(bbox=bbox, crs=CRS.WGS84)
        catalog = SentinelHubCatalog(config=self._config)

        try:
            results: list[dict[str, Any]] = list(
                catalog.search(
                    DataCollection.SENTINEL2_L2A,
                    bbox=sh_bbox,
                    time=(date_from.isoformat(), date_to.isoformat()),
                    filter=f"eo:cloud_cover < {max_cloud_cover}",
                    fields={
                        "include": [
                            "id",
                            "properties.datetime",
                            "properties.eo:cloud_cover",
                        ],
                        "exclude": [],
                    },
                )
            )
        except Exception as exc:
            raise SentinelHubError(
                f"Scene search failed for bbox={bbox} "
                f"({date_from}–{date_to}): {exc}"
            ) from exc

        logger.info(
            "Found %d scenes between %s and %s (cloud_cover < %.0f%%)",
            len(results),
            date_from,
            date_to,
            max_cloud_cover,
        )
        return results

    def download_bands(
        self,
        scene_datetime: str,
        bbox: list[float],
        bands: list[str],
        resolution: int = 10,
    ) -> dict[str, np.ndarray]:
        """Download specific Sentinel-2 L2A bands for a scene.

        Args:
            scene_datetime: ISO 8601 acquisition datetime string from the
                catalog search result (``properties.datetime``).  Used as
                both the start and end of the time interval to select exactly
                one scene.
            bbox: ``[min_lon, min_lat, max_lon, max_lat]`` in EPSG:4326.
            bands: Band names to download, e.g. ``["B04", "B08", "SCL"]``.
                Reflectance bands are returned as float32 (0–1 scale).
                ``SCL`` is returned as uint8.
            resolution: Pixel resolution in metres (10 or 20).

        Returns:
            Dict mapping each band name to a 2-D numpy array of shape
            ``(height, width)``.

        Raises:
            SentinelHubError: If the download request fails or a requested
                band is absent from the response.
        """
        sh_bbox = BBox(bbox=bbox, crs=CRS.WGS84)
        size = bbox_to_dimensions(sh_bbox, resolution=resolution)

        reflectance_bands = [b for b in bands if b != "SCL"]

        # Build a multi-output evalscript that returns each band separately
        # so Sentinel Hub delivers them as individual TIFF responses.
        outputs_js = "\n".join(
            f'      {{id: "{b}", bands: 1, sampleType: "FLOAT32"}},'
            for b in reflectance_bands
        )
        if "SCL" in bands:
            outputs_js += '\n      {id: "SCL", bands: 1, sampleType: "UINT8"},'

        returns_js = "\n".join(f"    {b}: [sample.{b}]," for b in bands)
        bands_js = str(bands).replace("'", '"')

        evalscript = (
            "//VERSION=3\n"
            "function setup() {\n"
            "  return {\n"
            f"    input: [{{bands: {bands_js}, units: 'REFLECTANCE'}}],\n"
            "    output: [\n"
            f"{outputs_js}\n"
            "    ]\n"
            "  };\n"
            "}\n"
            "function evaluatePixel(sample) {\n"
            "  return {\n"
            f"{returns_js}\n"
            "  };\n"
            "}"
        )

        try:
            request = SentinelHubRequest(
                evalscript=evalscript,
                input_data=[
                    SentinelHubRequest.input_data(
                        data_collection=DataCollection.SENTINEL2_L2A,
                        time_interval=(scene_datetime, scene_datetime),
                        mosaicking_order=MosaickingOrder.LEAST_CC,
                        maxcc=1.0,
                    )
                ],
                responses=[
                    SentinelHubRequest.output_response(b, MimeType.TIFF)
                    for b in bands
                ],
                bbox=sh_bbox,
                size=size,
                config=self._config,
            )
            # get_data() returns a list with one dict per time slot
            data: dict[str, np.ndarray] = request.get_data()[0]
        except Exception as exc:
            raise SentinelHubError(
                f"Band download failed for scene {scene_datetime}: {exc}"
            ) from exc

        result: dict[str, np.ndarray] = {}
        for b in bands:
            arr = data.get(b)
            if arr is None:
                raise SentinelHubError(
                    f"Band {b!r} missing from downloaded data for scene {scene_datetime}."
                )
            # Squeeze the trailing channel dimension: (H, W, 1) → (H, W)
            result[b] = arr.squeeze(axis=-1)

        shape = next(iter(result.values())).shape
        logger.info(
            "Downloaded bands %s for scene %s; array shape %s",
            bands,
            scene_datetime,
            shape,
        )
        return result
