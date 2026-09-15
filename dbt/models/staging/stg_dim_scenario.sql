-- Staging model for DimScenario
select
    cast(ScenarioKey as int64) as scenario_key,
    trim(cast(ScenarioCode as string)) as scenario_code,
    trim(cast(ScenarioName as string)) as scenario_name,
    trim(cast(Description as string)) as scenario_description,
    round(cast(DemandMultiplier as numeric), 2) as demand_multiplier,
    cast(LeadTimeShockDays as int64) as lead_time_shock_days,
    round(cast(ServiceLevelTargetPct as numeric), 2) as service_level_target_pct,
    round(cast(AnnualCarryingCostRatePct as numeric), 2) as annual_carrying_cost_rate_pct
from {{ source('raw_supply_chain', 'raw_dim_scenario') }}
