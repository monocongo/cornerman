select
    eligibility_span_id,
    member_id,
    benefit_plan_id,
    start_date::date as start_date,
    nullif(end_date::varchar, '')::date as end_date,
    span_reason
from {{ ref('health_eligibility_span') }}
