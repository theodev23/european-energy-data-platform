with duplicates as (

    select
        bidding_zone,
        observation_date,
        psr_type,
        domain_direction,
        count(*) as row_count
    from {{ ref('agg_daily_generation_by_type') }}
    group by
        bidding_zone,
        observation_date,
        psr_type,
        domain_direction
    having count(*) > 1

)

select *
from duplicates
