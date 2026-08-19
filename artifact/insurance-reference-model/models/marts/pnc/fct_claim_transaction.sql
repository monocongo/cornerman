-- Grain: one row per claim, per coverage, per transaction, per booked_date. Append-only ledger:
-- reserve_set, reserve_change, payment_issued, payment_voided, reopened. This is the fact a loss
-- triangle GROUP BY runs against -- current claim status/reserve is never stored separately from
-- this ledger.
select
    ct.claim_transaction_id,
    ct.claim_id,
    ct.coverage_id,
    dc.coverage_type,
    dc.policy_id,
    ct.transaction_type,
    ct.booked_date,
    ct.amount,
    c.loss_date,
    c.report_date
from {{ ref('stg_pnc__claim_transaction') }} ct
join {{ ref('dim_coverage') }} dc on ct.coverage_id = dc.coverage_id
join {{ ref('stg_pnc__claim') }} c on ct.claim_id = c.claim_id
