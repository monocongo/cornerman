select
    provider_id,
    npi,
    provider_name,
    specialty,
    provider_type
from {{ ref('health_provider') }}
