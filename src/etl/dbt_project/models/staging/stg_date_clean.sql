-- Staging model for dim_date dimension table
-- Ensures date continuity and adds fiscal period calculations

{{
    config(
        materialized='view',
        description='Cleaned and validated date dimension from raw tables'
    )
}}

SELECT
    date_key,
    date_value,
    year,
    quarter,
    month,
    day_of_week,
    day_of_month,
    day_of_year,
    week_of_year,
    -- Add fiscal year (assumes fiscal year starts Apr 1)
    CASE
        WHEN EXTRACT(MONTH FROM date_value) >= 4
        THEN EXTRACT(YEAR FROM date_value)
        ELSE EXTRACT(YEAR FROM date_value) - 1
    END AS fiscal_year,
    is_weekend,
    is_holiday,
    created_at
FROM
    `{{ var('raw_dataset') }}.dim_date`
WHERE
    -- Ensure no null dates
    date_value IS NOT NULL
    AND date_key IS NOT NULL

ORDER BY date_key
