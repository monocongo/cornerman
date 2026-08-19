select
    party_id,
    first_name,
    last_name,
    date_of_birth::date as date_of_birth,
    ssn,
    credit_score::integer as credit_score,
    state,
    created_date::date as created_date
from {{ ref('pnc_party') }}
