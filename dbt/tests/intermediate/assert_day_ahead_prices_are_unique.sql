with duplicates as (
    select
        source_object_name,
        document_id,
        in_domain,
        out_domain,
        auction_type,
        business_type,
        contract_market_agreement_type,
        point_timestamp,
        count(*) as row_count
    from {{ ref('int_entsoe__day_ahead_prices_deduplicated') }}
    group by
        source_object_name,
        document_id,
        in_domain,
        out_domain,
        auction_type,
        business_type,
        contract_market_agreement_type,
        point_timestamp
    having count(*) > 1
)

select *
from duplicates
