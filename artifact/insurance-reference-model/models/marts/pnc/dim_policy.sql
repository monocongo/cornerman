-- Grain: one row per policy per endorsement-effective period (policy_version_id).
-- SCD2-shaped: valid_from/valid_to define the effective window; is_current flags the latest
-- version per policy. Built as a regular model reading pre-versioned staging data rather than
-- dbt's native `snapshot` resource -- see ADR-0001 for why.
select
    pv.policy_version_id,
    pv.policy_id,
    p.policy_number,
    p.line_of_business,
    p.status as policy_status,
    pv.version_number,
    pv.change_reason,
    pv.term_premium_amount,
    pv.garaging_state,
    pv.effective_date as valid_from,
    pv.expiration_date as valid_to,
    (
        pv.expiration_date = (
            select max(pv2.expiration_date)
            from {{ ref('stg_pnc__policy_version') }} pv2
            where pv2.policy_id = pv.policy_id
        )
    ) as is_current
from {{ ref('stg_pnc__policy_version') }} pv
join {{ ref('stg_pnc__policy') }} p on pv.policy_id = p.policy_id
