from google.cloud import bigquery

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
        ("classification_sequence_position", "INTEGER", "NULLABLE"),
        ("curve_type", "STRING", "REQUIRED"),
        ("period_start", "TIMESTAMP", "REQUIRED"),
        ("period_end", "TIMESTAMP", "REQUIRED"),
        ("resolution", "STRING", "REQUIRED"),
        ("position", "INTEGER", "REQUIRED"),
        ("point_timestamp", "TIMESTAMP", "REQUIRED"),
        ("price_amount", "NUMERIC", "REQUIRED"),
    ]


def test_raw_bigquery_infrastructure_contract() -> None:
    from european_energy_data_platform.bigquery_raw import (
        build_raw_dataset,
        build_raw_tables,
    )

    project_id = "european-energy-data-td26"

    dataset = build_raw_dataset(project_id)

    assert dataset.project == project_id
    assert dataset.dataset_id == "entsoe_raw"
    assert dataset.location == "EU"

    tables = {table.table_id: table for table in build_raw_tables(project_id)}

    assert set(tables) == {
        "actual_load",
        "actual_generation",
        "day_ahead_prices",
    }

    assert tables["actual_load"].schema == list(ACTUAL_LOAD_SCHEMA)
    assert tables["actual_generation"].schema == list(ACTUAL_GENERATION_SCHEMA)
    assert tables["day_ahead_prices"].schema == list(DAY_AHEAD_PRICES_SCHEMA)

    for table in tables.values():
        assert table.project == project_id
        assert table.dataset_id == "entsoe_raw"
        assert table.time_partitioning is not None
        assert table.time_partitioning.type_ == bigquery.TimePartitioningType.DAY
        assert table.time_partitioning.field == "point_timestamp"

    assert tables["actual_load"].clustering_fields == [
        "out_bidding_zone",
    ]
    assert tables["actual_generation"].clustering_fields == [
        "in_bidding_zone",
        "out_bidding_zone",
        "psr_type",
    ]
    assert tables["day_ahead_prices"].clustering_fields == [
        "in_domain",
        "out_domain",
    ]


class FakeBigQueryAdminClient:
    project = "european-energy-data-td26"

    def __init__(self) -> None:
        self.dataset_calls = []
        self.table_calls = []

    def create_dataset(self, dataset, *, exists_ok):
        self.dataset_calls.append(
            {
                "dataset": dataset,
                "exists_ok": exists_ok,
            }
        )
        return dataset

    def create_table(self, table, *, exists_ok):
        self.table_calls.append(
            {
                "table": table,
                "exists_ok": exists_ok,
            }
        )
        return table


def test_provision_raw_infrastructure_creates_dataset_and_tables_idempotently() -> None:
    from european_energy_data_platform.bigquery_raw import (
        provision_raw_infrastructure,
    )

    client = FakeBigQueryAdminClient()

    provision_raw_infrastructure(client)

    assert len(client.dataset_calls) == 1

    dataset_call = client.dataset_calls[0]

    assert dataset_call["dataset"].project == client.project
    assert dataset_call["dataset"].dataset_id == "entsoe_raw"
    assert dataset_call["dataset"].location == "EU"
    assert dataset_call["exists_ok"] is True

    assert len(client.table_calls) == 3

    table_ids = [call["table"].table_id for call in client.table_calls]

    assert table_ids == [
        "actual_load",
        "actual_generation",
        "day_ahead_prices",
    ]

    assert all(call["table"].project == client.project for call in client.table_calls)
    assert all(call["table"].dataset_id == "entsoe_raw" for call in client.table_calls)
    assert all(call["exists_ok"] is True for call in client.table_calls)
