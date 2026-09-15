-- Analytical Fact: FactDemandForecast (Consensus & Baseline Planning)
{{ config(
    materialized='table',
    partition_by={
        "field": "target_period_date",
        "data_type": "date",
        "granularity": "month"
    },
    cluster_by=['product_key', 'warehouse_key']
) }}

select
    forecast_key,
    target_period_date,
    forecast_generated_date,
    target_period_date_key,
    forecast_generated_date_key,
    product_key,
    warehouse_key,
    scenario_key,
    forecasted_quantity,
    baseline_statistical_quantity,
    planner_adjustment_quantity,
    forecast_value
from {{ ref('stg_fact_demand_forecast') }}
