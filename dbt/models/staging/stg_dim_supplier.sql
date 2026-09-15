-- Staging model for DimSupplier
select
    cast(SupplierKey as int64) as supplier_key,
    trim(cast(SupplierCode as string)) as supplier_code,
    trim(cast(SupplierName as string)) as supplier_name,
    trim(cast(Country as string)) as country,
    trim(cast(City as string)) as city,
    trim(cast(RegionZone as string)) as region_zone,
    trim(cast(SupplierTier as string)) as supplier_tier,
    cast(ContractLeadTimeDays as int64) as contract_lead_time_days,
    cast(LeadTimeToleranceDays as int64) as lead_time_tolerance_days,
    cast(PaymentTermsDays as int64) as payment_terms_days,
    cast(MinimumOrderQuantity as int64) as minimum_order_quantity,
    cast(PreferredStatusFlag as boolean) as is_preferred_status,
    round(cast(VendorRiskScore as numeric), 2) as vendor_risk_score
from {{ source('raw_supply_chain', 'raw_dim_supplier') }}
