-- Conformed Dimension: DimEmployeePlanner
{{ config(materialized='table') }}

select
    planner_key,
    employee_number,
    planner_name,
    email_address,
    job_role,
    department,
    assigned_region_key,
    assigned_category_group
from {{ ref('stg_dim_employee_planner') }}
