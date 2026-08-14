-- Grain: one row per party, current attributes only.
select
    party_id,
    first_name,
    last_name,
    date_of_birth,
    ssn,
    credit_score,
    state
from {{ ref('stg_pnc__party') }}
