with prices as (

    select *
    from {{ ref('int_entsoe__day_ahead_prices_deduplicated') }}

),

ranked as (

    select
        *,
        row_number() over (
            partition by
                in_domain,
                point_timestamp
            order by
                safe_cast(revision_number as int64) desc,
                document_created_at desc,
                source_object_name desc,
                document_id desc,
                time_series_id desc
        ) as canonical_rank
    from prices

),

canonical as (

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
    where canonical_rank = 1

)

select *
from canonical
