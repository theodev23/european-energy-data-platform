with source as (
    select *
    from {{ source('entsoe_raw', 'day_ahead_prices') }}
),

renamed as (
    select
        source_object_name,
        document_mrid as document_id,
        document_type,
        revision_number,
        document_created_at,
        time_series_mrid as time_series_id,
        auction_type,
        business_type,
        in_domain,
        out_domain,
        contract_market_agreement_type,
        currency_unit,
        price_unit,
        classification_sequence_position,
        curve_type,
        period_start,
        period_end,
        resolution,
        position,
        point_timestamp,
        price_amount
    from source
)

select *
from renamed
