import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from european_energy_data_platform.ingestion import RawPayload


@dataclass(frozen=True, slots=True)
class ActualLoadRawRow:
    """One source-aligned ENTSO-E Actual Load point."""

    source_object_name: str
    document_mrid: str
    document_type: str
    revision_number: int
    document_created_at: datetime
    process_type: str
    time_series_mrid: str
    business_type: str
    object_aggregation: str
    out_bidding_zone: str
    quantity_unit: str
    curve_type: str
    period_start: datetime
    period_end: datetime
    resolution: str
    position: int
    point_timestamp: datetime
    quantity: Decimal


@dataclass(frozen=True, slots=True)
class ActualGenerationRawRow:
    """One source-aligned ENTSO-E Actual Generation point."""

    source_object_name: str
    document_mrid: str
    document_type: str
    revision_number: int
    document_created_at: datetime
    process_type: str
    time_series_mrid: str
    business_type: str
    object_aggregation: str
    in_bidding_zone: str | None
    out_bidding_zone: str | None
    quantity_unit: str
    curve_type: str
    psr_type: str
    period_start: datetime
    period_end: datetime
    resolution: str
    position: int
    point_timestamp: datetime
    quantity: Decimal


@dataclass(frozen=True, slots=True)
class DayAheadPriceRawRow:
    """One source-aligned ENTSO-E Day-Ahead Price point."""

    source_object_name: str
    document_mrid: str
    document_type: str
    revision_number: int
    document_created_at: datetime
    time_series_mrid: str
    auction_type: str
    business_type: str
    in_domain: str
    out_domain: str
    contract_market_agreement_type: str
    currency_unit: str
    price_unit: str
    curve_type: str
    period_start: datetime
    period_end: datetime
    resolution: str
    position: int
    point_timestamp: datetime
    price_amount: Decimal


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _direct_child(element: ET.Element, name: str) -> ET.Element:
    for child in element:
        if _local_name(child.tag) == name:
            return child

    raise ValueError(f"Missing required XML element: {name}")


def _required_text(element: ET.Element, name: str) -> str:
    child = _direct_child(element, name)
    value = (child.text or "").strip()

    if not value:
        raise ValueError(f"XML element must not be empty: {name}")

    return value


def _optional_text(element: ET.Element, name: str) -> str | None:
    for child in element:
        if _local_name(child.tag) == name:
            value = (child.text or "").strip()
            return value or None

    return None


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)

    if parsed.tzinfo is None:
        raise ValueError("ENTSO-E timestamp must be timezone-aware")

    return parsed.astimezone(UTC)


def _parse_resolution(value: str) -> timedelta:
    match = re.fullmatch(
        r"PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?",
        value,
    )

    if match is None:
        raise ValueError(f"Unsupported ENTSO-E resolution: {value}")

    duration = timedelta(
        hours=int(match.group("hours") or 0),
        minutes=int(match.group("minutes") or 0),
        seconds=int(match.group("seconds") or 0),
    )

    if duration <= timedelta(0):
        raise ValueError(f"ENTSO-E resolution must be positive: {value}")

    return duration


def parse_actual_load(payload: RawPayload) -> list[ActualLoadRawRow]:
    """Parse an ENTSO-E Actual Load XML payload into point-level RAW rows."""
    root = ET.fromstring(payload.content)

    document_mrid = _required_text(root, "mRID")
    document_type = _required_text(root, "type")
    revision_number = int(_required_text(root, "revisionNumber"))
    document_created_at = _parse_datetime(_required_text(root, "createdDateTime"))
    process_type = _required_text(root, "process.processType")

    rows: list[ActualLoadRawRow] = []

    for time_series in root:
        if _local_name(time_series.tag) != "TimeSeries":
            continue

        time_series_mrid = _required_text(time_series, "mRID")
        business_type = _required_text(time_series, "businessType")
        object_aggregation = _required_text(time_series, "objectAggregation")
        out_bidding_zone = _required_text(
            time_series,
            "outBiddingZone_Domain.mRID",
        )
        quantity_unit = _required_text(
            time_series,
            "quantity_Measure_Unit.name",
        )
        curve_type = _required_text(time_series, "curveType")

        for period in time_series:
            if _local_name(period.tag) != "Period":
                continue

            time_interval = _direct_child(period, "timeInterval")
            period_start = _parse_datetime(_required_text(time_interval, "start"))
            period_end = _parse_datetime(_required_text(time_interval, "end"))
            resolution = _required_text(period, "resolution")
            resolution_delta = _parse_resolution(resolution)

            for point in period:
                if _local_name(point.tag) != "Point":
                    continue

                position = int(_required_text(point, "position"))
                quantity = Decimal(_required_text(point, "quantity"))

                if position < 1:
                    raise ValueError("ENTSO-E point position must be positive")

                rows.append(
                    ActualLoadRawRow(
                        source_object_name=payload.object_name,
                        document_mrid=document_mrid,
                        document_type=document_type,
                        revision_number=revision_number,
                        document_created_at=document_created_at,
                        process_type=process_type,
                        time_series_mrid=time_series_mrid,
                        business_type=business_type,
                        object_aggregation=object_aggregation,
                        out_bidding_zone=out_bidding_zone,
                        quantity_unit=quantity_unit,
                        curve_type=curve_type,
                        period_start=period_start,
                        period_end=period_end,
                        resolution=resolution,
                        position=position,
                        point_timestamp=(period_start + resolution_delta * (position - 1)),
                        quantity=quantity,
                    )
                )

    return rows


