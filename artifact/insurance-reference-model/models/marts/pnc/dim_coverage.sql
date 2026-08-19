-- Grain: one row per policy version per coverage type (coverage_id). Inherits its policy
-- version's effective window.
select
    c.coverage_id,
    c.policy_version_id,
    dp.policy_id,
    c.coverage_type,
    c.limit_amount,
    c.deductible_amount,
    dp.valid_from,
    dp.valid_to,
    dp.is_current
from {{ ref('stg_pnc__coverage') }} c
join {{ ref('dim_policy') }} dp on c.policy_version_id = dp.policy_version_id
