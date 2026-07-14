select
    recorded_at,
    messages_processed,
    elapsed_seconds,
    messages_per_second,
    messages_per_minute,

    avg(messages_per_second) over (
        order by recorded_at
        rows between 10 preceding and current row
    ) as rolling_avg_messages_per_second

from {{ ref('stg_pipeline_metrics') }}

order by recorded_at