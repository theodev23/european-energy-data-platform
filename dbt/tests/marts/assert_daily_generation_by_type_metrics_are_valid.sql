with invalid_rows as (

    select *
    from {{ ref('agg_daily_generation_by_type') }}
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

        or minimum_generation_mw
            > average_generation_mw

        or average_generation_mw
            > maximum_generation_mw

        or observed_energy_mwh < 0

        or peak_generation_timestamp
            < timestamp(observation_date)

        or peak_generation_timestamp
            >= timestamp(
                date_add(
                    observation_date,
                    interval 1 day
                )
            )

)

select *
from invalid_rows
