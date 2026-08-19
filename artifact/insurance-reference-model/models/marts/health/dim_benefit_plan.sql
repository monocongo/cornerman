-- Grain: one row per plan per plan-year.
select
    b1.benefit_plan_id,
    b1.plan_name,
    b1.plan_year,
    b1.plan_type,
    b1.deductible_individual,
    b1.oop_max_individual,
    b1.effective_date as valid_from,
    b1.expiration_date as valid_to,
    (
        current_date >= b1.effective_date
        and (b1.expiration_date is null or current_date < b1.expiration_date)
    ) as is_current
from {{ ref('stg_health__benefit_plan') }} b1
