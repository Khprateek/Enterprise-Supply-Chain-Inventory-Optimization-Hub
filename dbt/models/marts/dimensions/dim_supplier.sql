-- Conformed Dimension: DimSupplier
{{ config(materialized='table') }}

select
    supplier_key,
    supplier_code,
    supplier_name,
    country,
    city,
    region_zone,
    supplier_tier,
    contract_lead_time_days,
    lead_time_tolerance_days,
    payment_terms_days,
    minimum_order_quantity,
    is_preferred_status,
    vendor_risk_score
from {{ ref('stg_dim_supplier') }}
