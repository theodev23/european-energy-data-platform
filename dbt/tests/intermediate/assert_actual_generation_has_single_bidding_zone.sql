select *
from {{ ref('int_entsoe__actual_generation_normalized') }}
where
    (
        in_bidding_zone is null
        and out_bidding_zone is null
    )
    or (
        in_bidding_zone is not null
        and out_bidding_zone is not null
    )
