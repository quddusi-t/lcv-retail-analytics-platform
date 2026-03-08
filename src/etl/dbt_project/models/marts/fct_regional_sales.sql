-- CTE 1: AGGREGATION
WITH regional_performance AS (
    SELECT
        s.region,
        s.store_name,
        p.category AS product_category,
        DATE_TRUNC(sc.sale_date, MONTH) AS year_month,
        SUM(sc.net_amount) AS total_revenue,
        SUM(sc.quantity) AS total_units_sold,
        SUM(sc.margin_amount) AS total_profit,
        ROUND((SUM(sc.margin_amount) / NULLIF(SUM(sc.net_amount), 0) * 100), 2) AS profit_margin,
        ROUND(SUM(sc.net_amount) / COUNT(*), 2) AS avg_transaction_value,
        COUNT(*) AS transaction_count
    FROM
        {{ ref('stg_sales_clean') }} sc
    LEFT JOIN
        {{ ref('stg_store_clean') }} s
    ON
        sc.store_id = s.store_id
    LEFT JOIN
        {{ ref('stg_product_clean') }} p
    ON
        sc.product_id = p.product_id
    WHERE
        sc.is_return = FALSE -- Exclude returns from regional performance metrics
    GROUP BY
        s.region,
        s.store_name,
        p.category,
        DATE_TRUNC(sc.sale_date, MONTH)
)
-- CTE 2: CALCULATION (Window functions)
, region_ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY region ORDER BY total_profit DESC) AS rank,
        NTILE(4) OVER (PARTITION BY region ORDER BY total_profit DESC) AS quartile
    FROM
        regional_performance
)

-- CTE 3: ENRICHMENT (Segment)
SELECT
    rr.region,
    rr.store_name,
    rr.product_category,
    rr.year_month,
    rr.total_revenue,
    rr.total_units_sold,
    rr.total_profit,
    rr.profit_margin,
    rr.avg_transaction_value,
    rr.transaction_count,
    rr.rank,
    rr.quartile,
    CASE
        WHEN rr.quartile = 1 THEN 'Top Performer'
        WHEN rr.quartile = 2 THEN 'High Performer'
        WHEN rr.quartile = 3 THEN 'Mid Performer'
        ELSE 'Low Performer'
    END AS performance_segment,
    CURRENT_TIMESTAMP() AS _loaded_at
FROM
    region_ranked rr
