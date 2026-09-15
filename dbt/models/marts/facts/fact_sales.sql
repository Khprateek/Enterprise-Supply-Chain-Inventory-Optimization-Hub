-- Analytical Fact: FactSales (Transactional Order Lines)
{{ config(
    materialized='table',
    partition_by={
        "field": "order_date",
        "data_type": "date",
        "granularity": "day"
    },
    cluster_by=['product_key', 'warehouse_key', 'customer_channel_key']
) }}

select
    s.sales_line_key,
    s.sales_order_id,
    s.sales_order_line_number,
    s.order_date,
    s.ship_date,
    s.delivery_date,
    s.order_date_key,
    s.ship_date_key,
    s.delivery_date_key,
    coalesce(p.product_key, s.product_key) as product_key,
    s.customer_channel_key,
    s.warehouse_key,
    s.ordered_quantity,
    s.shipped_quantity,
    s.cancelled_quantity,
    s.unit_price,
    coalesce(p.unit_standard_cost, s.unit_standard_cost) as unit_standard_cost,
    s.gross_sales_amount,
    s.discount_amount,
    s.net_sales_amount,
    round(s.shipped_quantity * coalesce(p.unit_standard_cost, s.unit_standard_cost), 2) as cost_of_goods_sold,
    s.order_line_cycle_time_days,
    s.on_time_in_full_flag
from {{ ref('stg_fact_sales') }} s
left join {{ ref('dim_product') }} p
  on s.product_sku = p.product_sku
 and s.order_date >= p.effective_from_date
 and (s.order_date < p.effective_to_date or p.effective_to_date is null)
