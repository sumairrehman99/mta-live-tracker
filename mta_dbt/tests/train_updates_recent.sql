select
    max(received_at) as latest_update
from {{ ref('stg_train_updates') }}
having max(received_at) < now() - interval '30 minutes'