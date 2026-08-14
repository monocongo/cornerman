select
    claim_transaction_id,
    claim_id,
    coverage_id,
    transaction_type,
    booked_date::date as booked_date,
    amount::decimal(12, 2) as amount
from {{ ref('pnc_claim_transaction') }}
