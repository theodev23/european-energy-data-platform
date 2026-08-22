with source as (
    select *
    from {{ source('entsoe_raw', 'actual_load') }}
),

renamed as (
    select
        source_object_name,
        document_mrid as document_id,
        document_type,
        revision_number,
        document_created_at,
        process_type,
        time_series_mrid as time_series_id,
        business_type,
        object_aggregation,
        out_bidding_zone as bidding_zone,
        quantity_unit,
        curve_type,
        period_start,
        period_end,
        resolution,
        position,
        point_timestamp,
        quantity as load_quantity
    from source
)

select *
from renamed
