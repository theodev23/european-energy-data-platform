with duplicates as (

    select
        bidding_zone,
        observation_date,
        count(*) as row_count
    from {{ ref('agg_daily_load') }}
    group by
        bidding_zone,
        observation_date
    having count(*) > 1

)

select *
from duplicates
