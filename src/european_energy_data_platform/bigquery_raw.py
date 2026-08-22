from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from hashlib import sha256

from google.cloud import bigquery

from european_energy_data_platform.parsing import (
    ActualGenerationRawRow,
    ActualLoadRawRow,
    DayAheadPriceRawRow,
)

ACTUAL_LOAD_SCHEMA = (
    bigquery.SchemaField("source_object_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("document_mrid", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("document_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("revision_number", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("document_created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("process_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("time_series_mrid", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("business_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("object_aggregation", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("out_bidding_zone", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("quantity_unit", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("curve_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("period_start", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("period_end", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("resolution", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("position", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("point_timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("quantity", "NUMERIC", mode="REQUIRED"),
)


ACTUAL_GENERATION_SCHEMA = (
    bigquery.SchemaField("source_object_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("document_mrid", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("document_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("revision_number", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("document_created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("process_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("time_series_mrid", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("business_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("object_aggregation", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("in_bidding_zone", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("out_bidding_zone", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("quantity_unit", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("curve_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("psr_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("period_start", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("period_end", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("resolution", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("position", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("point_timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("quantity", "NUMERIC", mode="REQUIRED"),
)


DAY_AHEAD_PRICES_SCHEMA = (
    bigquery.SchemaField("source_object_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("document_mrid", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("document_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("revision_number", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("document_created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("time_series_mrid", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("auction_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("business_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("in_domain", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("out_domain", "STRING", mode="REQUIRED"),
    bigquery.SchemaField(
        "contract_market_agreement_type",
        "STRING",
        mode="REQUIRED",
    ),
    bigquery.SchemaField("currency_unit", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("price_unit", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("curve_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("period_start", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("period_end", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("resolution", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("position", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("point_timestamp", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("price_amount", "NUMERIC", mode="REQUIRED"),
)


def build_raw_dataset(
    project_id: str,
    *,
    dataset_id: str = "entsoe_raw",
    location: str = "EU",
) -> bigquery.Dataset:
    dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset.location = location
    return dataset


def build_raw_tables(
    project_id: str,
    *,
    dataset_id: str = "entsoe_raw",
) -> tuple[bigquery.Table, ...]:
    table_definitions = (
        (
            "actual_load",
            ACTUAL_LOAD_SCHEMA,
            ["out_bidding_zone"],
        ),
        (
            "actual_generation",
            ACTUAL_GENERATION_SCHEMA,
            [
                "in_bidding_zone",
                "out_bidding_zone",
                "psr_type",
            ],
        ),
        (
            "day_ahead_prices",
            DAY_AHEAD_PRICES_SCHEMA,
            [
                "in_domain",
                "out_domain",
            ],
        ),
    )

    tables = []

    for table_id, schema, clustering_fields in table_definitions:
        table = bigquery.Table(
            f"{project_id}.{dataset_id}.{table_id}",
            schema=list(schema),
        )
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="point_timestamp",
        )
        table.clustering_fields = clustering_fields
        tables.append(table)

    return tuple(tables)


def provision_raw_infrastructure(
    client: bigquery.Client,
    *,
    dataset_id: str = "entsoe_raw",
    location: str = "EU",
) -> None:
    dataset = build_raw_dataset(
        client.project,
        dataset_id=dataset_id,
        location=location,
    )
    client.create_dataset(
        dataset,
        exists_ok=True,
    )

    for table in build_raw_tables(
        client.project,
        dataset_id=dataset_id,
    ):
        client.create_table(
            table,
            exists_ok=True,
        )


def _json_value(value):
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def _row_to_json(row) -> dict:
    return {key: _json_value(value) for key, value in asdict(row).items()}


class BigQueryRawLoader:
    """Load parsed ENTSO-E RAW rows into BigQuery."""

    def __init__(
        self,
        client: bigquery.Client,
        *,
        dataset_id: str = "entsoe_raw",
        location: str = "EU",
    ) -> None:
        self._client = client
        self._dataset_id = dataset_id
        self._location = location

    def load_actual_load(
        self,
        rows: list[ActualLoadRawRow],
    ) -> None:
        if not rows:
            raise ValueError("Actual Load rows must not be empty")

        source_object_name = rows[0].source_object_name
        source_hash = sha256(source_object_name.encode()).hexdigest()[:24]

        destination = f"{self._client.project}.{self._dataset_id}.actual_load"

        job_config = bigquery.LoadJobConfig(
            schema=ACTUAL_LOAD_SCHEMA,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            create_disposition=bigquery.CreateDisposition.CREATE_NEVER,
        )

        job = self._client.load_table_from_json(
            [_row_to_json(row) for row in rows],
            destination,
            job_id=f"raw_actual_load_{source_hash}",
            job_config=job_config,
            location=self._location,
        )
        job.result()

    def load_actual_generation(
        self,
        rows: list[ActualGenerationRawRow],
    ) -> None:
        if not rows:
            raise ValueError("Actual Generation rows must not be empty")

        source_object_name = rows[0].source_object_name
        source_hash = sha256(source_object_name.encode()).hexdigest()[:24]

        destination = f"{self._client.project}.{self._dataset_id}.actual_generation"

        job_config = bigquery.LoadJobConfig(
            schema=ACTUAL_GENERATION_SCHEMA,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            create_disposition=bigquery.CreateDisposition.CREATE_NEVER,
        )

        job = self._client.load_table_from_json(
            [_row_to_json(row) for row in rows],
            destination,
            job_id=f"raw_actual_generation_{source_hash}",
            job_config=job_config,
            location=self._location,
        )
        job.result()

    def load_day_ahead_prices(
        self,
        rows: list[DayAheadPriceRawRow],
    ) -> None:
        if not rows:
            raise ValueError("Day-Ahead Price rows must not be empty")

        source_object_name = rows[0].source_object_name
        source_hash = sha256(source_object_name.encode()).hexdigest()[:24]

        destination = f"{self._client.project}.{self._dataset_id}.day_ahead_prices"

        job_config = bigquery.LoadJobConfig(
            schema=DAY_AHEAD_PRICES_SCHEMA,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            create_disposition=bigquery.CreateDisposition.CREATE_NEVER,
        )

        job = self._client.load_table_from_json(
            [_row_to_json(row) for row in rows],
            destination,
            job_id=f"raw_day_ahead_prices_{source_hash}",
            job_config=job_config,
            location=self._location,
        )
        job.result()
