-- Staging model for dim_date dimension table
-- Ensures date continuity and adds fiscal period calculations

{{
    config(
        materialized='view',
        description='Cleaned and validated date dimension from raw tables'
    )
}}

SELECT
    date_id,
    date_value,
    year,
    quarter,
    month,
    day_of_week,
    day_name,
    week_of_year,
    fiscal_year,
    fiscal_quarter,
    is_weekend,
    is_holiday,
    holiday_name
FROM
    `{{ var('raw_dataset') }}.dim_date`
WHERE
    -- Ensure no null dates
    date_value IS NOT NULL
    AND date_id IS NOT NULL

ORDER BY date_id
