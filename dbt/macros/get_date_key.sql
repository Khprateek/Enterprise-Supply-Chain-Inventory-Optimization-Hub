{% macro get_date_key(date_field) %}
    cast(format_date('%Y%m%d', {{ date_field }}) as int64)
{% endmacro %}
