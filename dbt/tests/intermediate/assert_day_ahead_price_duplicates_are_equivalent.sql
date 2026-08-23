with grouped as (
    select
        source_object_name,
        document_id,
        in_domain,
        out_domain,
        auction_type,
        business_type,
        contract_market_agreement_type,
        point_timestamp,
        count(*) as row_count,
        count(
            distinct to_json_string(
                struct(
                    document_type,
                    revision_number,
                    document_created_at,
                    currency_unit,
                    price_unit,
                    curve_type,
                    period_start,
                    period_end,
                    resolution,
                    position,
                    price_amount
                )
            )
        ) as payload_variant_count
    from {{ ref('stg_entsoe__day_ahead_prices') }}
    group by
        source_object_name,
        document_id,
        in_domain,
        out_domain,
        auction_type,
        business_type,
        contract_market_agreement_type,
        point_timestamp
)

select *
from grouped
where
    row_count > 1
    and payload_variant_count > 1
