from european_energy_data_platform.areas import TARGET_BIDDING_ZONES


def test_target_bidding_zones_cover_expected_markets() -> None:
    markets = {zone.market for zone in TARGET_BIDDING_ZONES}

    assert markets == {
        "France",
        "Germany / Luxembourg",
        "Spain",
        "Italy",
    }


def test_target_bidding_zones_have_unique_eic_codes() -> None:
    eic_codes = [zone.eic_code for zone in TARGET_BIDDING_ZONES]

    assert len(eic_codes) == 10
    assert len(eic_codes) == len(set(eic_codes))


def test_italy_uses_seven_geographical_bidding_zones() -> None:
    italian_zones = {zone.name for zone in TARGET_BIDDING_ZONES if zone.market == "Italy"}

    assert italian_zones == {
        "IT-North",
        "IT-Centre-North",
        "IT-Centre-South",
        "IT-South",
        "IT-Calabria",
        "IT-Sicily",
        "IT-Sardinia",
    }
