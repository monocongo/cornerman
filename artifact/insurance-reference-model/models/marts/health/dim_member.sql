-- Grain: one row per member, current attributes only.
select
    member_id,
    first_name,
    last_name,
    date_of_birth,
    gender,
    subscriber_id,
    relationship_to_subscriber,
    state
from {{ ref('stg_health__member') }}
