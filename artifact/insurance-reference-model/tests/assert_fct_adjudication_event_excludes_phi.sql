-- Fails if fct_adjudication_event ever gains one of the columns listed below. Enforces the
-- boundary as a test, not a comment: a future join that accidentally pulls one of these known
-- diagnosis/procedure/member attributes onto this fact breaks the build. The list is a hardcoded
-- denylist (see ADR-0003) -- it catches regression of already-known-sensitive columns, not
-- detection of a newly introduced one that isn't in this list yet.
{% set relation = ref('fct_adjudication_event') %}
{% set forbidden_columns = ['diagnosis_code', 'procedure_code', 'first_name', 'last_name', 'date_of_birth', 'ssn', 'gender', 'subscriber_id'] %}
{% set actual_columns = adapter.get_columns_in_relation(relation) | map(attribute='name') | map('lower') | list %}
{% set leaked_columns = forbidden_columns | select('in', actual_columns) | list %}

{% if leaked_columns | length > 0 %}
select column_name
from (values {% for c in leaked_columns %}('{{ c }}'){% if not loop.last %}, {% endif %}{% endfor %}) as t(column_name)
{% else %}
select 'no_leak' as column_name where false
{% endif %}
