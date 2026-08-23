with duplicates as (

    select
        bidding_zone,
        psr_type,
        domain_direction,
        point_timestamp,
        count(*) as row_count
    from {{ ref('int_entsoe__actual_generation_canonical') }}
    group by
        bidding_zone,
        psr_type,
        domain_direction,
        point_timestamp
    having count(*) > 1

)

select *
from duplicates
