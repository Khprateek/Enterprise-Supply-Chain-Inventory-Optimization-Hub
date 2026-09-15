-- Staging model for DimWarehouse
select
    cast(WarehouseKey as int64) as warehouse_key,
    trim(cast(WarehouseCode as string)) as warehouse_code,
    trim(cast(WarehouseName as string)) as warehouse_name,
    cast(RegionKey as int64) as region_key,
    trim(cast(FacilityType as string)) as facility_type,
    cast(StorageCapacityPallets as int64) as storage_capacity_pallets,
    cast(TotalAreaSqMeters as int64) as total_area_sq_meters,
    cast(RefrigeratedCapacityPallets as int64) as refrigerated_capacity_pallets,
    cast(OperatingHoursPerWeek as int64) as operating_hours_per_week,
    cast(ActiveFlag as boolean) as is_active
from {{ source('raw_supply_chain', 'raw_dim_warehouse') }}
