-- Paid loss triangle: cumulative paid amount by accident quarter x development month. A
-- textbook actuarial view, produced entirely by a GROUP BY over fct_claim_transaction --
-- no bespoke snapshot pipeline required, because the ledger already carries every payment
-- event at its own booked_date.
with paid_transactions as (
    select
        date_trunc('quarter', c.loss_date) as accident_period,
        datediff('month', date_trunc('quarter', c.loss_date), ct.booked_date) as development_month,
        case when ct.transaction_type = 'payment_issued' then ct.amount
             when ct.transaction_type = 'payment_voided' then -ct.amount
             else 0 end as paid_amount
    from {{ ref('fct_claim_transaction') }} ct
    join {{ ref('fct_claim') }} c on ct.claim_id = c.claim_id
    where ct.transaction_type in ('payment_issued', 'payment_voided')
),

by_period as (
    select accident_period, development_month, sum(paid_amount) as period_paid_amount
    from paid_transactions
    group by 1, 2
)

select
    accident_period,
    development_month,
    sum(period_paid_amount) over (
        partition by accident_period order by development_month
        rows between unbounded preceding and current row
    ) as cumulative_paid_amount
from by_period
order by accident_period, development_month
