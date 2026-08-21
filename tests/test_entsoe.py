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


def test_build_actual_load_params() -> None:
    from european_energy_data_platform.entsoe import build_actual_load_params

    params = build_actual_load_params(
        bidding_zone="10YFR-RTE------C",
        period_start=datetime(2026, 8, 20, 0, 0, tzinfo=UTC),
        period_end=datetime(2026, 8, 20, 1, 0, tzinfo=UTC),
    )

    assert params == {
        "documentType": "A65",
        "processType": "A16",
        "outBiddingZone_Domain": "10YFR-RTE------C",
        "periodStart": "202608200000",
        "periodEnd": "202608200100",
    }


def test_build_actual_load_params_rejects_invalid_interval() -> None:
    from european_energy_data_platform.entsoe import build_actual_load_params

    period_start = datetime(2026, 8, 20, 0, 0, tzinfo=UTC)

    with pytest.raises(ValueError, match="period_end must be after period_start"):
        build_actual_load_params(
            bidding_zone="10YFR-RTE------C",
            period_start=period_start,
            period_end=period_start,
        )


def test_entsoe_client_rejects_empty_security_token() -> None:
    from european_energy_data_platform.entsoe import EntsoeClient

    with pytest.raises(ValueError, match="security token must not be empty"):
        EntsoeClient("   ")


def test_entsoe_client_fetches_actual_load_xml() -> None:
    from unittest.mock import Mock

    from european_energy_data_platform.entsoe import EntsoeClient

    session = Mock()
    response = Mock()
    response.content = b"<GL_MarketDocument />"
    session.get.return_value = response

    client = EntsoeClient(
        security_token="test-token",
        session=session,
        timeout=30.0,
    )

    result = client.fetch_actual_load(
        bidding_zone="10YFR-RTE------C",
        period_start=datetime(2026, 8, 20, 0, 0, tzinfo=UTC),
        period_end=datetime(2026, 8, 20, 1, 0, tzinfo=UTC),
    )

    assert result == b"<GL_MarketDocument />"

    session.get.assert_called_once_with(
        "https://web-api.tp.entsoe.eu/api",
        params={
            "documentType": "A65",
            "processType": "A16",
            "outBiddingZone_Domain": "10YFR-RTE------C",
            "periodStart": "202608200000",
            "periodEnd": "202608200100",
            "securityToken": "test-token",
        },
        timeout=30.0,
    )
    response.raise_for_status.assert_called_once_with()


def test_build_actual_load_raw_object_name_uses_utc() -> None:
    from european_energy_data_platform.entsoe import (
        build_actual_load_raw_object_name,
    )

    utc_plus_two = timezone(timedelta(hours=2))

    object_name = build_actual_load_raw_object_name(
        bidding_zone="10YFR-RTE------C",
        period_start=datetime(2026, 8, 20, 2, 0, tzinfo=utc_plus_two),
        period_end=datetime(2026, 8, 20, 3, 0, tzinfo=utc_plus_two),
    )

    assert object_name == (
        "entsoe/actual_load/"
        "bidding_zone=10YFR-RTE------C/"
        "year=2026/"
        "month=08/"
        "day=20/"
        "20260820T0000Z_20260820T0100Z.xml"
    )


def test_build_actual_load_raw_object_name_rejects_invalid_interval() -> None:
    from european_energy_data_platform.entsoe import (
        build_actual_load_raw_object_name,
    )

    period_start = datetime(2026, 8, 20, 0, 0, tzinfo=UTC)

    with pytest.raises(ValueError, match="period_end must be after period_start"):
        build_actual_load_raw_object_name(
            bidding_zone="10YFR-RTE------C",
            period_start=period_start,
            period_end=period_start,
        )


def test_build_actual_generation_params() -> None:
    from european_energy_data_platform.entsoe import build_actual_generation_params

    params = build_actual_generation_params(
        bidding_zone="10YFR-RTE------C",
        period_start=datetime(2026, 8, 20, 0, 0, tzinfo=UTC),
        period_end=datetime(2026, 8, 20, 1, 0, tzinfo=UTC),
    )

    assert params == {
        "documentType": "A75",
        "processType": "A16",
        "in_Domain": "10YFR-RTE------C",
        "periodStart": "202608200000",
        "periodEnd": "202608200100",
    }


def test_build_actual_generation_params_rejects_invalid_interval() -> None:
    from european_energy_data_platform.entsoe import build_actual_generation_params

    period_start = datetime(2026, 8, 20, 0, 0, tzinfo=UTC)

    with pytest.raises(ValueError, match="period_end must be after period_start"):
        build_actual_generation_params(
            bidding_zone="10YFR-RTE------C",
            period_start=period_start,
            period_end=period_start,
        )
