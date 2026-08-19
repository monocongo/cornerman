select
    member_id,
    first_name,
    last_name,
    date_of_birth::date as date_of_birth,
    gender,
    subscriber_id,
    relationship_to_subscriber,
    state
from {{ ref('health_member') }}
