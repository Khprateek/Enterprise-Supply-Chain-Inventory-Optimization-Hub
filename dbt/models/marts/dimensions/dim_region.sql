-- Conformed Dimension: DimRegion
{{ config(materialized='table') }}

select
    region_key,
    region_code,
    region_name,
    theater,
    primary_country,
    currency_code,
    regional_director
from {{ ref('stg_dim_region') }}
