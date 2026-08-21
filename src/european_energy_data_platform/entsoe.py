from datetime import UTC, datetime

ENTSOE_DATETIME_FORMAT = "%Y%m%d%H%M"


def format_entsoe_datetime(value: datetime) -> str:
    """Format a timezone-aware datetime for the ENTSO-E Web API."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("ENTSO-E timestamps must be timezone-aware")

    return value.astimezone(UTC).strftime(ENTSOE_DATETIME_FORMAT)


def build_actual_load_params(
    bidding_zone: str,
    period_start: datetime,
    period_end: datetime,
) -> dict[str, str]:
    """Build query parameters for ENTSO-E Actual Total Load data."""
    if period_end <= period_start:
        raise ValueError("period_end must be after period_start")

    return {
        "documentType": "A65",
        "processType": "A16",
        "outBiddingZone_Domain": bidding_zone,
        "periodStart": format_entsoe_datetime(period_start),
        "periodEnd": format_entsoe_datetime(period_end),
    }
