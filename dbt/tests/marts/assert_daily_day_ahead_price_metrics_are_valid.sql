with invalid_rows as (

    select *
    from {{ ref('agg_daily_day_ahead_prices') }}
    where
        period_end <= period_start

        or interval_minutes <= 0

        or expected_interval_count <= 0

        or observed_interval_count < 0

        or observed_interval_count > expected_interval_count

        or coverage_ratio < 0
        or coverage_ratio > 1

        or (
            is_complete_delivery_day
            != (
                observed_interval_count
                = expected_interval_count
            )
        )

        or negative_price_interval_count < 0

        or negative_price_interval_count
            > observed_interval_count

        or negative_price_duration_hours < 0

        or negative_price_duration_hours
            > (
                observed_interval_count
                * interval_minutes
                / 60.0
            )

        or minimum_price_eur_per_mwh
            > average_price_eur_per_mwh

        or average_price_eur_per_mwh
            > maximum_price_eur_per_mwh

)

select *
from invalid_rows
