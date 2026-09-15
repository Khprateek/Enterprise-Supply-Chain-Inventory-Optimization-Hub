-- Staging model for DimEmployeePlanner
select
    cast(PlannerKey as int64) as planner_key,
    trim(cast(EmployeeNumber as string)) as employee_number,
    trim(cast(PlannerName as string)) as planner_name,
    lower(trim(cast(EmailAddress as string))) as email_address,
    trim(cast(JobRole as string)) as job_role,
    trim(cast(Department as string)) as department,
    cast(AssignedRegionKey as int64) as assigned_region_key,
    trim(cast(AssignedCategoryGroup as string)) as assigned_category_group
from {{ source('raw_supply_chain', 'raw_dim_employee_planner') }}
