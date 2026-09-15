-- Staging model for FactInventoryMovement
select
    cast(MovementKey as int64) as movement_key,
    trim(cast(MovementTransactionID as string)) as movement_transaction_id,
    cast(MovementDate as date) as movement_date,
    cast(MovementDateKey as int64) as movement_date_key,
    cast(ProductKey as int64) as product_key,
    trim(cast(ProductSKU as string)) as product_sku,
    cast(OriginWarehouseKey as int64) as origin_warehouse_key,
    cast(DestinationWarehouseKey as int64) as destination_warehouse_key,
    cast(ResponsibleEmployeeKey as int64) as responsible_employee_key,
    trim(cast(MovementType as string)) as movement_type,
    cast(MovementQuantity as int64) as movement_quantity,
    round(cast(MovementValue as numeric), 2) as movement_value,
    round(cast(TransferFreightCost as numeric), 2) as transfer_freight_cost,
    cast(TransferTransitDays as int64) as transfer_transit_days
from {{ source('raw_supply_chain', 'raw_fact_inventory_movement') }}
