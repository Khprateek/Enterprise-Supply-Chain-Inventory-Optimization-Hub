-- Conformed Dimension: DimCustomerChannel
{{ config(materialized='table') }}

select
    customer_channel_key,
    customer_channel_code,
    channel_name,
    customer_account_name,
    customer_segment,
    credit_terms_days,
    delivery_priority_tier
from {{ ref('stg_dim_customer_channel') }}
