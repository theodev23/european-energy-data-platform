{{
    config(
        partition_by={
            "field": "delivery_date",
            "data_type": "date",
            "granularity": "day",
        },
        cluster_by=["bidding_zone"],
    )
}}

with prices as (

    select *
    from {{ ref('fct_day_ahead_prices') }}

),

with_interval_minutes as (

    select
        *,
        case
            when regexp_contains(resolution, r'^PT[0-9]+M$')
                then cast(
                    regexp_extract(
                        resolution,
                        r'^PT([0-9]+)M$'
                    ) as int64
                )
            when regexp_contains(resolution, r'^PT[0-9]+H$')
                then 60 * cast(
                    regexp_extract(
                        resolution,
                        r'^PT([0-9]+)H$'
                    ) as int64
                )
        end as interval_minutes
    from prices

),

daily as (

    select
        bidding_zone,
        classification_sequence_position,
        date(period_end) as delivery_date,
        min(period_start) as period_start,
        max(period_end) as period_end,
        any_value(currency_unit) as currency_unit,
        any_value(price_unit) as price_unit,
        any_value(resolution) as resolution,
        min(interval_minutes) as interval_minutes,
        count(*) as observed_interval_count,
        cast(
            timestamp_diff(
                max(period_end),
                min(period_start),
                minute
            )
            / min(interval_minutes)
            as int64
        ) as expected_interval_count,
        avg(price_amount) as average_price_eur_per_mwh,
        min(price_amount) as minimum_price_eur_per_mwh,
        max(price_amount) as maximum_price_eur_per_mwh,
        countif(price_amount < 0) as negative_price_interval_count,
        sum(
            case
                when price_amount < 0
                    then interval_minutes / 60.0
                else 0
            end
        ) as negative_price_duration_hours
    from with_interval_minutes
    group by
        bidding_zone,
        classification_sequence_position,
        delivery_date

),

final as (

    select
        *,
        safe_divide(
            observed_interval_count,
            expected_interval_count
        ) as coverage_ratio,
        observed_interval_count = expected_interval_count
            as is_complete_delivery_day
    from daily

)

select *
from final
