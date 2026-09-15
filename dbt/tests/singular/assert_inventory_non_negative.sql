-- Singular test: Ensure on-hand and available inventory never fall below zero
select
    snapshot_key,
    on_hand_quantity,
    available_quantity
from {{ ref('fact_inventory_snapshot') }}
where on_hand_quantity < 0 or available_quantity < 0
