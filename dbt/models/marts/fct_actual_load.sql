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

with load as (
    select *
    from {{ ref('stg_entsoe__actual_load') }}
),

final as (
    select
        source_object_name,
        document_id,
        time_series_id,
        bidding_zone,
        point_timestamp,
        load_quantity,
        quantity_unit,
        resolution
    from load
)

select *
from final
