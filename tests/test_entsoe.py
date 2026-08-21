from datetime import UTC, datetime, timedelta, timezone

import pytest

from european_energy_data_platform.entsoe import format_entsoe_datetime


def test_format_entsoe_datetime_in_utc() -> None:
    value = datetime(2026, 8, 20, 0, 0, tzinfo=UTC)

    assert format_entsoe_datetime(value) == "202608200000"


def test_format_entsoe_datetime_converts_to_utc() -> None:
    utc_plus_two = timezone(timedelta(hours=2))
    value = datetime(2026, 8, 20, 2, 0, tzinfo=utc_plus_two)

    assert format_entsoe_datetime(value) == "202608200000"


def test_format_entsoe_datetime_rejects_naive_datetime() -> None:
    value = datetime(2026, 8, 20, 0, 0, tzinfo=UTC).replace(tzinfo=None)

    with pytest.raises(ValueError, match="timezone-aware"):
        format_entsoe_datetime(value)
