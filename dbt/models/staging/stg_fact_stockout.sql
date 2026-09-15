-- Staging model for FactStockout
select
    cast(StockoutEventKey as int64) as stockout_event_key,
    cast(StartDateKey as int64) as start_date_key,
    cast(EndDateKey as int64) as end_date_key,
    cast(StartDate as date) as start_date,
    cast(EndDate as date) as end_date,
    cast(ProductKey as int64) as product_key,
    trim(cast(ProductSKU as string)) as product_sku,
    cast(WarehouseKey as int64) as warehouse_key,
    cast(StockoutDurationDays as int64) as stockout_duration_days,
    cast(EstimatedLostDemandUnits as int64) as estimated_lost_demand_units,
    round(cast(EstimatedLostRevenueAmount as numeric), 2) as estimated_lost_revenue_amount,
    trim(cast(StockoutAttributedReason as string)) as stockout_attributed_reason,
    trim(cast(SeverityTier as string)) as severity_tier
from {{ source('raw_supply_chain', 'raw_fact_stockout') }}
