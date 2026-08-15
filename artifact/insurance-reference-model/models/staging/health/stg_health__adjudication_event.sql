select
    adjudication_event_id,
    claim_line_id,
    event_type,
    booked_date::date as booked_date,
    nullif(paid_amount::varchar, '')::decimal(10, 2) as paid_amount,
    nullif(denial_reason, '') as denial_reason
from {{ ref('health_adjudication_event') }}
