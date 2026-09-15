-- Intermediate model: Computes 30-day moving sales velocity by SKU and Warehouse
with sales as (
    select
        order_date,
        product_key,
        warehouse_key,
        ordered_quantity,
        net_sales_amount
    from {{ ref('stg_fact_sales') }}
),
daily_agg as (
    select
        order_date,
        product_key,
        warehouse_key,
        sum(ordered_quantity) as daily_units_sold,
        sum(net_sales_amount) as daily_revenue
    from sales
    group by order_date, product_key, warehouse_key
)
select
    order_date,
    product_key,
    warehouse_key,
    daily_units_sold,
    daily_revenue,
    avg(daily_units_sold) over(
        partition by product_key, warehouse_key
        order by order_date
        rows between 29 preceding and current row
    ) as rolling_30d_avg_daily_demand
from daily_agg