def parse_actual_generation(payload: RawPayload) -> list[ActualGenerationRawRow]:
    """Parse ENTSO-E Actual Generation XML into point-level RAW rows."""
    root = ET.fromstring(payload.content)

    document_mrid = _required_text(root, "mRID")
    document_type = _required_text(root, "type")
    revision_number = int(_required_text(root, "revisionNumber"))
    document_created_at = _parse_datetime(_required_text(root, "createdDateTime"))
    process_type = _required_text(root, "process.processType")

    rows: list[ActualGenerationRawRow] = []

    for time_series in root:
        if _local_name(time_series.tag) != "TimeSeries":
            continue

        time_series_mrid = _required_text(time_series, "mRID")
        business_type = _required_text(time_series, "businessType")
        object_aggregation = _required_text(time_series, "objectAggregation")
        in_bidding_zone = _optional_text(
            time_series,
            "inBiddingZone_Domain.mRID",
        )
        out_bidding_zone = _optional_text(
            time_series,
            "outBiddingZone_Domain.mRID",
        )
        quantity_unit = _required_text(
            time_series,
            "quantity_Measure_Unit.name",
        )
        curve_type = _required_text(time_series, "curveType")

        market_psr_type = _direct_child(time_series, "MktPSRType")
        psr_type = _required_text(market_psr_type, "psrType")

        for period in time_series:
            if _local_name(period.tag) != "Period":
                continue

            time_interval = _direct_child(period, "timeInterval")
            period_start = _parse_datetime(_required_text(time_interval, "start"))
            period_end = _parse_datetime(_required_text(time_interval, "end"))
            resolution = _required_text(period, "resolution")
            resolution_delta = _parse_resolution(resolution)

            for point in period:
                if _local_name(point.tag) != "Point":
                    continue

                position = int(_required_text(point, "position"))
                quantity = Decimal(_required_text(point, "quantity"))

                if position < 1:
                    raise ValueError("ENTSO-E point position must be positive")

                rows.append(
                    ActualGenerationRawRow(
                        source_object_name=payload.object_name,
                        document_mrid=document_mrid,
                        document_type=document_type,
                        revision_number=revision_number,
                        document_created_at=document_created_at,
                        process_type=process_type,
                        time_series_mrid=time_series_mrid,
                        business_type=business_type,
                        object_aggregation=object_aggregation,
                        in_bidding_zone=in_bidding_zone,
                        out_bidding_zone=out_bidding_zone,
                        quantity_unit=quantity_unit,
                        curve_type=curve_type,
                        psr_type=psr_type,
                        period_start=period_start,
                        period_end=period_end,
                        resolution=resolution,
                        position=position,
                        point_timestamp=(period_start + resolution_delta * (position - 1)),
                        quantity=quantity,
                    )
                )

    return rows


def parse_day_ahead_prices(payload: RawPayload) -> list[DayAheadPriceRawRow]:
    """Parse ENTSO-E Day-Ahead Price XML into point-level RAW rows."""
    root = ET.fromstring(payload.content)

    document_mrid = _required_text(root, "mRID")
    document_type = _required_text(root, "type")
    revision_number = int(_required_text(root, "revisionNumber"))
    document_created_at = _parse_datetime(_required_text(root, "createdDateTime"))

    rows: list[DayAheadPriceRawRow] = []

    for time_series in root:
        if _local_name(time_series.tag) != "TimeSeries":
            continue

        time_series_mrid = _required_text(time_series, "mRID")
        auction_type = _required_text(time_series, "auction.type")
        business_type = _required_text(time_series, "businessType")
        in_domain = _required_text(time_series, "in_Domain.mRID")
        out_domain = _required_text(time_series, "out_Domain.mRID")
        contract_market_agreement_type = _required_text(
            time_series,
            "contract_MarketAgreement.type",
        )
        currency_unit = _required_text(
            time_series,
            "currency_Unit.name",
        )
        price_unit = _required_text(
            time_series,
            "price_Measure_Unit.name",
        )
        curve_type = _required_text(time_series, "curveType")

        for period in time_series:
            if _local_name(period.tag) != "Period":
                continue

            time_interval = next(
                (
                    child
                    for child in period
                    if _local_name(child.tag) in {"timeInterval", "period.timeInterval"}
                ),
                None,
            )

            if time_interval is None:
                raise ValueError(
                    "Missing required XML element: timeInterval or period.timeInterval"
                )

            period_start = _parse_datetime(_required_text(time_interval, "start"))
            period_end = _parse_datetime(_required_text(time_interval, "end"))
            resolution = _required_text(period, "resolution")
            resolution_delta = _parse_resolution(resolution)

            for point in period:
                if _local_name(point.tag) != "Point":
                    continue

                position = int(_required_text(point, "position"))
                price_amount = Decimal(_required_text(point, "price.amount"))

                if position < 1:
                    raise ValueError("ENTSO-E point position must be positive")

                rows.append(
                    DayAheadPriceRawRow(
                        source_object_name=payload.object_name,
                        document_mrid=document_mrid,
                        document_type=document_type,
                        revision_number=revision_number,
                        document_created_at=document_created_at,
                        time_series_mrid=time_series_mrid,
                        auction_type=auction_type,
                        business_type=business_type,
                        in_domain=in_domain,
                        out_domain=out_domain,
                        contract_market_agreement_type=(contract_market_agreement_type),
                        currency_unit=currency_unit,
                        price_unit=price_unit,
                        curve_type=curve_type,
                        period_start=period_start,
                        period_end=period_end,
                        resolution=resolution,
                        position=position,
                        point_timestamp=(period_start + resolution_delta * (position - 1)),
                        price_amount=price_amount,
                    )
                )

    return rows
