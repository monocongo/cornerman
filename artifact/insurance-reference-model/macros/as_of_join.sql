{% macro as_of_join(fact_alias, fact_date_column, dim_relation, dim_alias, key_columns, valid_from_column='valid_from', valid_to_column='valid_to') %}
left join {{ dim_relation }} as {{ dim_alias }}
    on {% for col in key_columns %}{{ fact_alias }}.{{ col }} = {{ dim_alias }}.{{ col }}{% if not loop.last %} and {% endif %}{% endfor %}

    and {{ fact_alias }}.{{ fact_date_column }} >= {{ dim_alias }}.{{ valid_from_column }}
    and ({{ fact_alias }}.{{ fact_date_column }} < {{ dim_alias }}.{{ valid_to_column }} or {{ dim_alias }}.{{ valid_to_column }} is null)
{% endmacro %}
