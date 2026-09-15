-- Intermediate model: Analyzes historical supplier lead times and OTIF compliance
with po as (
    select
        supplier_key,
        actual_lead_time_days,
        is_delivered_on_time_flag,
        is_delivered_in_full_flag,
        is_supplier_otif_flag
    from {{ ref('stg_fact_purchase_order') }}
    where po_status = 'Completed'
)
select
    supplier_key,
    count(*) as completed_po_lines,
    avg(actual_lead_time_days) as historical_avg_lead_time_days,
    stddev_samp(actual_lead_time_days) as historical_lead_time_stddev_days,
    avg(is_delivered_on_time_flag) as on_time_rate,
    avg(is_delivered_in_full_flag) as in_full_rate,
    avg(is_supplier_otif_flag) as otif_rate
from po
group by supplier_key
