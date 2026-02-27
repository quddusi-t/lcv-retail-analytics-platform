-- Staging model for fact_sales fact table
-- Deduplicates, validates, and joins with dimensions

{{
    config(
        materialized='table',  -- Materialized table for performance (1M rows)
        description='Cleaned and deduplicated sales facts with dimension validation'
    )
}}

SELECT
    sale_id,
    store_id,
    product_id,
    customer_id,
    date_key,
    -- Ensure quantities are positive
    CASE
        WHEN quantity <= 0 THEN NULL
        ELSE quantity
    END AS quantity,
    -- Ensure unit price is positive
    CASE
        WHEN unit_price <= 0 THEN NULL
        ELSE unit_price
    END AS unit_price,
    -- Calculate total sale amount
    CASE
        WHEN quantity > 0 AND unit_price > 0 THEN ROUND(quantity * unit_price, 2)
        ELSE NULL
    END AS total_amount,
    -- Ensure discount is between 0 and 1
    CASE
        WHEN discount < 0 OR discount > 1 THEN 0
        ELSE discount
    END AS discount,
    -- Calculate amount after discount
    CASE
        WHEN total_amount IS NOT NULL THEN ROUND(total_amount * (1 - discount), 2)
        ELSE NULL
    END AS amount_after_discount,
    -- Ensure cost is positive
    CASE
        WHEN cost_price <= 0 THEN NULL
        ELSE cost_price
    END AS cost_price,
    -- Calculate profit
    CASE
        WHEN amount_after_discount IS NOT NULL AND cost_price IS NOT NULL
        THEN ROUND(amount_after_discount - (cost_price * quantity), 2)
        ELSE NULL
    END AS profit,
    -- Loyalty points (ensure non-negative)
    CASE
        WHEN loyalty_points < 0 THEN 0
        ELSE loyalty_points
    END AS loyalty_points,
    -- Payment method
    CASE
        WHEN payment_method IS NULL THEN 'UNKNOWN'
        ELSE UPPER(payment_method)
    END AS payment_method,
    -- Return flag
    CASE
        WHEN is_return IS NULL THEN FALSE
        ELSE is_return
    END AS is_return,
    created_at,
    updated_at,
    -- Deduplication: keep latest version
    ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY updated_at DESC) AS rn
FROM
    `{{ var('raw_dataset') }}.fact_sales`
WHERE
    -- Remove completely null transactions
    sale_id IS NOT NULL
    AND store_id IS NOT NULL
    AND product_id IS NOT NULL
    AND customer_id IS NOT NULL
    AND date_key IS NOT NULL

QUALIFY rn = 1  -- Keep only latest version of each sale

ORDER BY sale_id
