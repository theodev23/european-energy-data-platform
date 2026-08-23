with prices as (
    select *
    from {{ ref('stg_entsoe__day_ahead_prices') }}
),

ranked as (
    select
        *,
        row_number() over (
            partition by
                source_object_name,
                document_id,
                in_domain,
                out_domain,
                auction_type,
                business_type,
                contract_market_agreement_type,
                point_timestamp
            order by time_series_id
        ) as duplicate_rank
    from prices
),

deduplicated as (
    select
        source_object_name,
        document_id,
        document_type,
        revision_number,
        document_created_at,
        time_series_id,
        auction_type,
        business_type,
        in_domain,
        out_domain,
        contract_market_agreement_type,
        currency_unit,
        price_unit,
        curve_type,
        period_start,
        period_end,
        resolution,
        position,
        point_timestamp,
        price_amount
    from ranked
    where duplicate_rank = 1
)

select *
from deduplicated
