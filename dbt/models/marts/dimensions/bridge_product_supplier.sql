-- Sourcing Authorization Bridge: BridgeProductSupplier
{{ config(
    materialized='table',
    cluster_by=['supplier_key', 'product_sku']
) }}

select
    bridge_key,
    product_sku,
    supplier_key,
    is_primary_supplier,
    contract_allocation_share_pct
from {{ ref('stg_bridge_product_supplier') }}
