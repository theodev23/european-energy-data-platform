from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from european_energy_data_platform.bigquery_raw import BigQueryRawLoader
from european_energy_data_platform.entsoe import EntsoeClient
from european_energy_data_platform.gcs import GcsRawStorage
from european_energy_data_platform.pipeline import (
    ingest_actual_generation,
    ingest_actual_load,
    ingest_day_ahead_prices,
)


@pytest.fixture
def period() -> tuple[datetime, datetime]:
    return (
        datetime(2026, 8, 20, 0, 0, tzinfo=UTC),
        datetime(2026, 8, 20, 1, 0, tzinfo=UTC),
    )


@pytest.mark.parametrize(
    ("function", "client_method", "loader_method", "fixture_name", "dataset"),
    [
        (
            ingest_actual_load,
            "fetch_actual_load",
            "load_actual_load",
            "actual_load.xml",
            "actual_load",
        ),
        (
            ingest_actual_generation,
            "fetch_actual_generation",
            "load_actual_generation",
            "actual_generation.xml",
            "actual_generation",
        ),
        (
            ingest_day_ahead_prices,
            "fetch_day_ahead_prices",
            "load_day_ahead_prices",
            "day_ahead_prices.xml",
            "day_ahead_prices",
        ),
    ],
)
def test_ingestion_pipeline_composes_existing_components(
    function,
    client_method: str,
    loader_method: str,
    fixture_name: str,
    dataset: str,
    period: tuple[datetime, datetime],
) -> None:
    client = Mock(spec=EntsoeClient)
    storage = Mock(spec=GcsRawStorage)
    loader = Mock(spec=BigQueryRawLoader)

    xml = (Path(__file__).parent / "fixtures" / fixture_name).read_bytes()

    getattr(client, client_method).return_value = xml
    storage.store.return_value = True

    period_start, period_end = period

    result = function(
        client=client,
        storage=storage,
        loader=loader,
        bidding_zone="10YFR-RTE------C",
        period_start=period_start,
        period_end=period_end,
    )

    getattr(client, client_method).assert_called_once_with(
        bidding_zone="10YFR-RTE------C",
        period_start=period_start,
        period_end=period_end,
    )
    storage.store.assert_called_once()
    getattr(loader, loader_method).assert_called_once()

    loaded_rows = getattr(loader, loader_method).call_args.args[0]

    assert result.dataset == dataset
    assert result.bidding_zone == "10YFR-RTE------C"
    assert result.source_object_name.startswith(f"entsoe/{dataset}/")
    assert result.stored_in_gcs is True
    assert result.row_count == len(loaded_rows)
    assert result.row_count > 0
