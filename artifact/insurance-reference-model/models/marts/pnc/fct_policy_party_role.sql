-- Grain: one row per party, per policy or claim, per role.
select
    policy_party_role_id,
    party_id,
    policy_id,
    claim_id,
    role_type,
    effective_date,
    end_date
from {{ ref('stg_pnc__policy_party_role') }}
