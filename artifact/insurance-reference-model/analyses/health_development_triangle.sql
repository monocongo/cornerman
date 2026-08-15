-- Development triangle for claim-line adjudication: cumulative paid amount by service quarter x
-- development month (months from service_date to booked_date of each 'paid' event). Same
-- GROUP BY pattern as the P&C loss triangle, run against fct_adjudication_event instead of
-- fct_claim_transaction.
with paid_events as (
    select
        date_trunc('quarter', service_date) as service_period,
        datediff('month', date_trunc('quarter', service_date), booked_date) as development_month,
        paid_amount
    from {{ ref('fct_adjudication_event') }}
    where event_type = 'paid'
),

by_period as (
    select service_period, development_month, sum(paid_amount) as period_paid_amount
    from paid_events
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
