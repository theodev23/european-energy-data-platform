with load as (

    select *
    from {{ ref('stg_entsoe__actual_load') }}

),

ranked as (

    select
        *,
        row_number() over (
            partition by
                bidding_zone,
                point_timestamp
            order by
                safe_cast(revision_number as int64) desc,
                document_created_at desc,
                source_object_name desc,
                document_id desc,
                time_series_id desc
        ) as canonical_rank
    from load

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
        bidding_zone,
        quantity_unit,
        curve_type,
        period_start,
        period_end,
        resolution,
        position,
        point_timestamp,
        load_quantity
    from ranked
    where canonical_rank = 1

)

select *
from canonical
