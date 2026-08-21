from datetime import UTC, datetime

import requests

ENTSOE_DATETIME_FORMAT = "%Y%m%d%H%M"


def format_entsoe_datetime(value: datetime) -> str:
    """Format a timezone-aware datetime for the ENTSO-E Web API."""
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("ENTSO-E timestamps must be timezone-aware")

    return value.astimezone(UTC).strftime(ENTSOE_DATETIME_FORMAT)


def _normalize_period_to_utc(
    period_start: datetime,
    period_end: datetime,
) -> tuple[datetime, datetime]:
    """Validate a period and normalize both bounds to UTC."""
    if period_start.tzinfo is None or period_start.utcoffset() is None:
        raise ValueError("period_start must be timezone-aware")

    if period_end.tzinfo is None or period_end.utcoffset() is None:
        raise ValueError("period_end must be timezone-aware")

    if period_end <= period_start:
        raise ValueError("period_end must be after period_start")

    return (
        period_start.astimezone(UTC),
        period_end.astimezone(UTC),
    )


def build_actual_load_params(
    bidding_zone: str,
    period_start: datetime,
    period_end: datetime,
) -> dict[str, str]:
    """Build query parameters for ENTSO-E Actual Total Load data."""
    period_start_utc, period_end_utc = _normalize_period_to_utc(
        period_start,
        period_end,
    )

    return {
        "documentType": "A65",
        "processType": "A16",
        "outBiddingZone_Domain": bidding_zone,
        "periodStart": period_start_utc.strftime(ENTSOE_DATETIME_FORMAT),
        "periodEnd": period_end_utc.strftime(ENTSOE_DATETIME_FORMAT),
    }


def build_actual_generation_params(
    bidding_zone: str,
    period_start: datetime,
    period_end: datetime,
) -> dict[str, str]:
    """Build query parameters for ENTSO-E Actual Generation per Production Type."""
    period_start_utc, period_end_utc = _normalize_period_to_utc(
        period_start,
        period_end,
    )

    return {
        "documentType": "A75",
        "processType": "A16",
        "in_Domain": bidding_zone,
        "periodStart": period_start_utc.strftime(ENTSOE_DATETIME_FORMAT),
        "periodEnd": period_end_utc.strftime(ENTSOE_DATETIME_FORMAT),
    }


def build_day_ahead_price_params(
    bidding_zone: str,
    period_start: datetime,
    period_end: datetime,
) -> dict[str, str]:
    """Build query parameters for ENTSO-E Day-Ahead Prices."""
    period_start_utc, period_end_utc = _normalize_period_to_utc(
        period_start,
        period_end,
    )

    return {
        "documentType": "A44",
        "contract_MarketAgreement.type": "A01",
        "out_Domain": bidding_zone,
        "in_Domain": bidding_zone,
        "periodStart": period_start_utc.strftime(ENTSOE_DATETIME_FORMAT),
        "periodEnd": period_end_utc.strftime(ENTSOE_DATETIME_FORMAT),
    }


def build_actual_load_raw_object_name(
    bidding_zone: str,
    period_start: datetime,
    period_end: datetime,
) -> str:
    """Build a deterministic RAW object name for Actual Total Load XML."""
    period_start_utc, period_end_utc = _normalize_period_to_utc(
        period_start,
        period_end,
    )

    return (
        "entsoe/actual_load/"
        f"bidding_zone={bidding_zone}/"
        f"year={period_start_utc:%Y}/"
        f"month={period_start_utc:%m}/"
        f"day={period_start_utc:%d}/"
        f"{period_start_utc:%Y%m%dT%H%MZ}_"
        f"{period_end_utc:%Y%m%dT%H%MZ}.xml"
    )


def build_actual_generation_raw_object_name(
    bidding_zone: str,
    period_start: datetime,
    period_end: datetime,
) -> str:
    """Build a deterministic RAW object name for Actual Generation XML."""
    period_start_utc, period_end_utc = _normalize_period_to_utc(
        period_start,
        period_end,
    )

    return (
        "entsoe/actual_generation/"
        f"bidding_zone={bidding_zone}/"
        f"year={period_start_utc:%Y}/"
        f"month={period_start_utc:%m}/"
        f"day={period_start_utc:%d}/"
        f"{period_start_utc:%Y%m%dT%H%MZ}_"
        f"{period_end_utc:%Y%m%dT%H%MZ}.xml"
    )


def build_day_ahead_price_raw_object_name(
    bidding_zone: str,
    period_start: datetime,
    period_end: datetime,
) -> str:
    """Build a deterministic RAW object name for Day-Ahead Prices XML."""
    period_start_utc, period_end_utc = _normalize_period_to_utc(
        period_start,
        period_end,
    )

    return (
        "entsoe/day_ahead_prices/"
        f"bidding_zone={bidding_zone}/"
        f"year={period_start_utc:%Y}/"
        f"month={period_start_utc:%m}/"
        f"day={period_start_utc:%d}/"
        f"{period_start_utc:%Y%m%dT%H%MZ}_"
        f"{period_end_utc:%Y%m%dT%H%MZ}.xml"
    )


ENTSOE_API_URL = "https://web-api.tp.entsoe.eu/api"
ENTSOE_DEFAULT_TIMEOUT_SECONDS = 30.0


class EntsoeClient:
    """HTTP client for the ENTSO-E Transparency Platform Web API."""

    def __init__(
        self,
        security_token: str,
        session: requests.Session | None = None,
        timeout: float = ENTSOE_DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        security_token = security_token.strip()

        if not security_token:
            raise ValueError("ENTSO-E security token must not be empty")

        self._security_token = security_token
        self._session = session or requests.Session()
        self._timeout = timeout

    def fetch_actual_load(
        self,
        bidding_zone: str,
        period_start: datetime,
        period_end: datetime,
    ) -> bytes:
        """Fetch raw Actual Total Load XML from ENTSO-E."""
        params = build_actual_load_params(
            bidding_zone=bidding_zone,
            period_start=period_start,
            period_end=period_end,
        )
        params["securityToken"] = self._security_token

        response = self._session.get(
            ENTSOE_API_URL,
            params=params,
            timeout=self._timeout,
        )
        response.raise_for_status()

        return response.content

    def fetch_actual_generation(
        self,
        bidding_zone: str,
        period_start: datetime,
        period_end: datetime,
    ) -> bytes:
        """Fetch raw Actual Generation per Production Type XML from ENTSO-E."""
        params = build_actual_generation_params(
            bidding_zone=bidding_zone,
            period_start=period_start,
            period_end=period_end,
        )
        params["securityToken"] = self._security_token

        response = self._session.get(
            ENTSOE_API_URL,
            params=params,
            timeout=self._timeout,
        )
        response.raise_for_status()

        return response.content

    def fetch_day_ahead_prices(
        self,
        bidding_zone: str,
        period_start: datetime,
        period_end: datetime,
    ) -> bytes:
        """Fetch raw Day-Ahead Prices XML from ENTSO-E."""
        params = build_day_ahead_price_params(
            bidding_zone=bidding_zone,
            period_start=period_start,
            period_end=period_end,
        )
        params["securityToken"] = self._security_token

        response = self._session.get(
            ENTSOE_API_URL,
            params=params,
            timeout=self._timeout,
        )
        response.raise_for_status()

        return response.content
