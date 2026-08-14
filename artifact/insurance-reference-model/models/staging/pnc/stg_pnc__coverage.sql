select
    coverage_id,
    policy_version_id,
    coverage_type,
    limit_amount::decimal(12, 2) as limit_amount,
    deductible_amount::decimal(10, 2) as deductible_amount
from {{ ref('pnc_coverage') }}
