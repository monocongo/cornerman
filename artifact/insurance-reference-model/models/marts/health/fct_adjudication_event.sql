-- Grain: one row per claim line, per status-transition event, per booked_date. Append-only
-- ledger: received, pended, approved, denied, paid, adjusted. Carries no diagnosis/procedure
-- codes or member PHI -- enforced by tests/assert_fct_adjudication_event_excludes_phi.sql.
select
    ae.adjudication_event_id,
    ae.claim_line_id,
    cl.claim_id,
    ae.event_type,
    ae.booked_date,
    ae.paid_amount,
    ae.denial_reason,
    cl.service_date
from {{ ref('stg_health__adjudication_event') }} ae
join {{ ref('stg_health__claim_line') }} cl on ae.claim_line_id = cl.claim_line_id
