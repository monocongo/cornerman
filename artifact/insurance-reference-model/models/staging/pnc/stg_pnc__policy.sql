select
    policy_id,
    policy_number,
    line_of_business,
    original_effective_date::date as original_effective_date,
    current_term_start::date as current_term_start,
    current_term_end::date as current_term_end,
    status
from {{ ref('pnc_policy') }}
