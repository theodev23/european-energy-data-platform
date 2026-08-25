{{
    config(
        partition_by={
            "field": "point_timestamp",
            "data_type": "timestamp",
            "granularity": "day",
        },
        cluster_by=["bidding_zone"],
    )
}}

with prices as (
    select *
    from {{ ref('int_entsoe__day_ahead_prices_canonical') }}
),

final as (
    select
        source_object_name,
        document_id,
        time_series_id,
        in_domain as bidding_zone,
        classification_sequence_position,
        auction_type,
        contract_market_agreement_type,
        period_start,
        period_end,
        point_timestamp,
        price_amount,
        currency_unit,
        price_unit,
        resolution
    from prices
)

select *
from final
