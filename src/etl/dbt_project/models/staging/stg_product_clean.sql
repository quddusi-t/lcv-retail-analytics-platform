-- Staging model for dim_product dimension table
-- Cleans and validates product information

{{
    config(
        materialized='view',
        description='Cleaned and validated product dimension'
    )
}}

SELECT
    product_id,
    product_name,
    UPPER(category) AS category,
    UPPER(subcategory) AS subcategory,
    -- Standardize brand (handle nulls)
    CASE
        WHEN brand IS NULL OR brand = '' THEN 'UNBRANDED'
        ELSE UPPER(brand)
    END AS brand,
    -- Ensure prices are positive (flag if not)
    CASE
        WHEN unit_price <= 0 THEN -1
        ELSE unit_price
    END AS unit_price,
    -- Ensure costs are positive
    CASE
        WHEN cost_price <= 0 THEN -1
        ELSE cost_price
    END AS cost_price,
    CASE
        WHEN is_active IS NULL THEN TRUE
        ELSE is_active
    END AS is_active,
    created_at,
    updated_at
FROM
    `{{ var('raw_dataset') }}.dim_product`
WHERE
    -- Ensure required fields
    product_id IS NOT NULL
    AND product_name IS NOT NULL
    AND category IS NOT NULL

ORDER BY product_id
