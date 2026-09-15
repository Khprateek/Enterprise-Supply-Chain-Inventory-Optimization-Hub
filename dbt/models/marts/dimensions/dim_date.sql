-- Conformed Dimension: DimDate
{{ config(materialized='table') }}

select
    date_key,
    full_date,
    day_of_week,
    day_name,
    day_of_month,
    day_of_year,
    week_of_year,
    month_number,
    month_name,
    month_year,
    quarter_number,
    quarter_name,
    year_number,
    fiscal_month_number,
    fiscal_quarter,
    fiscal_year,
    is_weekday,
    is_holiday,
    seasonality_period
from {{ ref('stg_dim_date') }}
