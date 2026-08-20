def test_package_is_importable() -> None:
    import european_energy_data_platform

    assert european_energy_data_platform.__name__ == "european_energy_data_platform"
