select
    date_trunc('hour', received_at) as hour,
    count(*) as messages_processed,
    count(distinct route_id) as active_routes,
    count(distinct stop_id) as active_stops,
    count(distinct trip_id) as active_trips

from {{ ref('stg_train_updates') }}

group by 1
order by 1