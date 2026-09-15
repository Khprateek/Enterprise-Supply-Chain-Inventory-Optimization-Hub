-- Conformed Dimension: DimProduct (Kimball SCD Type 2 Active & Historical Presentation)
{{ config(
    materialized='table',
    cluster_by=['primary_supplier_key', 'category_name']
) }}

select
    product_key,
    product_sku,
    product_name,
    brand_name,
    category_name,
    subcategory_name,
    department_name,
    unit_standard_cost,
    unit_list_price,
    handling_profile,
    storage_class,
    weight_kg,
    volume_cubic_meters,
    primary_supplier_key,
    abc_classification,
    xyz_classification,
    cast(dbt_valid_from as date) as effective_from_date,
    cast(dbt_valid_to as date) as effective_to_date,
    case when dbt_valid_to is null then true else false end as is_current
from {{ ref('snap_dim_product_scd2') }}
