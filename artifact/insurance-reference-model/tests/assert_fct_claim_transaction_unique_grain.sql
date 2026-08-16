select claim_id, coverage_id, transaction_type, booked_date, count(*) as row_count
from {{ ref('fct_claim_transaction') }}
group by 1, 2, 3, 4
having count(*) > 1
