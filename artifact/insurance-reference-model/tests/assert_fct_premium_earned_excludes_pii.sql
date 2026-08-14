-- Fails if fct_premium_earned ever gains a column that carries PII. Enforces the boundary as a
-- test, not a comment: any future join that accidentally pulls party attributes onto this
-- finance-facing fact breaks the build.
{% set relation = ref('fct_premium_earned') %}
{% set forbidden_columns = ['ssn', 'credit_score', 'first_name', 'last_name', 'date_of_birth'] %}
{% set actual_columns = adapter.get_columns_in_relation(relation) | map(attribute='name') | map('lower') | list %}
{% set leaked_columns = forbidden_columns | select('in', actual_columns) | list %}

{% if leaked_columns | length > 0 %}
select column_name
from (values {% for c in leaked_columns %}('{{ c }}'){% if not loop.last %}, {% endif %}{% endfor %}) as t(column_name)
{% else %}
select 'no_leak' as column_name where false
{% endif %}
