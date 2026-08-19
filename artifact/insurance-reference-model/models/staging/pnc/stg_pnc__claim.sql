select
    claim_id,
    policy_id,
    claimant_party_id,
    loss_date::date as loss_date,
    report_date::date as report_date,
    loss_type,
    status,
    catastrophe_flag::boolean as catastrophe_flag
from {{ ref('pnc_claim') }}
