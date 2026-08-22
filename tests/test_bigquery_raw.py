from european_energy_data_platform.bigquery_raw import (
    ACTUAL_GENERATION_SCHEMA,
    ACTUAL_LOAD_SCHEMA,
    DAY_AHEAD_PRICES_SCHEMA,
)


def _schema_signature(schema):
    return [(field.name, field.field_type, field.mode) for field in schema]


def test_actual_load_schema_matches_raw_row_contract() -> None:
    assert _schema_signature(ACTUAL_LOAD_SCHEMA) == [
        ("source_object_name", "STRING", "REQUIRED"),
        ("document_mrid", "STRING", "REQUIRED"),
        ("document_type", "STRING", "REQUIRED"),
        ("revision_number", "INTEGER", "REQUIRED"),
        ("document_created_at", "TIMESTAMP", "REQUIRED"),
        ("process_type", "STRING", "REQUIRED"),
        ("time_series_mrid", "STRING", "REQUIRED"),
        ("business_type", "STRING", "REQUIRED"),
        ("object_aggregation", "STRING", "REQUIRED"),
        ("out_bidding_zone", "STRING", "REQUIRED"),
        ("quantity_unit", "STRING", "REQUIRED"),
        ("curve_type", "STRING", "REQUIRED"),
        ("period_start", "TIMESTAMP", "REQUIRED"),
        ("period_end", "TIMESTAMP", "REQUIRED"),
        ("resolution", "STRING", "REQUIRED"),
        ("position", "INTEGER", "REQUIRED"),
        ("point_timestamp", "TIMESTAMP", "REQUIRED"),
        ("quantity", "NUMERIC", "REQUIRED"),
    ]


def test_actual_generation_schema_matches_raw_row_contract() -> None:
    assert _schema_signature(ACTUAL_GENERATION_SCHEMA) == [
        ("source_object_name", "STRING", "REQUIRED"),
        ("document_mrid", "STRING", "REQUIRED"),
        ("document_type", "STRING", "REQUIRED"),
        ("revision_number", "INTEGER", "REQUIRED"),
        ("document_created_at", "TIMESTAMP", "REQUIRED"),
        ("process_type", "STRING", "REQUIRED"),
        ("time_series_mrid", "STRING", "REQUIRED"),
        ("business_type", "STRING", "REQUIRED"),
        ("object_aggregation", "STRING", "REQUIRED"),
        ("in_bidding_zone", "STRING", "NULLABLE"),
        ("out_bidding_zone", "STRING", "NULLABLE"),
        ("quantity_unit", "STRING", "REQUIRED"),
        ("curve_type", "STRING", "REQUIRED"),
        ("psr_type", "STRING", "REQUIRED"),
        ("period_start", "TIMESTAMP", "REQUIRED"),
        ("period_end", "TIMESTAMP", "REQUIRED"),
        ("resolution", "STRING", "REQUIRED"),
        ("position", "INTEGER", "REQUIRED"),
        ("point_timestamp", "TIMESTAMP", "REQUIRED"),
        ("quantity", "NUMERIC", "REQUIRED"),
    ]


def test_day_ahead_prices_schema_matches_raw_row_contract() -> None:
    assert _schema_signature(DAY_AHEAD_PRICES_SCHEMA) == [
        ("source_object_name", "STRING", "REQUIRED"),
        ("document_mrid", "STRING", "REQUIRED"),
        ("document_type", "STRING", "REQUIRED"),
        ("revision_number", "INTEGER", "REQUIRED"),
        ("document_created_at", "TIMESTAMP", "REQUIRED"),
        ("time_series_mrid", "STRING", "REQUIRED"),
        ("auction_type", "STRING", "REQUIRED"),
        ("business_type", "STRING", "REQUIRED"),
        ("in_domain", "STRING", "REQUIRED"),
        ("out_domain", "STRING", "REQUIRED"),
        ("contract_market_agreement_type", "STRING", "REQUIRED"),
        ("currency_unit", "STRING", "REQUIRED"),
        ("price_unit", "STRING", "REQUIRED"),
        ("curve_type", "STRING", "REQUIRED"),
        ("period_start", "TIMESTAMP", "REQUIRED"),
        ("period_end", "TIMESTAMP", "REQUIRED"),
        ("resolution", "STRING", "REQUIRED"),
        ("position", "INTEGER", "REQUIRED"),
        ("point_timestamp", "TIMESTAMP", "REQUIRED"),
        ("price_amount", "NUMERIC", "REQUIRED"),
    ]
