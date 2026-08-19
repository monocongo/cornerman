-- Development triangle for claim-line adjudication: cumulative paid amount by service quarter x
-- development month (months from service_date to booked_date of each paid/adjusted event). Same
-- GROUP BY pattern as the P&C loss triangle, run against fct_adjudication_event instead of
-- fct_claim_transaction -- but 'adjusted' events restate the claim line's total paid amount
-- (a correction/clawback per the domain pack), they don't add a second full payment on top of
-- 'paid'. So each event's contribution is the incremental change versus that claim line's prior
-- paid_amount, not its raw paid_amount -- otherwise a clawback would double-count instead of net.
with paid_and_adjusted as (
    select
        claim_line_id,
        service_date,
        booked_date,
        paid_amount - coalesce(
            lag(paid_amount) over (partition by claim_line_id order by booked_date),
            0
        ) as incremental_paid_amount
    from {{ ref('fct_adjudication_event') }}
    where event_type in ('paid', 'adjusted')
),

by_period as (
    select
        date_trunc('quarter', service_date) as service_period,
        datediff('month', date_trunc('quarter', service_date), booked_date) as development_month,
        sum(incremental_paid_amount) as period_paid_amount
    from paid_and_adjusted
    group by 1, 2
)

select
    service_period,
    development_month,
    sum(period_paid_amount) over (
        partition by service_period order by development_month
        rows between unbounded preceding and current row
    ) as cumulative_paid_amount
from by_period
order by service_period, development_month
