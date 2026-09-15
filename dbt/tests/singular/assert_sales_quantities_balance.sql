-- Singular test: Verify that shipped + cancelled does not exceed ordered quantity
select
    sales_line_key,
    ordered_quantity,
    shipped_quantity,
    cancelled_quantity
from {{ ref('fact_sales') }}
where shipped_quantity + cancelled_quantity > ordered_quantity
