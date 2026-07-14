select
    stop_id,
    max(stop_name) as stop_name,
    count(*) as total_updates,
    count(distinct route_id) as unique_routes,
    count(distinct trip_id) as unique_trips,
    min(received_at) as first_update_time,
    max(received_at) as last_update_time

from {{ ref('stg_train_updates') }}

group by stop_id