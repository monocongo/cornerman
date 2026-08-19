select
    benefit_plan_id,
    plan_name,
    plan_year::integer as plan_year,
    effective_date::date as effective_date,
    expiration_date::date as expiration_date,
    plan_type,
    deductible_individual::decimal(10, 2) as deductible_individual,
    oop_max_individual::decimal(10, 2) as oop_max_individual
from {{ ref('health_benefit_plan') }}
