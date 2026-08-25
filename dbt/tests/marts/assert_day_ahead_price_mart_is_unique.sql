with duplicates as (
    select
        bidding_zone,
        classification_sequence_position,
        point_timestamp,
        count(*) as row_count
    from {{ ref('fct_day_ahead_prices') }}
    group by
        bidding_zone,
        classification_sequence_position,
        point_timestamp
    having count(*) > 1
)

select *
from duplicates
