-- SCD Type 2 Snapshot: snap_dim_product_scd2
{% snapshot snap_dim_product_scd2 %}

{{
    config(
      target_schema='snapshots',
      unique_key='product_sku',
      strategy='check',
      check_cols=['unit_standard_cost', 'unit_list_price', 'category_name', 'primary_supplier_key', 'handling_profile'],
      invalidate_hard_deletes=True
    )
}}

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
    xyz_classification
from {{ ref('stg_dim_product') }}

{% endsnapshot %}
