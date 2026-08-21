from dataclasses import dataclass
from datetime import datetime

from european_energy_data_platform.entsoe import (
    EntsoeClient,
    build_actual_generation_raw_object_name,
    build_actual_load_raw_object_name,
)


@dataclass(frozen=True, slots=True)
class RawPayload:
    """Raw source payload ready to be persisted."""

    object_name: str
    content: bytes


def extract_actual_load(
    client: EntsoeClient,
    bidding_zone: str,
    period_start: datetime,
    period_end: datetime,
) -> RawPayload:
    """Extract Actual Total Load XML and associate its RAW object name."""
    content = client.fetch_actual_load(
        bidding_zone=bidding_zone,
        period_start=period_start,
        period_end=period_end,
    )

    object_name = build_actual_load_raw_object_name(
        bidding_zone=bidding_zone,
        period_start=period_start,
        period_end=period_end,
    )

    return RawPayload(
        object_name=object_name,
        content=content,
    )


def extract_actual_generation(
    client: EntsoeClient,
    bidding_zone: str,
    period_start: datetime,
    period_end: datetime,
) -> RawPayload:
    """Extract Actual Generation XML and associate its RAW object name."""
    content = client.fetch_actual_generation(
        bidding_zone=bidding_zone,
        period_start=period_start,
        period_end=period_end,
    )

    object_name = build_actual_generation_raw_object_name(
        bidding_zone=bidding_zone,
        period_start=period_start,
        period_end=period_end,
    )

    return RawPayload(
        object_name=object_name,
        content=content,
    )
