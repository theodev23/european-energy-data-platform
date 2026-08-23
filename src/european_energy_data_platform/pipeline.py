from dataclasses import dataclass
from datetime import datetime

from european_energy_data_platform.bigquery_raw import BigQueryRawLoader
from european_energy_data_platform.entsoe import EntsoeClient
from european_energy_data_platform.gcs import GcsRawStorage
from european_energy_data_platform.ingestion import (
    extract_actual_generation,
    extract_actual_load,
    extract_day_ahead_prices,
)
from european_energy_data_platform.parsing import (
    parse_actual_generation,
    parse_actual_load,
    parse_day_ahead_prices,
)


@dataclass(frozen=True, slots=True)
class IngestionResult:
    """Lightweight metadata returned by one RAW ingestion operation."""

    dataset: str
    bidding_zone: str
    source_object_name: str
    stored_in_gcs: bool
    row_count: int


def ingest_actual_load(
    *,
    client: EntsoeClient,
    storage: GcsRawStorage,
    loader: BigQueryRawLoader,
    bidding_zone: str,
    period_start: datetime,
    period_end: datetime,
) -> IngestionResult:
    payload = extract_actual_load(
        client=client,
        bidding_zone=bidding_zone,
        period_start=period_start,
        period_end=period_end,
    )
    stored_in_gcs = storage.store(payload)
    rows = parse_actual_load(payload)
    loader.load_actual_load(rows)

    return IngestionResult(
        dataset="actual_load",
        bidding_zone=bidding_zone,
        source_object_name=payload.object_name,
        stored_in_gcs=stored_in_gcs,
        row_count=len(rows),
    )


def ingest_actual_generation(
    *,
    client: EntsoeClient,
    storage: GcsRawStorage,
    loader: BigQueryRawLoader,
    bidding_zone: str,
    period_start: datetime,
    period_end: datetime,
) -> IngestionResult:
    payload = extract_actual_generation(
        client=client,
        bidding_zone=bidding_zone,
        period_start=period_start,
        period_end=period_end,
    )
    stored_in_gcs = storage.store(payload)
    rows = parse_actual_generation(payload)
    loader.load_actual_generation(rows)

    return IngestionResult(
        dataset="actual_generation",
        bidding_zone=bidding_zone,
        source_object_name=payload.object_name,
        stored_in_gcs=stored_in_gcs,
        row_count=len(rows),
    )


def ingest_day_ahead_prices(
    *,
    client: EntsoeClient,
    storage: GcsRawStorage,
    loader: BigQueryRawLoader,
    bidding_zone: str,
    period_start: datetime,
    period_end: datetime,
) -> IngestionResult:
    payload = extract_day_ahead_prices(
        client=client,
        bidding_zone=bidding_zone,
        period_start=period_start,
        period_end=period_end,
    )
    stored_in_gcs = storage.store(payload)
    rows = parse_day_ahead_prices(payload)
    loader.load_day_ahead_prices(rows)

    return IngestionResult(
        dataset="day_ahead_prices",
        bidding_zone=bidding_zone,
        source_object_name=payload.object_name,
        stored_in_gcs=stored_in_gcs,
        row_count=len(rows),
    )
