-- Materialized Scorecard Mart: FactSupplierMonthlyPerformance
{{ config(
    materialized='table',
    cluster_by=['supplier_key']
) }}

with po_completed as (
    select
        supplier_key,
        po_creation_date,
        format_date('%Y-%m', po_creation_date) as year_month,
        purchase_order_id,
        ordered_quantity,
        received_quantity,
        rejected_quantity,
        extended_po_amount,
        is_delivered_on_time_flag,
        is_delivered_in_full_flag,
        is_supplier_otif_flag,
        actual_lead_time_days
    from {{ ref('stg_fact_purchase_order') }}
    where po_status = 'Completed'
),
monthly_agg as (
    select
        supplier_key,
        year_month,
        min(po_creation_date) as month_start_date,
        count(distinct purchase_order_id) as total_po_count,
        count(*) as total_po_lines,
        sum(ordered_quantity) as total_ordered_quantity,
        sum(received_quantity) as total_received_quantity,
        sum(rejected_quantity) as total_rejected_quantity,
        round(sum(extended_po_amount), 2) as total_spend_amount,
        sum(is_delivered_on_time_flag) as on_time_po_count,
        sum(is_delivered_in_full_flag) as in_full_po_count,
        sum(is_supplier_otif_flag) as otif_line_count,
        count(*) - sum(is_delivered_on_time_flag) as late_delivery_count,
        round(avg(actual_lead_time_days), 2) as average_lead_time_days,
        round(coalesce(stddev_samp(actual_lead_time_days), 0.5), 2) as lead_time_std_dev_days
    from po_completed
    group by supplier_key, year_month
)
select
    row_number() over(order by supplier_key, year_month) as supplier_monthly_key,
    cast(format_date('%Y%m01', month_start_date) as int64) as year_month_date_key,
    parse_date('%Y-%m-%d', concat(year_month, '-01')) as year_month_date,
    supplier_key,
    year_month,
    total_po_count,
    total_po_lines,
    total_ordered_quantity,
    total_received_quantity,
    total_rejected_quantity,
    total_spend_amount,
    on_time_po_count,
    in_full_po_count,
    otif_line_count,
    round(safe_divide(otif_line_count * 100.0, total_po_lines), 2) as otif_rate_pct,
    average_lead_time_days,
    lead_time_std_dev_days,
    late_delivery_count,
    round(safe_divide(total_received_quantity * 100.0, total_ordered_quantity), 2) as line_fill_rate_pct,
    case
        when safe_divide(otif_line_count * 100.0, total_po_lines) >= 90.0 and lead_time_std_dev_days <= 3.0 then 'Low Risk (Compliant)'
        when safe_divide(otif_line_count * 100.0, total_po_lines) >= 78.0 then 'Moderate Risk (Watchlist)'
        else 'Critical SLA Breach'
    end as supplier_monthly_risk_rating
from monthly_agg
