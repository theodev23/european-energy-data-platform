from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BiddingZone:
    """ENTSO-E bidding zone targeted by the data platform."""

    market: str
    name: str
    eic_code: str


TARGET_BIDDING_ZONES = (
    BiddingZone(
        market="France",
        name="FR",
        eic_code="10YFR-RTE------C",
    ),
    BiddingZone(
        market="Germany / Luxembourg",
        name="DE-LU",
        eic_code="10Y1001A1001A82H",
    ),
    BiddingZone(
        market="Spain",
        name="ES",
        eic_code="10YES-REE------0",
    ),
    BiddingZone(
        market="Italy",
        name="IT-North",
        eic_code="10Y1001A1001A73I",
    ),
    BiddingZone(
        market="Italy",
        name="IT-Centre-North",
        eic_code="10Y1001A1001A70O",
    ),
    BiddingZone(
        market="Italy",
        name="IT-Centre-South",
        eic_code="10Y1001A1001A71M",
    ),
    BiddingZone(
        market="Italy",
        name="IT-South",
        eic_code="10Y1001A1001A788",
    ),
    BiddingZone(
        market="Italy",
        name="IT-Calabria",
        eic_code="10Y1001C--00096J",
    ),
    BiddingZone(
        market="Italy",
        name="IT-Sicily",
        eic_code="10Y1001A1001A75E",
    ),
    BiddingZone(
        market="Italy",
        name="IT-Sardinia",
        eic_code="10Y1001A1001A74G",
    ),
)
