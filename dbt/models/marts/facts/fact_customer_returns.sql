-- Analytical Fact: FactCustomerReturns (Reverse Logistics & Salvage)
{{ config(
    materialized='table',
    partition_by={
        "field": "return_date",
        "data_type": "date",
        "granularity": "month"
    },
    cluster_by=['product_key', 'customer_channel_key']
) }}

select
    return_line_key,
    return_id,
    return_date,
    original_order_date,
    return_date_key,
    original_order_date_key,
    product_key,
    receiving_warehouse_key,
    customer_channel_key,
    returned_quantity,
    restocked_quantity,
    scrapped_quantity,
    refund_amount,
    return_reason_category,
    disposition_status
from {{ ref('stg_fact_customer_returns') }}
