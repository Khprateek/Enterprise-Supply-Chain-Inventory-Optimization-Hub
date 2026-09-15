-- Staging model for FactInventorySnapshot
select
    cast(SnapshotKey as int64) as snapshot_key,
    cast(SnapshotDate as date) as snapshot_date,
    cast(SnapshotDateKey as int64) as snapshot_date_key,
    cast(ProductKey as int64) as product_key,
    trim(cast(ProductSKU as string)) as product_sku,
    cast(WarehouseKey as int64) as warehouse_key,
    trim(cast(WarehouseCode as string)) as warehouse_code,
    cast(OnHandQuantity as int64) as on_hand_quantity,
    cast(ReservedQuantity as int64) as reserved_quantity,
    cast(AvailableQuantity as int64) as available_quantity,
    cast(InTransitInboundQuantity as int64) as in_transit_inbound_quantity,
    round(cast(UnitLandedCost as numeric), 2) as unit_landed_cost,
    round(cast(InventoryValuation as numeric), 2) as inventory_valuation,
    cast(DaysSinceLastMovement as int64) as days_since_last_movement,
    cast(IsStockoutFlag as int64) as is_stockout_flag,
    cast(IsDeadStockFlag as int64) as is_dead_stock_flag
from {{ source('raw_supply_chain', 'raw_fact_inventory_snapshot') }}
