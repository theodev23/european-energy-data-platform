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


def test_parse_actual_generation_preserves_direction_and_psr_type() -> None:
    from european_energy_data_platform.parsing import parse_actual_generation

    payload = RawPayload(
        object_name=(
            "entsoe/actual_generation/"
            "bidding_zone=10YFR-RTE------C/"
            "year=2026/month=08/day=20/"
            "20260820T0000Z_20260820T0100Z.xml"
        ),
        content=Path("tests/fixtures/actual_generation.xml").read_bytes(),
    )

    rows = parse_actual_generation(payload)

    assert len(rows) == 3

    exported = rows[0]

    assert exported.source_object_name == payload.object_name
    assert exported.document_mrid == "document-generation-1"
    assert exported.document_type == "A75"
    assert exported.revision_number == 1
    assert exported.document_created_at == datetime(
        2026,
        8,
        22,
        8,
        30,
        47,
        tzinfo=UTC,
    )
    assert exported.process_type == "A16"

    assert exported.time_series_mrid == "series-generation-out"
    assert exported.business_type == "A01"
    assert exported.object_aggregation == "A08"
    assert exported.in_bidding_zone is None
    assert exported.out_bidding_zone == "10YFR-RTE------C"
    assert exported.quantity_unit == "MAW"
    assert exported.curve_type == "A03"
    assert exported.psr_type == "B10"

    assert exported.period_start == datetime(2026, 8, 20, 0, 0, tzinfo=UTC)
    assert exported.period_end == datetime(2026, 8, 20, 1, 0, tzinfo=UTC)
    assert exported.resolution == "PT15M"
    assert exported.position == 1
    assert exported.point_timestamp == datetime(2026, 8, 20, 0, 0, tzinfo=UTC)
    assert exported.quantity == Decimal("206.63")

    exported_position_three = rows[1]

    assert exported_position_three.position == 3
    assert exported_position_three.point_timestamp == datetime(
        2026,
        8,
        20,
        0,
        30,
        tzinfo=UTC,
    )
    assert exported_position_three.quantity == Decimal("169.74")

    imported = rows[2]

    assert imported.time_series_mrid == "series-generation-in"
    assert imported.psr_type == "B10"
    assert imported.in_bidding_zone == "10YFR-RTE------C"
    assert imported.out_bidding_zone is None
    assert imported.quantity == Decimal("174.62")
