-- Grain: one row per claim line, as submitted (billed amount, service date, procedure/diagnosis
-- codes). Does not store current adjudication state -- see fct_adjudication_event. Network
-- status and benefit plan are resolved as of service_date via as_of_join, demonstrating the
-- domain's core temporal trap: "as of service date," not "as of today."
with claim_lines as (
    select
        cl.claim_line_id,
        cl.claim_id,
        cl.line_number,
        cl.procedure_code,
        cl.diagnosis_code,
        cl.billed_amount,
        cl.service_date,
        c.member_id,
        c.provider_id,
        c.claim_type
    from {{ ref('stg_health__claim_line') }} cl
    join {{ ref('stg_health__claim') }} c on cl.claim_id = c.claim_id
)

select
    cl.claim_line_id,
    cl.claim_id,
    cl.line_number,
    cl.procedure_code,
    cl.diagnosis_code,
    cl.billed_amount,
    cl.service_date,
    cl.member_id,
    cl.provider_id,
    cl.claim_type,
    dp.network_status as provider_network_status_at_service,
    es.benefit_plan_id as benefit_plan_id_at_service,
    bp.plan_type as benefit_plan_type_at_service
from claim_lines cl
{{ as_of_join('cl', 'service_date', ref('dim_provider'), 'dp', ['provider_id']) }}
{{ as_of_join('cl', 'service_date', ref('fct_eligibility_span'), 'es', ['member_id'], valid_from_column='start_date', valid_to_column='end_date') }}
left join {{ ref('dim_benefit_plan') }} bp on es.benefit_plan_id = bp.benefit_plan_id
