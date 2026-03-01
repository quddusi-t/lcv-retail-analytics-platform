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
    -- Loyalty member flag
    loyalty_member,
    -- Join date for loyalty members
    join_date,
    -- First and last purchase dates
    first_purchase_date,
    last_purchase_date,
    -- Customer lifetime metrics
    lifetime_purchases,
    -- Ensure lifetime spend is non-negative
    CASE
        WHEN lifetime_spend < 0 THEN 0
        ELSE lifetime_spend
    END AS lifetime_spend,
    -- Standardize country
    UPPER(country) AS country,
    -- Customer status
    status
FROM
    `{{ var('raw_dataset') }}.dim_customer`
WHERE
    -- Ensure required fields
    customer_id IS NOT NULL

ORDER BY customer_id
