-- Grain: one row per authorization request. Its valid_from/valid_to window is independent of
-- both eligibility and service date.
select
    authorization_id,
    member_id,
    provider_id,
    service_type,
    requested_date,
    valid_from,
    valid_to,
    status
from {{ ref('stg_health__authorization') }}
