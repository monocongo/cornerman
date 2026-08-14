select
    policy_party_role_id,
    party_id,
    nullif(policy_id, '') as policy_id,
    nullif(claim_id, '') as claim_id,
    role_type,
    effective_date::date as effective_date,
    nullif(end_date, '')::date as end_date
from {{ ref('pnc_policy_party_role') }}
