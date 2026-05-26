{%- set ref_date = date_literal('2025-10-31') -%}

{{ config(
    materialized='table',
    partition_by={
        'field': 'as_of_date',
        'data_type': 'date',
        'granularity': 'day',
    } if target.type == 'bigquery' else none,
    cluster_by=['is_churned', 'loyalty_member'] if target.type == 'bigquery' else none,
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
      AND sale_date <= {{ ref_date }}
),

customer_aggregates AS (
    SELECT
        customer_id,

        -- Recency
        {{ datediff_days('MAX(CASE WHEN NOT is_return THEN sale_date END)', ref_date) }}
            AS days_since_last_purchase,

        -- Purchase frequency windows (forward-looking from reference date)
        {{ countif('NOT is_return AND sale_date >= ' ~ dateadd_days(ref_date, -30)) }}
            AS purchases_l30d,
        {{ countif('NOT is_return AND sale_date >= ' ~ dateadd_days(ref_date, -60)) }}
            AS purchases_l60d,
        {{ countif('NOT is_return AND sale_date >= ' ~ dateadd_days(ref_date, -90)) }}
            AS purchases_l90d,

        -- Spend in most recent 90 days vs the 90 days before that
        SUM(CASE
            WHEN NOT is_return
             AND sale_date >= {{ dateadd_days(ref_date, -90) }}
            THEN net_amount ELSE 0 END)
            AS spend_l90d,
        SUM(CASE
            WHEN NOT is_return
             AND sale_date >= {{ dateadd_days(ref_date, -180) }}
             AND sale_date <  {{ dateadd_days(ref_date, -90) }}
            THEN net_amount ELSE 0 END)
            AS spend_prev_90d,

        -- Return rate inputs
        {{ countif('is_return') }}  AS total_returns,
        COUNT(*)                    AS total_transactions,

        -- Cadence inputs
        {{ countif('NOT is_return') }} AS purchase_count,
        {{ datediff_days(
            'MIN(CASE WHEN NOT is_return THEN sale_date END)',
            'MAX(CASE WHEN NOT is_return THEN sale_date END)'
        ) }} AS tenure_days

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

        {{ safe_divide('spend_l90d', 'spend_prev_90d') }} AS spend_trend_ratio,
        {{ safe_divide('total_returns', 'total_transactions') }} AS return_rate
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

    {{ ref_date }} AS as_of_date,
    CURRENT_TIMESTAMP() AS _loaded_at

FROM customer_derived cd
LEFT JOIN {{ ref('stg_customer_clean') }} c
    ON cd.customer_id = c.customer_id
