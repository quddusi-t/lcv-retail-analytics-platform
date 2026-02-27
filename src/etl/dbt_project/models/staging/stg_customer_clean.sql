-- Staging model for dim_customer dimension table
-- Deduplicates and validates customer information

{{
    config(
        materialized='view',
        description='Deduplicated and validated customer dimension'
    )
}}

SELECT
    customer_id,
    customer_name,
    email,
    phone,
    -- Standardize country
    UPPER(country) AS country,
    UPPER(city) AS city,
    state,
    postal_code,
    -- Customer segment
    CASE
        WHEN customer_segment IS NULL THEN 'UNKNOWN'
        ELSE UPPER(customer_segment)
    END AS customer_segment,
    -- Join date
    CAST(join_date AS DATE) AS join_date,
    -- Ensure lifetime value is non-negative
    CASE
        WHEN lifetime_value < 0 THEN 0
        ELSE lifetime_value
    END AS lifetime_value,
    created_at,
    updated_at,
    -- Row number for deduplication (in case of duplicates)
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY updated_at DESC) AS rn
FROM
    `{{ var('raw_dataset') }}.dim_customer`
WHERE
    -- Ensure required fields
    customer_id IS NOT NULL
    AND customer_name IS NOT NULL
    AND email IS NOT NULL

QUALIFY rn = 1  -- Keep only latest version if duplicates exist

ORDER BY customer_id
