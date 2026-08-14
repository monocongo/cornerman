select
    policy_party_role_id,
    party_id,
    policy_id,
    claim_id,
    role_type,
    effective_date,
    end_date
from {{ ref('pnc_policy_party_role') }}
