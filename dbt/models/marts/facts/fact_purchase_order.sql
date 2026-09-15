-- Analytical Fact: FactPurchaseOrder (Replenishment Lines & Inbound Receiving)
{{ config(
    materialized='table',
    partition_by={
        "field": "po_creation_date",
        "data_type": "date",
        "granularity": "day"
    },
    cluster_by=['supplier_key', 'product_key', 'receiving_warehouse_key']
) }}

with po as (
    select *
    from {{ ref('stg_fact_purchase_order') }}
),

supplier as (
    select
        supplier_key,
        supplier_tier,
        region_zone
    from {{ ref('stg_dim_supplier') }}
)

select
    po.po_line_key,
    po.purchase_order_id,
    po.po_line_number,
    po.po_creation_date,
    po.promised_delivery_date,
    po.actual_dock_receipt_date,
    po.po_creation_date_key,
    po.promised_delivery_date_key,
    po.actual_dock_receipt_date_key,
    po.supplier_key,
    po.product_key,
    po.receiving_warehouse_key,
    po.buyer_employee_key,
    po.ordered_quantity,
    po.received_quantity,
    po.rejected_quantity,
    po.unit_purchase_price,
    po.extended_po_amount,
    po.promised_lead_time_days,
    po.actual_lead_time_days,
    po.lead_time_variance_days,
    po.is_delivered_on_time_flag,
    po.is_delivered_in_full_flag,
    po.is_supplier_otif_flag,
    po.po_status,

    -- Delay root cause classification (Page 4: Root Cause breakdown visual)
    -- Priority order: Overseas customs > Tier 3 material shortage > Carrier/freight > On time
    case
        when po.po_status = 'Completed'
             and sup.region_zone = 'Overseas Inbound'
             and po.lead_time_variance_days >= 7
            then 'Customs & Port Congestion (Overseas)'
        when po.po_status = 'Completed'
             and sup.supplier_tier = 'Tier 3 Tactical'
             and po.lead_time_variance_days between 3 and 5
            then 'Raw Material Shortage (Tier 3)'
        when po.po_status = 'Completed'
             and po.lead_time_variance_days between 1 and 2
            then 'Carrier Capacity & Freight Inefficiency'
        when po.po_status = 'Completed'
             and po.lead_time_variance_days > 0
            then 'Other Late Delivery'
        else 'On Time or Early'
    end as delay_root_cause_category

from po
left join supplier as sup
    on po.supplier_key = sup.supplier_key
