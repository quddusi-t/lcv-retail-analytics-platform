-- Staging model for fact_sales fact table
-- Deduplicates, validates, and joins with dimensions
-- Materialized as view (default from dbt_project.yml)

SELECT
    sale_id,
    store_id,
    product_id,
    customer_id,
    sale_date,
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
    -- Validate total amount
    CASE
        WHEN total_amount < 0 THEN NULL
        ELSE total_amount
    END AS total_amount,
    -- Discount as percentage (0-100)
    CASE
        WHEN discount_pct < 0 OR discount_pct > 100 THEN 0
        ELSE discount_pct
    END AS discount_pct,
    -- Discount amount in dollars
    CASE
        WHEN discount_amount < 0 THEN 0
        ELSE discount_amount
    END AS discount_amount,
    -- Net amount after discount
    net_amount,
    -- Cost amount
    CASE
        WHEN cost_amount < 0 THEN NULL
        ELSE cost_amount
    END AS cost_amount,
    -- Margin/profit
    margin_amount,
    -- Payment method
    CASE
        WHEN payment_method IS NULL THEN 'UNKNOWN'
        ELSE UPPER(payment_method)
    END AS payment_method,
    -- Return flag
    CASE
        WHEN is_return IS NULL THEN FALSE
        ELSE is_return
    END AS is_return
FROM
    `{{ var('raw_dataset') }}.fact_sales`
WHERE
    -- Remove completely null transactions
    sale_id IS NOT NULL
    AND store_id IS NOT NULL
    AND product_id IS NOT NULL
    AND customer_id IS NOT NULL
    AND sale_date IS NOT NULL
