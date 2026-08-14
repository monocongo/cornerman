select policy_id, accrual_date, coverage_type, count(*) as row_count
from {{ ref('fct_premium_earned') }}
group by 1, 2, 3
having count(*) > 1
