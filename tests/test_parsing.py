from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from european_energy_data_platform.ingestion import RawPayload
from european_energy_data_platform.parsing import parse_actual_load


def test_parse_actual_load_preserves_source_metadata_and_point_positions() -> None:
    payload = RawPayload(
        object_name=(
            "entsoe/actual_load/"
            "bidding_zone=10YFR-RTE------C/"
            "year=2026/month=08/day=20/"
            "20260820T0000Z_20260820T0100Z.xml"
        ),
        content=Path("tests/fixtures/actual_load.xml").read_bytes(),
    )

    rows = parse_actual_load(payload)

    assert len(rows) == 2

    first = rows[0]

    assert first.source_object_name == payload.object_name
    assert first.document_mrid == "document-load-1"
    assert first.document_type == "A65"
    assert first.revision_number == 1
    assert first.document_created_at == datetime(
        2026,
        8,
        22,
        8,
        27,
        52,
        tzinfo=UTC,
    )
    assert first.process_type == "A16"

    assert first.time_series_mrid == "series-load-1"
    assert first.business_type == "A04"
    assert first.object_aggregation == "A01"
    assert first.out_bidding_zone == "10YFR-RTE------C"
    assert first.quantity_unit == "MAW"
    assert first.curve_type == "A03"

    assert first.period_start == datetime(2026, 8, 20, 0, 0, tzinfo=UTC)
    assert first.period_end == datetime(2026, 8, 20, 1, 0, tzinfo=UTC)
    assert first.resolution == "PT15M"
    assert first.position == 1
    assert first.point_timestamp == datetime(2026, 8, 20, 0, 0, tzinfo=UTC)
    assert first.quantity == Decimal("38821.26")

    third_position = rows[1]

    assert third_position.position == 3
    assert third_position.point_timestamp == datetime(
        2026,
        8,
        20,
        0,
        30,
        tzinfo=UTC,
    )
    assert third_position.quantity == Decimal("39000.50")
