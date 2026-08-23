with duplicates as (
    select
        bidding_zone,
        psr_type,
        point_timestamp,
        count(*) as row_count
    from {{ ref('fct_generation_by_type') }}
    group by
        bidding_zone,
        psr_type,
        point_timestamp
    having count(*) > 1
)

select *
from duplicates
