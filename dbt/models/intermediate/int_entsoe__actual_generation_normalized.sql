with generation as (
    select *
    from {{ ref('stg_entsoe__actual_generation') }}
),

normalized as (
    select
        source_object_name,
        document_id,
        document_type,
        revision_number,
        document_created_at,
        process_type,
        time_series_id,
        business_type,
        object_aggregation,
        in_bidding_zone,
        out_bidding_zone,
        coalesce(in_bidding_zone, out_bidding_zone) as bidding_zone,
        case
            when
                in_bidding_zone is not null
                and out_bidding_zone is null
                then 'in'
            when
                in_bidding_zone is null
                and out_bidding_zone is not null
                then 'out'
            when
                in_bidding_zone is not null
                and out_bidding_zone is not null
                then 'both'
            else 'none'
        end as domain_direction,
        quantity_unit,
        curve_type,
        psr_type,
        period_start,
        period_end,
        resolution,
        position,
        point_timestamp,
        generation_quantity
    from generation
)

select *
from normalized
