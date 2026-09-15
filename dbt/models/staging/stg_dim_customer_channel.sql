-- Staging model for DimCustomerChannel
select
    cast(CustomerChannelKey as int64) as customer_channel_key,
    trim(cast(CustomerChannelCode as string)) as customer_channel_code,
    trim(cast(ChannelName as string)) as channel_name,
    trim(cast(CustomerAccountName as string)) as customer_account_name,
    trim(cast(CustomerSegment as string)) as customer_segment,
    cast(CreditTermsDays as int64) as credit_terms_days,
    trim(cast(DeliveryPriorityTier as string)) as delivery_priority_tier
from {{ source('raw_supply_chain', 'raw_dim_customer_channel') }}
