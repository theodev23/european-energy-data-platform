from datetime import UTC, datetime
from unittest.mock import Mock

from european_energy_data_platform.entsoe import EntsoeClient
from european_energy_data_platform.ingestion import (
    extract_actual_generation,
    extract_actual_load,
)


def test_extract_actual_load_returns_raw_payload() -> None:
    client = Mock(spec=EntsoeClient)
    client.fetch_actual_load.return_value = b"<GL_MarketDocument />"

    period_start = datetime(2026, 8, 20, 0, 0, tzinfo=UTC)
    period_end = datetime(2026, 8, 20, 1, 0, tzinfo=UTC)

    payload = extract_actual_load(
        client=client,
        bidding_zone="10YFR-RTE------C",
        period_start=period_start,
        period_end=period_end,
    )

    assert payload.object_name == (
        "entsoe/actual_load/"
        "bidding_zone=10YFR-RTE------C/"
        "year=2026/"
        "month=08/"
        "day=20/"
        "20260820T0000Z_20260820T0100Z.xml"
    )
    assert payload.content == b"<GL_MarketDocument />"

    client.fetch_actual_load.assert_called_once_with(
        bidding_zone="10YFR-RTE------C",
        period_start=period_start,
        period_end=period_end,
    )


def test_extract_actual_generation_returns_raw_payload() -> None:
    client = Mock(spec=EntsoeClient)
    client.fetch_actual_generation.return_value = b"<GL_MarketDocument />"

    period_start = datetime(2026, 8, 20, 0, 0, tzinfo=UTC)
    period_end = datetime(2026, 8, 20, 1, 0, tzinfo=UTC)

    payload = extract_actual_generation(
        client=client,
        bidding_zone="10YFR-RTE------C",
        period_start=period_start,
        period_end=period_end,
    )

    assert payload.object_name == (
        "entsoe/actual_generation/"
        "bidding_zone=10YFR-RTE------C/"
        "year=2026/"
        "month=08/"
        "day=20/"
        "20260820T0000Z_20260820T0100Z.xml"
    )
    assert payload.content == b"<GL_MarketDocument />"

    client.fetch_actual_generation.assert_called_once_with(
        bidding_zone="10YFR-RTE------C",
        period_start=period_start,
        period_end=period_end,
    )
