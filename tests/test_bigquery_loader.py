from hashlib import sha256
from pathlib import Path

from google.cloud import bigquery

from european_energy_data_platform.ingestion import RawPayload
from european_energy_data_platform.parsing import (
    parse_actual_generation,
    parse_actual_load,
    parse_day_ahead_prices,
)


class FakeLoadJob:
    def __init__(self) -> None:
        self.result_call_count = 0

    def result(self) -> None:
        self.result_call_count += 1


class FakeBigQueryClient:
    project = "european-energy-data-td26"

    def __init__(self) -> None:
        self.calls = []
        self.job = FakeLoadJob()

    def load_table_from_json(
        self,
        json_rows,
        destination,
        *,
        job_id,
        job_config,
        location,
    ):
        self.calls.append(
            {
                "json_rows": json_rows,
                "destination": destination,
                "job_id": job_id,
                "job_config": job_config,
                "location": location,
            }
        )
        return self.job


def test_load_actual_load_uses_deterministic_bigquery_load_job() -> None:
    from european_energy_data_platform.bigquery_raw import BigQueryRawLoader

    payload = RawPayload(
        object_name=(
            "entsoe/actual_load/"
            "bidding_zone=10YFR-RTE------C/"
            "year=2026/month=08/day=20/"
            "20260820T0000Z_20260820T0100Z.xml"
        ),
        content=Path("tests/fixtures/actual_load.xml").read_bytes(),
    )
    rows = parse_actual_load(payload)

    client = FakeBigQueryClient()
    loader = BigQueryRawLoader(client=client)

    loader.load_actual_load(rows)

    assert len(client.calls) == 1

    call = client.calls[0]

    assert call["destination"] == ("european-energy-data-td26.entsoe_raw.actual_load")
    assert call["location"] == "EU"

    expected_hash = sha256(payload.object_name.encode()).hexdigest()[:24]
    assert call["job_id"] == f"raw_actual_load_{expected_hash}"

    job_config = call["job_config"]

    assert job_config.write_disposition == bigquery.WriteDisposition.WRITE_APPEND
    assert job_config.create_disposition == bigquery.CreateDisposition.CREATE_NEVER

    assert len(call["json_rows"]) == len(rows)

    first_json_row = call["json_rows"][0]
    first_source_row = rows[0]

    assert first_json_row["source_object_name"] == payload.object_name
    assert first_json_row["document_created_at"] == (
        first_source_row.document_created_at.isoformat()
    )
    assert first_json_row["point_timestamp"] == (first_source_row.point_timestamp.isoformat())
    assert first_json_row["quantity"] == str(first_source_row.quantity)

    assert client.job.result_call_count == 1


def test_load_actual_generation_uses_deterministic_bigquery_load_job() -> None:
    from european_energy_data_platform.bigquery_raw import BigQueryRawLoader

    payload = RawPayload(
        object_name=(
            "entsoe/actual_generation/"
            "bidding_zone=10YFR-RTE------C/"
            "year=2026/month=08/day=20/"
            "20260820T0000Z_20260820T0100Z.xml"
        ),
        content=Path("tests/fixtures/actual_generation.xml").read_bytes(),
    )
    rows = parse_actual_generation(payload)

    client = FakeBigQueryClient()
    loader = BigQueryRawLoader(client=client)

    loader.load_actual_generation(rows)

    assert len(client.calls) == 1

    call = client.calls[0]

    assert call["destination"] == ("european-energy-data-td26.entsoe_raw.actual_generation")
    assert call["location"] == "EU"

    expected_hash = sha256(payload.object_name.encode()).hexdigest()[:24]
    assert call["job_id"] == f"raw_actual_generation_{expected_hash}"

    job_config = call["job_config"]

    assert job_config.write_disposition == bigquery.WriteDisposition.WRITE_APPEND
    assert job_config.create_disposition == bigquery.CreateDisposition.CREATE_NEVER

    assert len(call["json_rows"]) == len(rows)

    exported = call["json_rows"][0]

    assert exported["psr_type"] == "B10"
    assert exported["in_bidding_zone"] is None
    assert exported["out_bidding_zone"] == "10YFR-RTE------C"
    assert exported["quantity"] == "206.63"

    imported = call["json_rows"][2]

    assert imported["psr_type"] == "B10"
    assert imported["in_bidding_zone"] == "10YFR-RTE------C"
    assert imported["out_bidding_zone"] is None
    assert imported["quantity"] == "174.62"

    assert client.job.result_call_count == 1


def test_load_day_ahead_prices_uses_deterministic_bigquery_load_job() -> None:
    from european_energy_data_platform.bigquery_raw import BigQueryRawLoader

    payload = RawPayload(
        object_name=(
            "entsoe/day_ahead_prices/"
            "bidding_zone=10YFR-RTE------C/"
            "year=2026/month=08/day=20/"
            "20260820T0000Z_20260820T0100Z.xml"
        ),
        content=Path("tests/fixtures/day_ahead_prices.xml").read_bytes(),
    )
    rows = parse_day_ahead_prices(payload)

    client = FakeBigQueryClient()
    loader = BigQueryRawLoader(client=client)

    loader.load_day_ahead_prices(rows)

    assert len(client.calls) == 1

    call = client.calls[0]

    assert call["destination"] == ("european-energy-data-td26.entsoe_raw.day_ahead_prices")
    assert call["location"] == "EU"

    expected_hash = sha256(payload.object_name.encode()).hexdigest()[:24]
    assert call["job_id"] == f"raw_day_ahead_prices_{expected_hash}"

    job_config = call["job_config"]

    assert job_config.write_disposition == bigquery.WriteDisposition.WRITE_APPEND
    assert job_config.create_disposition == bigquery.CreateDisposition.CREATE_NEVER

    assert len(call["json_rows"]) == len(rows)

    first_series = call["json_rows"][0]

    assert first_series["time_series_mrid"] == "series-price-1"
    assert first_series["position"] == 24
    assert first_series["price_amount"] == "164.96"
    assert first_series["currency_unit"] == "EUR"
    assert first_series["price_unit"] == "MWH"

    after_gap = call["json_rows"][1]

    assert after_gap["position"] == 26
    assert after_gap["point_timestamp"] == (rows[1].point_timestamp.isoformat())
    assert after_gap["price_amount"] == "165.40"

    second_series = call["json_rows"][2]

    assert second_series["time_series_mrid"] == "series-price-2"
    assert second_series["position"] == 24
    assert second_series["price_amount"] == "164.96"

    assert client.job.result_call_count == 1
