{% test assert_chronological_dates(model, start_date_col, end_date_col) %}
select
    {{ start_date_col }},
    {{ end_date_col }}
from {{ model }}
where {{ start_date_col }} is not null
  and {{ end_date_col }} is not null
  and {{ end_date_col }} < {{ start_date_col }}
{% endtest %}
