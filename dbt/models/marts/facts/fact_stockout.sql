-- Analytical Fact: FactStockout (Consolidated Outage Incidents)
{{ config(
    materialized='table',
    cluster_by=['product_key', 'warehouse_key']
) }}

select
    stockout_event_key,
    start_date_key,
    end_date_key,
    start_date,
    end_date,
    product_key,
    warehouse_key,
    stockout_duration_days,
    estimated_lost_demand_units,
    estimated_lost_revenue_amount,
    stockout_attributed_reason,
    severity_tier
from {{ ref('stg_fact_stockout') }}
