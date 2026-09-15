-- Staging model for DimProduct
select
    cast(ProductKey as int64) as product_key,
    trim(cast(ProductSKU as string)) as product_sku,
    trim(cast(ProductName as string)) as product_name,
    trim(cast(BrandName as string)) as brand_name,
    trim(cast(CategoryName as string)) as category_name,
    trim(cast(SubcategoryName as string)) as subcategory_name,
    trim(cast(DepartmentName as string)) as department_name,
    round(cast(UnitStandardCost as numeric), 2) as unit_standard_cost,
    round(cast(UnitListPrice as numeric), 2) as unit_list_price,
    trim(cast(HandlingProfile as string)) as handling_profile,
    trim(cast(StorageClass as string)) as storage_class,
    round(cast(WeightKg as numeric), 3) as weight_kg,
    round(cast(VolumeCubicMeters as numeric), 4) as volume_cubic_meters,
    cast(PrimarySupplierKey as int64) as primary_supplier_key,
    trim(cast(ABCClassification as string)) as abc_classification,
    trim(cast(XYZClassification as string)) as xyz_classification,
    cast(EffectiveFrom as date) as effective_from_date,
    cast(EffectiveTo as date) as effective_to_date,
    cast(IsCurrent as boolean) as is_current
from {{ source('raw_supply_chain', 'raw_dim_product') }}
