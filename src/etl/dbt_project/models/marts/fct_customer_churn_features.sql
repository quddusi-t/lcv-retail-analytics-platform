{{ config(
    materialized='table',
    partition_by={
        'field': 'as_of_date',
        'data_type': 'date',
        'granularity': 'day',
    },
    cluster_by=['is_churned', 'loyalty_member'],
) }}

-- Reference date: 2025-10-31 (synthetic data ceiling).
-- Swap to CURRENT_DATE when running against live data.
WITH purchase_history AS (
    SELECT
        customer_id,
        sale_date,
        net_amount,
        is_return
    FROM {{ ref('stg_sales_clean') }}
    WHERE customer_id IS NOT NULL
      AND sale_date <= DATE '2025-10-31'
),

customer_aggregates AS (
    SELECT
        customer_id,

        -- Recency
        DATE_DIFF(DATE '2025-10-31', MAX(CASE WHEN NOT is_return THEN sale_date END), DAY)
            AS days_since_last_purchase,

        -- Purchase frequency windows (forward-looking from reference date)
        COUNTIF(NOT is_return AND sale_date >= DATE_SUB(DATE '2025-10-31', INTERVAL 30 DAY))
            AS purchases_l30d,
        COUNTIF(NOT is_return AND sale_date >= DATE_SUB(DATE '2025-10-31', INTERVAL 60 DAY))
            AS purchases_l60d,
        COUNTIF(NOT is_return AND sale_date >= DATE_SUB(DATE '2025-10-31', INTERVAL 90 DAY))
            AS purchases_l90d,

        -- Spend in most recent 90 days vs the 90 days before that
        SUM(CASE
            WHEN NOT is_return
             AND sale_date >= DATE_SUB(DATE '2025-10-31', INTERVAL 90 DAY)
            THEN net_amount ELSE 0 END)
            AS spend_l90d,
        SUM(CASE
            WHEN NOT is_return
             AND sale_date >= DATE_SUB(DATE '2025-10-31', INTERVAL 180 DAY)
             AND sale_date <  DATE_SUB(DATE '2025-10-31', INTERVAL 90 DAY)
            THEN net_amount ELSE 0 END)
            AS spend_prev_90d,

        -- Return rate inputs
        COUNTIF(is_return)  AS total_returns,
        COUNT(*)            AS total_transactions,

        -- Cadence inputs
        COUNTIF(NOT is_return) AS purchase_count,
        DATE_DIFF(
            MAX(CASE WHEN NOT is_return THEN sale_date END),
            MIN(CASE WHEN NOT is_return THEN sale_date END),
            DAY
        ) AS tenure_days

    FROM purchase_history
    GROUP BY customer_id
),

customer_derived AS (
    SELECT
        *,
        -- NULL when only one purchase (no cadence yet)
        CASE
            WHEN purchase_count > 1
            THEN ROUND(tenure_days / (purchase_count - 1), 1)
        END AS avg_days_between_purchases,

        SAFE_DIVIDE(spend_l90d, spend_prev_90d) AS spend_trend_ratio,
        SAFE_DIVIDE(total_returns, total_transactions) AS return_rate
    FROM customer_aggregates
)

SELECT
    cd.customer_id,
    c.loyalty_member,

    -- Features
    cd.days_since_last_purchase,
    cd.purchases_l30d,
    cd.purchases_l60d,
    cd.purchases_l90d,
    cd.spend_l90d,
    cd.spend_prev_90d,
    cd.spend_trend_ratio,
    cd.return_rate,
    cd.avg_days_between_purchases,
    cd.purchase_count,

    -- Churn target: churned if silent longer than MAX(90d, 1.5x personal cadence)
    CASE
        WHEN cd.days_since_last_purchase
             > GREATEST(90, COALESCE(cd.avg_days_between_purchases * 1.5, 90))
        THEN TRUE
        ELSE FALSE
    END AS is_churned,

    DATE '2025-10-31' AS as_of_date,
    CURRENT_TIMESTAMP() AS _loaded_at

FROM customer_derived cd
LEFT JOIN {{ ref('stg_customer_clean') }} c
    ON cd.customer_id = c.customer_id
