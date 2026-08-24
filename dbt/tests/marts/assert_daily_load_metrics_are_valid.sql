with invalid_rows as (

    select *
    from {{ ref('agg_daily_load') }}
    where
        interval_minutes <= 0

        or expected_interval_count <= 0

        or observed_interval_count < 0

        or observed_interval_count > expected_interval_count

        or coverage_ratio < 0
        or coverage_ratio > 1

        or (
            is_complete_observation_day
            != (
                observed_interval_count
                = expected_interval_count
            )
        )

        or minimum_load_mw > average_load_mw

        or average_load_mw > maximum_load_mw

        or observed_energy_mwh < 0

        or peak_load_timestamp
            < timestamp(observation_date)

        or peak_load_timestamp
            >= timestamp(
                date_add(
                    observation_date,
                    interval 1 day
                )
            )

)

select *
from invalid_rows
