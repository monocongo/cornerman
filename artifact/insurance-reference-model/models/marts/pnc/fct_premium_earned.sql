-- Grain: one row per policy, per coverage, per day of accrual. Finance-facing; carries no PII --
-- enforced by tests/assert_fct_premium_earned_excludes_pii.sql, not a comment.
-- This is a window-expansion accrual fact, not an as_of_join usage: it generates one row per
-- calendar day directly from dim_policy/dim_coverage's own valid_from/valid_to windows, rather
-- than joining an independently-dated fact row to those dimensions. Still never joins on
-- is_current -- the windows themselves drive which days belong to which coverage.
with policy_days as (
    select
        dp.policy_id,
        dp.policy_version_id,
        dp.term_premium_amount,
        dp.valid_from,
        dp.valid_to,
        d.date_day
    from {{ ref('dim_policy') }} dp
    join {{ ref('dim_date') }} d
        on d.date_day >= dp.valid_from
        and d.date_day < dp.valid_to
        and d.date_day <= current_date
),

coverage_counts as (
    select policy_version_id, count(*) as n_coverages
    from {{ ref('dim_coverage') }}
    group by 1
),

daily_by_coverage as (
    select
        pd.policy_id,
        pd.date_day,
        dc.coverage_type,
        pd.term_premium_amount / cc.n_coverages
            / datediff('day', pd.valid_from, pd.valid_to) as earned_premium_amount
    from policy_days pd
    join {{ ref('dim_coverage') }} dc on dc.policy_version_id = pd.policy_version_id
    join coverage_counts cc on cc.policy_version_id = pd.policy_version_id
)

select
    policy_id,
    date_day as accrual_date,
    coverage_type,
    cast(round(sum(earned_premium_amount), 2) as decimal(18, 2)) as earned_premium_amount
from daily_by_coverage
group by 1, 2, 3
