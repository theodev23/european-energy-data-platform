with duplicates as (

    select
        in_domain,
        point_timestamp,
        count(*) as row_count
    from {{ ref('int_entsoe__day_ahead_prices_canonical') }}
    group by
        in_domain,
        point_timestamp
    having count(*) > 1

)

select *
from duplicates
