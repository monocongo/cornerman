-- Grain: one row per claim. The policy version in effect is resolved as of loss_date via
-- as_of_join, not stored directly on the claim -- this is what demonstrates joining an SCD2
-- dimension on effective date rather than on is_current.
with claims as (
    select * from {{ ref('stg_pnc__claim') }}
)

select
    c.claim_id,
    c.policy_id,
    c.claimant_party_id,
    c.loss_date,
    c.report_date,
    datediff('day', c.loss_date, c.report_date) as report_lag_days,
    c.loss_type,
    c.status,
    c.catastrophe_flag,
    dp.policy_version_id as policy_version_id_at_loss,
    dp.policy_number,
    dp.garaging_state as garaging_state_at_loss
from claims c
{{ as_of_join('c', 'loss_date', ref('dim_policy'), 'dp', ['policy_id']) }}
