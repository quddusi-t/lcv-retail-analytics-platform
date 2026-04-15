{{ config(materialized='table') }}

-- CTE 1: Aggregation
WITH store_performance AS(
    SELECT
        sa.store_id,
        st.store_name,
        st.region,
        SUM(sa.net_amount) AS total_revenue,
        SUM(sa.margin_amount) AS total_profit,
        ROUND(SUM(sa.net_amount) / COUNT(*), 2) AS avg_transaction_value,
        COUNT(*) AS transaction_count,
        SUM(sa.quantity) AS total_units_sold
    FROM
        {{ ref('stg_sales_clean') }} sa
    LEFT JOIN
        {{ ref('stg_store_clean') }} st
    ON
        sa.store_id = st.store_id
    WHERE
        sa.is_return = FALSE
    GROUP BY
        sa.store_id,
        st.store_name,
        st.region
)

-- CTE 2: CALCULATION (Window functions)
, store_ranked AS(
    SELECT
        store_id,
        store_name,
        region,
        total_revenue,
        total_profit,
        avg_transaction_value,
        transaction_count,
        total_units_sold,
        ROW_NUMBER() OVER (PARTITION BY region ORDER BY total_revenue DESC) AS rank_in_region,
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC) AS rank_overall
    FROM
        store_performance
)

-- CTE 3: Enrichment (Segment)
SELECT
    store_id,
    store_name,
    region,
    total_revenue,
    total_profit,
    avg_transaction_value,
    transaction_count,
    total_units_sold,
    rank_in_region,
    rank_overall,
    CASE
        WHEN rank_in_region = 1 THEN 'Top Store in Region'
        WHEN rank_in_region <= 3 THEN 'High Performing Store'
        WHEN rank_in_region >= 9 THEN 'Needs Attention'
        ELSE 'Average Performer'
    END AS regional_performance_segment,
    CASE
        WHEN rank_overall <= 5 THEN 'Top Store Overall'
        WHEN rank_overall <= 15 THEN 'High Performing Store Overall'
        WHEN rank_overall >= 46 THEN 'Needs Attention Overall'
        ELSE 'Average Performer Overall'
    END AS overall_performance_segment,
    CURRENT_TIMESTAMP() AS _loaded_at
FROM
    store_ranked
