-- Staging model for BridgeProductSupplier
select
    cast(BridgeKey as int64) as bridge_key,
    trim(cast(ProductSKU as string)) as product_sku,
    cast(SupplierKey as int64) as supplier_key,
    cast(IsPrimarySupplier as boolean) as is_primary_supplier,
    round(cast(ContractAllocationSharePct as numeric), 2) as contract_allocation_share_pct
from {{ source('raw_supply_chain', 'raw_bridge_product_supplier') }}
