with generation as (

    select *
    from {{ ref('int_entsoe__actual_generation_normalized') }}

),

ranked as (

    select
        *,
        row_number() over (
            partition by
                bidding_zone,
                psr_type,
                domain_direction,
                point_timestamp
            order by
                safe_cast(revision_number as int64) desc,
                document_created_at desc,
                source_object_name desc,
                document_id desc,
                time_series_id desc
        ) as canonical_rank
    from generation

),

canonical as (

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
        bidding_zone,
        domain_direction,
        quantity_unit,
        curve_type,
        psr_type,
        period_start,
        period_end,
        resolution,
        position,
        point_timestamp,
        generation_quantity
    from ranked
    where canonical_rank = 1

)

select *
from canonical
