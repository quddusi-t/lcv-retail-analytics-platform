-- CTE 1: Aggregation

WITH daily_sales AS (
    SELECT
        sale_date,
        CONCAT(d.year, '-Q', d.quarter) AS year_quarter,
        CONCAT(d.year, '-', LPAD(CAST(d.month AS STRING), 2, '0')) AS year_month,
        d.day_of_week,
        NOT d.is_weekend AS is_weekday,
        d.is_holiday,
        SUM(sc.net_amount) AS daily_revenue,
        SUM(sc.quantity) AS daily_units,
        SUM(sc.margin_amount) AS daily_profit,
        COUNT(*) AS transaction_count
    FROM
        {{ ref('stg_sales_clean') }} sc
    LEFT JOIN
        {{ ref('stg_date_clean')}} d
    ON
        sc.sale_date = d.date_value
    WHERE
        sc.is_return = FALSE
    GROUP BY
        sc.sale_date,
        d.year,
        d.quarter,
        d.month,
        d.day_of_week,
        d.is_weekend,
        d.is_holiday
)

-- CTE 2: Calculation (Window Functions)
, sales_comparisons AS (
    SELECT
    sale_date,
    year_quarter,
    year_month,
    day_of_week,
    is_weekday,
    is_holiday,
    daily_revenue,
    daily_units,
    daily_profit,
    transaction_count,
    AVG(daily_revenue) OVER (ORDER BY sale_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS revenue_moving_average_7day,
    AVG(daily_revenue) OVER (ORDER BY sale_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) AS revenue_moving_average_30day,
    LAG(daily_revenue) OVER (ORDER BY sale_date) AS prior_day_revenue,
    ROW_NUMBER() OVER (PARTITION BY day_of_week ORDER BY daily_revenue DESC) AS weekday_rank
    FROM
    daily_sales
)

-- CTE 3: Enrichment (Segment)
SELECT
    sale_date,
    year_quarter,
    year_month,
    day_of_week,
    is_weekday,
    is_holiday,
    daily_revenue,
    daily_units,
    daily_profit,
    transaction_count,
    revenue_moving_average_7day,
    revenue_moving_average_30day,
    ROUND((daily_revenue) / NULLIF(revenue_moving_average_7day, 0) * 100, 2) AS revenue_vs_weekly_avg,
    prior_day_revenue,
    ROUND((daily_revenue - prior_day_revenue) / NULLIF(prior_day_revenue, 0) * 100, 2) AS revenue_growth_pct,
    weekday_rank,
    CASE
        WHEN is_holiday = TRUE THEN 'Holiday'
        WHEN NOT is_weekday THEN 'Weekend'
        ELSE 'Weekday'
    END AS day_type,
    CURRENT_TIMESTAMP() AS _loaded_at
FROM
    sales_comparisons
