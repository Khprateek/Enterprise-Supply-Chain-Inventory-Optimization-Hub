-- Staging model for FactDemandForecast
select
    cast(ForecastKey as int64) as forecast_key,
    cast(TargetPeriodDate as date) as target_period_date,
    cast(ForecastGeneratedDate as date) as forecast_generated_date,
    cast(TargetPeriodDateKey as int64) as target_period_date_key,
    cast(ForecastGeneratedDateKey as int64) as forecast_generated_date_key,
    cast(ProductKey as int64) as product_key,
    trim(cast(ProductSKU as string)) as product_sku,
    cast(WarehouseKey as int64) as warehouse_key,

    cast(ScenarioKey as int64) as scenario_key,
    cast(ForecastedQuantity as int64) as forecasted_quantity,
    cast(BaselineStatisticalQuantity as int64) as baseline_statistical_quantity,
    cast(PlannerAdjustmentQuantity as int64) as planner_adjustment_quantity,
    round(cast(ForecastValue as numeric), 2) as forecast_value
from {{ source('raw_supply_chain', 'raw_fact_demand_forecast') }}
