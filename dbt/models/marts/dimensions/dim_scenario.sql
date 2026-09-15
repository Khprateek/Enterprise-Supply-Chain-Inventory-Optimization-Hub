-- Conformed Dimension: DimScenario (Parameter Reference)
{{ config(materialized='table') }}

select
    scenario_key,
    scenario_code,
    scenario_name,
    scenario_description,
    demand_multiplier,
    lead_time_shock_days,
    service_level_target_pct,
    annual_carrying_cost_rate_pct
from {{ ref('stg_dim_scenario') }}
