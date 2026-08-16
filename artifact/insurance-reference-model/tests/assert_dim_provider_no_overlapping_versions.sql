-- as_of_join (macros/as_of_join.sql) assumes at most one dim_provider row is valid for a given
-- provider_id at any point in time. Nothing else in the project enforces that; an overlap would
-- silently fan out every fact joined through this dimension.
select a.provider_id, a.valid_from as a_valid_from, a.valid_to as a_valid_to, b.valid_from as b_valid_from, b.valid_to as b_valid_to
from {{ ref('dim_provider') }} a
join {{ ref('dim_provider') }} b
    on a.provider_id = b.provider_id
    and a.network_status_id < b.network_status_id
    and a.valid_from < coalesce(b.valid_to, '9999-12-31')
    and coalesce(a.valid_to, '9999-12-31') > b.valid_from
