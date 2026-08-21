from google.api_core.exceptions import PreconditionFailed
from google.cloud import storage

from european_energy_data_platform.ingestion import RawPayload


class GcsRawStorage:
    """Persist immutable raw payloads in Google Cloud Storage."""

    def __init__(
        self,
        bucket_name: str,
        client: storage.Client,
    ) -> None:
        bucket_name = bucket_name.strip()

        if not bucket_name:
            raise ValueError("GCS bucket name must not be empty")

        self._bucket = client.bucket(bucket_name)

    def store(self, payload: RawPayload) -> bool:
        """Create a RAW object unless the deterministic object already exists."""
        blob = self._bucket.blob(payload.object_name)

        try:
            blob.upload_from_string(
                payload.content,
                content_type="application/xml",
                if_generation_match=0,
            )
        except PreconditionFailed:
            return False

        return True
