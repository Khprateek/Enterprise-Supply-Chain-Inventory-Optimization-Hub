-- Staging model for FactSales
select
    cast(SalesLineKey as int64) as sales_line_key,
    trim(cast(SalesOrderID as string)) as sales_order_id,
    cast(SalesOrderLineNumber as int64) as sales_order_line_number,
    cast(OrderDate as date) as order_date,
    cast(ShipDate as date) as ship_date,
    cast(DeliveryDate as date) as delivery_date,
    cast(OrderDateKey as int64) as order_date_key,
    cast(ShipDateKey as int64) as ship_date_key,
    cast(DeliveryDateKey as int64) as delivery_date_key,
    cast(ProductKey as int64) as product_key,
    trim(cast(ProductSKU as string)) as product_sku,
    cast(CustomerChannelKey as int64) as customer_channel_key,

    cast(WarehouseKey as int64) as warehouse_key,

    cast(OrderedQuantity as int64) as ordered_quantity,
    cast(ShippedQuantity as int64) as shipped_quantity,
    cast(CancelledQuantity as int64) as cancelled_quantity,
    round(cast(UnitPrice as numeric), 2) as unit_price,
    round(cast(UnitStandardCost as numeric), 2) as unit_standard_cost,
    round(cast(GrossSalesAmount as numeric), 2) as gross_sales_amount,
    round(cast(DiscountAmount as numeric), 2) as discount_amount,
    round(cast(NetSalesAmount as numeric), 2) as net_sales_amount,
    round(cast(CostOfGoodsSold as numeric), 2) as cost_of_goods_sold,
    cast(OrderLineCycleTimeDays as int64) as order_line_cycle_time_days,
    cast(OnTimeInFullFlag as int64) as on_time_in_full_flag
from {{ source('raw_supply_chain', 'raw_fact_sales') }}
