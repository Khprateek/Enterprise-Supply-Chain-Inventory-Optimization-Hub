-- Staging model for FactCustomerReturns
select
    cast(ReturnLineKey as int64) as return_line_key,
    trim(cast(ReturnID as string)) as return_id,
    cast(ReturnDate as date) as return_date,
    cast(OriginalOrderDate as date) as original_order_date,
    cast(ReturnDateKey as int64) as return_date_key,
    cast(OriginalOrderDateKey as int64) as original_order_date_key,
    cast(ProductKey as int64) as product_key,
    trim(cast(ProductSKU as string)) as product_sku,
    cast(ReceivingWarehouseKey as int64) as receiving_warehouse_key,
    trim(cast(WarehouseCode as string)) as warehouse_code,
    cast(CustomerChannelKey as int64) as customer_channel_key,
    cast(ReturnedQuantity as int64) as returned_quantity,
    cast(RestockedQuantity as int64) as restocked_quantity,
    cast(ScrappedQuantity as int64) as scrapped_quantity,
    round(cast(RefundAmount as numeric), 2) as refund_amount,
    trim(cast(ReturnReasonCategory as string)) as return_reason_category,
    trim(cast(DispositionStatus as string)) as disposition_status
from {{ source('raw_supply_chain', 'raw_fact_customer_returns') }}
