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
    product_code,
    UPPER(category) AS category,
    UPPER(subcategory) AS subcategory,
    color,
    size,
    material,
    season,
    -- Standardize brand (handle nulls)
    CASE
        WHEN brand IS NULL OR brand = '' THEN 'UNBRANDED'
        ELSE UPPER(brand)
    END AS brand,
    -- Ensure costs are positive
    CASE
        WHEN unit_cost <= 0 THEN -1
        ELSE unit_cost
    END AS unit_cost,
    -- Ensure prices are positive
    CASE
        WHEN list_price <= 0 THEN -1
        ELSE list_price
    END AS list_price,
    status,
    created_at,
    updated_at,
    is_current,
    scd_start_date
FROM
    `{{ var('raw_dataset') }}.dim_product`
WHERE
    -- Ensure required fields
    product_id IS NOT NULL
    AND product_name IS NOT NULL
    AND category IS NOT NULL

ORDER BY product_id
