with duplicates as (

    select
        bidding_zone,
        point_timestamp,
        count(*) as row_count
    from {{ ref('int_entsoe__actual_load_canonical') }}
    group by
        bidding_zone,
        point_timestamp
    having count(*) > 1

)

select *
from duplicates
