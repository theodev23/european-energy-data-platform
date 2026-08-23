select *
from {{ ref('int_entsoe__day_ahead_prices_deduplicated') }}
where in_domain != out_domain
