-- Conformed Dimension: DimWarehouse
{{ config(
    materialized='table',
    cluster_by=['region_key']
) }}

select
    warehouse_key,
    warehouse_code,
    warehouse_name,
    region_key,
    facility_type,
    storage_capacity_pallets,
    total_area_sq_meters,
    refrigerated_capacity_pallets,
    operating_hours_per_week,
    is_active
from {{ ref('stg_dim_warehouse') }}
