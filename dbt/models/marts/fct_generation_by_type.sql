{{
    config(
        partition_by={
            "field": "point_timestamp",
            "data_type": "timestamp",
            "granularity": "day",
        },
        cluster_by=["bidding_zone", "psr_type", "domain_direction"],
    )
}}

with generation as (
    select *
    from {{ ref('int_entsoe__actual_generation_normalized') }}
),

final as (
    select
        source_object_name,
        document_id,
        time_series_id,
        bidding_zone,
        domain_direction,
        psr_type,
        point_timestamp,
        generation_quantity,
        quantity_unit,
        resolution
    from generation
)

select *
from final
