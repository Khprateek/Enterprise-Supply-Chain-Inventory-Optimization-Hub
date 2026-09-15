-- Staging model for DimRegion
select
    cast(RegionKey as int64) as region_key,
    trim(cast(RegionCode as string)) as region_code,
    trim(cast(RegionName as string)) as region_name,
    trim(cast(Theater as string)) as theater,
    trim(cast(PrimaryCountry as string)) as primary_country,
    trim(cast(CurrencyCode as string)) as currency_code,
    trim(cast(RegionalDirector as string)) as regional_director
from {{ source('raw_supply_chain', 'raw_dim_region') }}
