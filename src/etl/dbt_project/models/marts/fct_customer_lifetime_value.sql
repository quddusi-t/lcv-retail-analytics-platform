{{ config(
    materialized='table',
) }}

-- CTE 1: Aggregates
WITH customer_lifetime_value AS (
    SELECT
        customer_id,
        SUM(net_amount) AS lifetime_value,
        COUNT(*) AS purchase_count,
        ROUND(SUM(net_amount) / COUNT(*), 2) AS avg_order_value,
        DATE_DIFF(CURRENT_DATE, MAX(sale_date), DAY) AS days_since_last_purchase,
        MAX(sale_date) AS last_purchase_date
    FROM
        {{ ref('stg_sales_clean') }}
    WHERE
        is_return = FALSE -- Exclude returns from CLV calculation
    GROUP BY
        customer_id
)

--CTE 2: Window functions (ROW_NUMBER, NTILE)
, customer_ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY lifetime_value DESC) AS rank,
        NTILE(4) OVER (ORDER BY lifetime_value DESC) AS quartile
    FROM
        customer_lifetime_value
)

-- Main SELECT: Join with customer dimension for additional attributes
SELECT
    cr.customer_id,
    dc.loyalty_member,
    dc.country,
    dc.join_date,
    cr.lifetime_value,
    cr.purchase_count,
    cr.avg_order_value,
    cr.days_since_last_purchase,
    cr.last_purchase_date,
    cr.rank,
    cr.quartile,
    CASE
        WHEN cr.days_since_last_purchase > 180 THEN 'At Risk'
        WHEN cr.quartile = 1 AND dc.loyalty_member = TRUE THEN 'VIP Loyal'
        WHEN cr.quartile = 1 THEN 'High Value'
        WHEN cr.quartile = 2 THEN 'Medium Value'
        WHEN cr.quartile = 3 THEN 'Low Value'
        ELSE 'Low Value'
    END AS customer_segment,
    CURRENT_TIMESTAMP() AS _loaded_at
FROM
    customer_ranked cr
LEFT JOIN
    {{ ref('stg_customer_clean') }} dc
ON
    cr.customer_id = dc.customer_id
