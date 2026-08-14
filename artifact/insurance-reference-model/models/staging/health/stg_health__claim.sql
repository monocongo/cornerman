select
    claim_id,
    member_id,
    provider_id,
    service_date::date as service_date,
    claim_received_date::date as claim_received_date,
    claim_type
from {{ ref('health_claim') }}
