from datetime import UTC, datetime

ENTSOE_DATETIME_FORMAT = "%Y%m%d%H%M"


def format_entsoe_datetime(value: datetime) -> str:
    """Format a timezone-aware datetime for the ENTSO-E Web API."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("ENTSO-E timestamps must be timezone-aware")

    return value.astimezone(UTC).strftime(ENTSOE_DATETIME_FORMAT)
