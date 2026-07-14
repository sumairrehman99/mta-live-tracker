select
    route_id,
    count(*) as total_updates,
    count(distinct trip_id) as unique_trips,
    count(distinct stop_id) as unique_stops,
    min(received_at) as first_update_time,
    max(received_at) as last_update_time,
    round(
        count(*)::numeric / nullif(count(distinct trip_id), 0),
        2
    ) as avg_updates_per_trip


from {{ ref('stg_train_updates') }}

group by route_id