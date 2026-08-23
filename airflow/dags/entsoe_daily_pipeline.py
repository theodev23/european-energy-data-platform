import os
import subprocess
from collections.abc import Callable
from dataclasses import asdict
from datetime import UTC, datetime, timedelta
from pathlib import Path

from airflow.sdk import dag, get_current_context, task
from airflow.timetables.interval import CronDataIntervalTimetable

from european_energy_data_platform.areas import TARGET_BIDDING_ZONES
from european_energy_data_platform.bigquery_raw import BigQueryRawLoader
from european_energy_data_platform.entsoe import EntsoeClient
from european_energy_data_platform.gcs import GcsRawStorage
from european_energy_data_platform.pipeline import (
    IngestionResult,
)
from european_energy_data_platform.pipeline import (
    ingest_actual_generation as run_actual_generation_ingestion,
)
from european_energy_data_platform.pipeline import (
    ingest_actual_load as run_actual_load_ingestion,
)
from european_energy_data_platform.pipeline import (
    ingest_day_ahead_prices as run_day_ahead_prices_ingestion,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BIDDING_ZONE_CODES = [zone.eic_code for zone in TARGET_BIDDING_ZONES]

IngestionFunction = Callable[..., IngestionResult]


def _required_environment_variable(name: str) -> str:
    value = os.environ.get(name, "").strip()

    if not value:
        raise RuntimeError(f"Required environment variable {name} is missing")

    return value


def _build_ingestion_services() -> tuple[
    EntsoeClient,
    GcsRawStorage,
    BigQueryRawLoader,
]:
    from google.cloud import bigquery, storage

    security_token = _required_environment_variable("ENTSOE_API_TOKEN")
    bucket_name = _required_environment_variable("GCS_RAW_BUCKET")
    project_id = _required_environment_variable("GCP_PROJECT_ID")

    entsoe_client = EntsoeClient(
        security_token=security_token,
    )
    storage_client = storage.Client(
        project=project_id,
    )
    bigquery_client = bigquery.Client(
        project=project_id,
    )

    raw_storage = GcsRawStorage(
        bucket_name=bucket_name,
        client=storage_client,
    )
    raw_loader = BigQueryRawLoader(
        client=bigquery_client,
    )

    return (
        entsoe_client,
        raw_storage,
        raw_loader,
    )


def _run_ingestion(
    *,
    function: IngestionFunction,
    bidding_zone: str,
) -> dict:
    context = get_current_context()
    period_start = context["data_interval_start"]
    period_end = context["data_interval_end"]

    client, storage, loader = _build_ingestion_services()

    result = function(
        client=client,
        storage=storage,
        loader=loader,
        bidding_zone=bidding_zone,
        period_start=period_start,
        period_end=period_end,
    )

    return asdict(result)


@dag(
    dag_id="entsoe_daily_pipeline",
    description="Daily ENTSO-E ingestion and dbt transformation pipeline.",
    schedule=CronDataIntervalTimetable(
        "@daily",
        timezone="UTC",
    ),
    start_date=datetime(2026, 8, 1, tzinfo=UTC),
    catchup=False,
    max_active_runs=1,
    max_active_tasks=3,
    tags=["entsoe", "energy", "elt"],
)
def entsoe_daily_pipeline():
    @task(
        retries=2,
        retry_delay=timedelta(minutes=5),
        max_active_tis_per_dag=1,
    )
    def ingest_actual_load(bidding_zone: str) -> dict:
        return _run_ingestion(
            function=run_actual_load_ingestion,
            bidding_zone=bidding_zone,
        )

    @task(
        retries=2,
        retry_delay=timedelta(minutes=5),
        max_active_tis_per_dag=1,
    )
    def ingest_actual_generation(bidding_zone: str) -> dict:
        return _run_ingestion(
            function=run_actual_generation_ingestion,
            bidding_zone=bidding_zone,
        )

    @task(
        retries=2,
        retry_delay=timedelta(minutes=5),
        max_active_tis_per_dag=1,
    )
    def ingest_day_ahead_prices(bidding_zone: str) -> dict:
        return _run_ingestion(
            function=run_day_ahead_prices_ingestion,
            bidding_zone=bidding_zone,
        )

    @task(
        retries=1,
        retry_delay=timedelta(minutes=2),
    )
    def run_dbt_build() -> None:
        _required_environment_variable("GCP_PROJECT_ID")
        _required_environment_variable("DBT_DATASET")

        dbt_environment = os.environ.copy()
        dbt_environment.pop("ENTSOE_API_TOKEN", None)
        dbt_environment.pop("GCS_RAW_BUCKET", None)

        subprocess.run(
            [
                str(REPOSITORY_ROOT / ".venv-dbt" / "bin" / "dbt"),
                "build",
                "--project-dir",
                str(REPOSITORY_ROOT / "dbt"),
                "--profiles-dir",
                str(REPOSITORY_ROOT / "dbt"),
            ],
            cwd=REPOSITORY_ROOT,
            env=dbt_environment,
            check=True,
        )

    actual_load = ingest_actual_load.expand(
        bidding_zone=BIDDING_ZONE_CODES,
    )
    actual_generation = ingest_actual_generation.expand(
        bidding_zone=BIDDING_ZONE_CODES,
    )
    day_ahead_prices = ingest_day_ahead_prices.expand(
        bidding_zone=BIDDING_ZONE_CODES,
    )

    dbt_build = run_dbt_build()

    actual_load >> dbt_build
    actual_generation >> dbt_build
    day_ahead_prices >> dbt_build


dag = entsoe_daily_pipeline()
