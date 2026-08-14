select
    network_status_id,
    provider_id,
    network_status,
    effective_date::date as effective_date,
    nullif(end_date, '')::date as end_date
from {{ ref('health_provider_network_status') }}
