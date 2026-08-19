-- Grain: one row per member per continuous coverage span. Gaps (lapsed coverage) and
-- re-enrollment are represented naturally -- a member with no active span simply has no
-- currently-covering row, rather than a false "active" flag.
select
    eligibility_span_id,
    member_id,
    benefit_plan_id,
    start_date,
    end_date,
    span_reason,
    (
        current_date >= start_date
        and (end_date is null or current_date < end_date)
    ) as is_currently_active
from {{ ref('stg_health__eligibility_span') }}
