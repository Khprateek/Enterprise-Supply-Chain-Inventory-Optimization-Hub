-- Analytical Fact: FactInventorySnapshot (Daily Semi-Additive Stock Balances)
{{ config(
    materialized='table',
    partition_by={
        "field": "snapshot_date",
        "data_type": "date",
        "granularity": "day"
    },
    cluster_by=['product_key', 'warehouse_key']
) }}

select
    snapshot_key,
    snapshot_date,
    snapshot_date_key,
    product_key,
    warehouse_key,
    on_hand_quantity,
    reserved_quantity,
    available_quantity,
    in_transit_inbound_quantity,
    unit_landed_cost,
    inventory_valuation,
    days_since_last_movement,
    is_stockout_flag,
    is_dead_stock_flag
from {{ ref('stg_fact_inventory_snapshot') }}
