with duplicates as (

    select
        bidding_zone,
        classification_sequence_position,
        delivery_date,
        count(*) as row_count
    from {{ ref('agg_daily_day_ahead_prices') }}
    group by
        bidding_zone,
        classification_sequence_position,
        delivery_date
    having count(*) > 1

)

select *
from duplicates
