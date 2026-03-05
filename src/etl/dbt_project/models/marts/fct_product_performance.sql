{{ config(
    materialized='table',
) }}

-- CTE to calculate total revenue, total units sold, total profit and count of transactions.
WITH product_performance AS (
    SELECT
        product_id,
        SUM(net_amount) AS total_revenue,
        SUM(quantity) AS total_units_sold,
        SUM(margin_amount) AS total_profit,
        COUNT(*) AS transaction_count
    FROM
        {{ ref('stg_sales_clean') }}
    WHERE
        is_return = FALSE -- Exclude returns from performance metrics
    GROUP BY
        product_id
)

SELECT
    pp.product_id,
    dp.product_name,
    dp.category,
    dp.subcategory,
    dp.brand,
    pp.total_revenue,
    pp.total_units_sold,
    pp.total_profit,
    pp.transaction_count
FROM
    product_performance pp
LEFT JOIN
    {{ ref('stg_product_clean') }} dp
ON
    pp.product_id = dp.product_id

ORDER BY
    pp.total_revenue DESC
