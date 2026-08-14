select
    claim_line_id,
    claim_id,
    line_number::integer as line_number,
    procedure_code,
    diagnosis_code,
    billed_amount::decimal(10, 2) as billed_amount,
    service_date::date as service_date
from {{ ref('health_claim_line') }}
