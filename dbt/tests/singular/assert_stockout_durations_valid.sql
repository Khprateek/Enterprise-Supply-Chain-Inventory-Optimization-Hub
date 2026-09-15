-- Singular test: Ensure stockout outage durations are strictly positive
select
    stockout_event_key,
    stockout_duration_days
from {{ ref('fact_stockout') }}
where stockout_duration_days <= 0
