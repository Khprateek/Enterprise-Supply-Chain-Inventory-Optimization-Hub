-- Analytical Fact: FactInventoryMovement (Transfers, Shrinkage & Adjustments)
{{ config(
    materialized='table',
    partition_by={
        "field": "movement_date",
        "data_type": "date",
        "granularity": "day"
    },
    cluster_by=['product_key', 'origin_warehouse_key']
) }}

select
    movement_key,
    movement_transaction_id,
    movement_date,
    movement_date_key,
    product_key,
    origin_warehouse_key,
    destination_warehouse_key,
    responsible_employee_key,
    movement_type,
    movement_quantity,
    movement_value,
    transfer_freight_cost,
    transfer_transit_days
from {{ ref('stg_fact_inventory_movement') }}
