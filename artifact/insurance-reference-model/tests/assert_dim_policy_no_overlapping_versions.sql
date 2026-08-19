-- as_of_join (macros/as_of_join.sql) assumes at most one dim_policy row is valid for a given
-- policy_id at any point in time. Nothing else in the project enforces that; an overlap would
-- silently fan out every fact joined through this dimension.
select a.policy_id, a.valid_from as a_valid_from, a.valid_to as a_valid_to, b.valid_from as b_valid_from, b.valid_to as b_valid_to
from {{ ref('dim_policy') }} a
join {{ ref('dim_policy') }} b
    on a.policy_id = b.policy_id
    and a.policy_version_id < b.policy_version_id
    and a.valid_from < coalesce(b.valid_to, '9999-12-31')
    and coalesce(a.valid_to, '9999-12-31') > b.valid_from
