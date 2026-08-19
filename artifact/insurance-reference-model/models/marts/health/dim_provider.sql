-- Grain: one row per provider per network-status-effective period. SCD2-shaped -- see
-- ADR-0001 for why this is a regular model rather than a dbt snapshot.
select
    ns.network_status_id,
    ns.provider_id,
    p.npi::varchar as npi,
    p.provider_name,
    p.specialty,
    p.provider_type,
    ns.network_status,
    ns.effective_date as valid_from,
    ns.end_date as valid_to,
    (
        current_date >= ns.effective_date
        and (ns.end_date is null or current_date < ns.end_date)
    ) as is_current
from {{ ref('stg_health__provider_network_status') }} ns
join {{ ref('stg_health__provider') }} p on ns.provider_id = p.provider_id
