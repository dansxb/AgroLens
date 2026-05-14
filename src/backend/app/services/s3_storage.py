"""S3 storage helpers for AgroLens raster and export file management.

All uploads use AES256 server-side encryption.  All keys follow the
conventions defined in the development plan:

- Satellite band rasters: ``imagery/{field_id}/{scene_id}/{band}.tif``
- Vegetation index composites: ``indices/{field_id}/{index_type}/{window}.tif``
- Prescription exports: ``exports/{field_id}/{prescription_id}/prescription.{ext}``
"""

from __future__ import annotations

import io
import logging
from typing import Any

import boto3
import numpy as np
import rasterio
from botocore.exceptions import BotoCoreError, ClientError
from rasterio.io import MemoryFile

from app.core.config import settings

logger = logging.getLogger(__name__)


class S3StorageService:
    """Thin class wrapper around the module-level S3 helper functions.

    Instantiate once per request/task and use as a typed dependency.
    All state lives in the module-level boto3 client factory.
    """

    def upload_geotiff(self, key: str, data: "np.ndarray", profile: "dict[str, Any]") -> str:
        return upload_geotiff(key, data, profile)

    def download_geotiff(self, key: str) -> "tuple[np.ndarray, dict[str, Any]]":
        return download_geotiff(key)

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return generate_presigned_url(key, expires_in)


def _get_s3_client() -> Any:
    """Return a configured boto3 S3 client."""
    return boto3.client(
        "s3",
        region_name=settings.aws_s3_region,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    )


def upload_geotiff(
    key: str,
    data: np.ndarray,
    profile: dict[str, Any],
) -> str:
    """Upload a numpy array as a GeoTIFF to S3.

    Args:
        key: S3 object key (e.g. ``imagery/field-uuid/scene-id/B04.tif``).
        data: 2-D float32 or uint8 numpy array to store as a single-band
            GeoTIFF.  Shape: ``(height, width)``.
        profile: rasterio dataset profile dict containing at minimum:
            ``driver``, ``dtype``, ``crs``, ``transform``, ``width``,
            ``height``, ``count``.

    Returns:
        The S3 key of the uploaded object (same as ``key``).

    Raises:
        RuntimeError: If the upload fails.
    """
    # Write array to an in-memory GeoTIFF buffer
    profile = dict(profile)
    profile.update(
        driver="GTiff",
        count=1,
        dtype=str(data.dtype),
    )

    with MemoryFile() as memfile:
        with memfile.open(**profile) as dataset:
            dataset.write(data, 1)
        tiff_bytes = memfile.read()

    s3 = _get_s3_client()
    try:
        s3.put_object(
            Bucket=settings.aws_s3_bucket_name,
            Key=key,
            Body=tiff_bytes,
            ServerSideEncryption="AES256",
            ContentType="image/tiff",
        )
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Failed to upload GeoTIFF to s3://{settings.aws_s3_bucket_name}/{key}: {exc}") from exc

    logger.debug("Uploaded GeoTIFF to s3://%s/%s (%d bytes)", settings.aws_s3_bucket_name, key, len(tiff_bytes))
    return key


def download_geotiff(key: str) -> tuple[np.ndarray, dict[str, Any]]:
    """Download a single-band GeoTIFF from S3 into a numpy array.

    Args:
        key: S3 object key.

    Returns:
        Tuple of ``(data, profile)`` where ``data`` is a 2-D numpy array
        and ``profile`` is the rasterio dataset profile dict.

    Raises:
        RuntimeError: If the download fails or the object does not exist.
    """
    s3 = _get_s3_client()
    try:
        response = s3.get_object(Bucket=settings.aws_s3_bucket_name, Key=key)
        tiff_bytes = response["Body"].read()
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(
            f"Failed to download GeoTIFF from s3://{settings.aws_s3_bucket_name}/{key}: {exc}"
        ) from exc

    with MemoryFile(tiff_bytes) as memfile:
        with memfile.open() as dataset:
            data = dataset.read(1)
            profile = dict(dataset.profile)

    logger.debug(
        "Downloaded GeoTIFF from s3://%s/%s; shape %s",
        settings.aws_s3_bucket_name,
        key,
        data.shape,
    )
    return data, profile


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    """Generate a presigned S3 GET URL for a stored object.

    Args:
        key: S3 object key.
        expires_in: URL expiry in seconds (default: 3600 = 1 hour).

    Returns:
        HTTPS presigned URL string.

    Raises:
        RuntimeError: If URL generation fails.
    """
    s3 = _get_s3_client()
    try:
        url: str = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.aws_s3_bucket_name, "Key": key},
            ExpiresIn=expires_in,
        )
    except (BotoCoreError, ClientError) as exc:
        raise RuntimeError(f"Failed to generate presigned URL for {key}: {exc}") from exc

    return url
