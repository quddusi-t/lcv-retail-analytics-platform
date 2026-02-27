-- Staging model for dim_store dimension table
-- Cleans and validates store information

{{
    config(
        materialized='view',
        description='Cleaned and validated store dimension with region hierarchy'
    )
}}

SELECT
    store_id,
    store_name,
    UPPER(city) AS city,
    UPPER(region) AS region,
    state,
    country,
    -- Standardize store type
    CASE
        WHEN store_type IS NULL THEN 'UNKNOWN'
        ELSE UPPER(store_type)
    END AS store_type,
    store_size_sqft,
    manager_name,
    created_at,
    updated_at
FROM
    `{{ var('raw_dataset') }}.dim_store`
WHERE
    -- Ensure required fields
    store_id IS NOT NULL
    AND store_name IS NOT NULL
    AND region IS NOT NULL

ORDER BY store_id
