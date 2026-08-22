from unittest.mock import Mock

import pytest
from google.api_core.exceptions import PreconditionFailed
from google.cloud import storage

from european_energy_data_platform.gcs import GcsRawStorage
from european_energy_data_platform.ingestion import RawPayload


def test_gcs_raw_storage_rejects_empty_bucket_name() -> None:
    client = Mock(spec=storage.Client)

    with pytest.raises(ValueError, match="GCS bucket name must not be empty"):
        GcsRawStorage(
            bucket_name="   ",
            client=client,
        )


def test_gcs_raw_storage_uploads_raw_payload_without_overwrite() -> None:
    client = Mock(spec=storage.Client)
    bucket = Mock()
    blob = Mock()

    client.bucket.return_value = bucket
    bucket.blob.return_value = blob

    raw_storage = GcsRawStorage(
        bucket_name="energy-platform-raw",
        client=client,
    )

    payload = RawPayload(
        object_name=(
            "entsoe/actual_load/"
            "bidding_zone=10YFR-RTE------C/"
            "year=2026/month=08/day=20/"
            "20260820T0000Z_20260820T0100Z.xml"
        ),
        content=b"<GL_MarketDocument />",
    )

    created = raw_storage.store(payload)

    assert created is True
    client.bucket.assert_called_once_with("energy-platform-raw")
    bucket.blob.assert_called_once_with(payload.object_name)
    blob.upload_from_string.assert_called_once_with(
        payload.content,
        content_type="application/xml",
        if_generation_match=0,
    )


def test_gcs_raw_storage_treats_existing_object_as_idempotent() -> None:
    client = Mock(spec=storage.Client)
    bucket = Mock()
    blob = Mock()

    client.bucket.return_value = bucket
    bucket.blob.return_value = blob
    blob.upload_from_string.side_effect = PreconditionFailed("Object already exists")

    raw_storage = GcsRawStorage(
        bucket_name="energy-platform-raw",
        client=client,
    )

    payload = RawPayload(
        object_name="entsoe/day_ahead_prices/example.xml",
        content=b"<Publication_MarketDocument />",
    )

    created = raw_storage.store(payload)

    assert created is False
    blob.upload_from_string.assert_called_once_with(
        payload.content,
        content_type="application/xml",
        if_generation_match=0,
    )


def test_gcs_raw_storage_can_use_default_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    client = Mock(spec=storage.Client)
    bucket = Mock()

    client.bucket.return_value = bucket

    client_factory = Mock(return_value=client)
    monkeypatch.setattr(
        "european_energy_data_platform.gcs.storage.Client",
        client_factory,
    )

    raw_storage = GcsRawStorage.from_default_credentials(
        bucket_name="energy-platform-raw",
    )

    assert isinstance(raw_storage, GcsRawStorage)
    client_factory.assert_called_once_with()
    client.bucket.assert_called_once_with("energy-platform-raw")
