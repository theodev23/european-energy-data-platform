{{
    config(
        partition_by={
            "field": "observation_date",
            "data_type": "date",
            "granularity": "day",
        },
        cluster_by=[
            "bidding_zone",
            "psr_type",
            "domain_direction",
        ],
    )
}}

with generation as (

    select *
    from {{ ref('fct_generation_by_type') }}

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
    from generation

),

daily as (

    select
        bidding_zone,
        date(point_timestamp) as observation_date,
        psr_type,
        domain_direction,
        quantity_unit,
        resolution,
        interval_minutes,
        count(*) as observed_interval_count,
        cast(
            1440 / interval_minutes
            as int64
        ) as expected_interval_count,
        avg(generation_quantity) as average_generation_mw,
        min(generation_quantity) as minimum_generation_mw,
        max(generation_quantity) as maximum_generation_mw,
        array_agg(
            point_timestamp
            order by
                generation_quantity desc,
                point_timestamp asc
            limit 1
        )[safe_offset(0)] as peak_generation_timestamp,
        sum(
            generation_quantity
            * interval_minutes
            / 60.0
        ) as observed_energy_mwh
    from with_interval_minutes
    group by
        bidding_zone,
        observation_date,
        psr_type,
        domain_direction,
        quantity_unit,
        resolution,
        interval_minutes

),

final as (

    select
        *,
        safe_divide(
            observed_interval_count,
            expected_interval_count
        ) as coverage_ratio,
        observed_interval_count = expected_interval_count
            as is_complete_observation_day
    from daily

)

select *
from final
