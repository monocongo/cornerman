select claim_line_id, event_type, booked_date, count(*) as row_count
from {{ ref('fct_adjudication_event') }}
group by 1, 2, 3
having count(*) > 1
