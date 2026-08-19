select
    policy_version_id,
    policy_id,
    version_number::integer as version_number,
    change_reason,
    effective_date::date as effective_date,
    expiration_date::date as expiration_date,
    term_premium_amount::decimal(10, 2) as term_premium_amount,
    garaging_state
from {{ ref('pnc_policy_version') }}
