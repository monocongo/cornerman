select
    authorization_id,
    member_id,
    provider_id,
    service_type,
    requested_date::date as requested_date,
    valid_from::date as valid_from,
    valid_to::date as valid_to,
    status
from {{ ref('health_authorization') }}
