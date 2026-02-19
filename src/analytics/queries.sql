-- LCV Retail Analytics Platform
-- Advanced SQL Queries for Week 1
-- Optimized queries for retail analytics and reporting

-- ============================================================
-- QUERY 1: Year-over-Year (YoY) Sales Growth
-- ============================================================
-- Compares sales performance month-by-month across years
-- Use case: Analyze growth trends, identify seasonality

CREATE OR REPLACE VIEW v_yoy_sales_growth AS
SELECT
    EXTRACT(YEAR FROM fs.sale_date) as year,
    EXTRACT(MONTH FROM fs.sale_date) as month,
    TO_CHAR(fs.sale_date, 'Month') as month_name,
    SUM(fs.net_amount) as monthly_revenue,
    LAG(SUM(fs.net_amount)) OVER (
        PARTITION BY EXTRACT(MONTH FROM fs.sale_date)
        ORDER BY EXTRACT(YEAR FROM fs.sale_date)
    ) as prev_year_revenue,
    ROUND(
        (SUM(fs.net_amount) - LAG(SUM(fs.net_amount)) OVER (
            PARTITION BY EXTRACT(MONTH FROM fs.sale_date)
            ORDER BY EXTRACT(YEAR FROM fs.sale_date)
        )) / LAG(SUM(fs.net_amount)) OVER (
            PARTITION BY EXTRACT(MONTH FROM fs.sale_date)
            ORDER BY EXTRACT(YEAR FROM fs.sale_date)
        ) * 100,
        2
    ) as yoy_growth_pct,
    COUNT(*) as transaction_count,
    SUM(fs.quantity) as units_sold
FROM fact_sales fs
WHERE fs.is_return = FALSE
GROUP BY
    EXTRACT(YEAR FROM fs.sale_date),
    EXTRACT(MONTH FROM fs.sale_date),
    TO_CHAR(fs.sale_date, 'Month')
ORDER BY year DESC, month ASC;

-- Query: Get current year vs last year
-- SELECT * FROM v_yoy_sales_growth WHERE year IN (2024, 2025) ORDER BY month, year DESC;


-- ============================================================
-- QUERY 2: RFM Segmentation (Recency, Frequency, Monetary)
-- ============================================================
-- Segments customers based on purchase behavior
-- Use case: Identify VIP customers, at-risk segments, engagement targeting

CREATE OR REPLACE VIEW v_rfm_customer_segments AS
SELECT
    fs.customer_id,
    dc.loyalty_member,
    CURRENT_DATE::date - MAX(fs.sale_date) as recency_days,
    COUNT(DISTINCT fs.sale_id) as frequency_purchases,
    SUM(fs.net_amount) as monetary_value,

    -- RFM Scores (1-5 scale, where 5 is best)
    ROUND(LEAST(5, GREATEST(1, 5 - ((CURRENT_DATE::date - MAX(fs.sale_date))::numeric / 100))), 0)::int as recency_score,
    ROUND(LEAST(5, COUNT(DISTINCT fs.sale_id)::numeric / 50), 0)::int as frequency_score,
    ROUND(LEAST(5, SUM(fs.net_amount) / 1000), 0)::int as monetary_score,

    -- Combined RFM Score
    ROUND(LEAST(5, (
        ROUND(LEAST(5, GREATEST(1, 5 - ((CURRENT_DATE::date - MAX(fs.sale_date))::numeric / 100))), 0) +
        ROUND(LEAST(5, COUNT(DISTINCT fs.sale_id)::numeric / 50), 0) +
        ROUND(LEAST(5, SUM(fs.net_amount) / 1000), 0)
    ) / 3), 1) as rfm_combined_score,

    -- Customer Segment (based on combined score)
    CASE
        WHEN (
            ROUND(LEAST(5, GREATEST(1, 5 - ((CURRENT_DATE::date - MAX(fs.sale_date))::numeric / 100))), 0) +
            ROUND(LEAST(5, COUNT(DISTINCT fs.sale_id)::numeric / 50), 0) +
            ROUND(LEAST(5, SUM(fs.net_amount) / 1000), 0)
        ) / 3 >= 4.0 THEN 'VIP (Champions)'
        WHEN (
            ROUND(LEAST(5, GREATEST(1, 5 - ((CURRENT_DATE::date - MAX(fs.sale_date))::numeric / 100))), 0) +
            ROUND(LEAST(5, COUNT(DISTINCT fs.sale_id)::numeric / 50), 0) +
            ROUND(LEAST(5, SUM(fs.net_amount) / 1000), 0)
        ) / 3 >= 3.0 THEN 'Core (Regular)'
        WHEN (
            ROUND(LEAST(5, GREATEST(1, 5 - ((CURRENT_DATE::date - MAX(fs.sale_date))::numeric / 100))), 0) +
            ROUND(LEAST(5, COUNT(DISTINCT fs.sale_id)::numeric / 50), 0) +
            ROUND(LEAST(5, SUM(fs.net_amount) / 1000), 0)
        ) / 3 >= 2.0 THEN 'Developing'
        ELSE 'At-Risk'
    END as customer_segment
FROM fact_sales fs
JOIN dim_customer dc ON fs.customer_id = dc.customer_id
WHERE fs.is_return = FALSE AND fs.customer_id IS NOT NULL
GROUP BY fs.customer_id, dc.loyalty_member
ORDER BY rfm_combined_score DESC;

-- Query: Show VIP customers
-- SELECT customer_id, rcency_days, frequency_purchases, monetary_value, rfm_combined_score FROM v_rfm_customer_segments WHERE customer_segment = 'VIP (Champions)' LIMIT 50;


-- ============================================================
-- QUERY 3: Inventory Turnover by Product Category
-- ============================================================
-- Measures how quickly inventory moves
-- Use case: Identify fast/slow moving products, optimize stock

CREATE OR REPLACE VIEW v_inventory_turnover_analysis AS
SELECT
    dp.category,
    dp.subcategory,
    COUNT(DISTINCT dp.product_id) as product_count,
    SUM(fs.quantity) as total_units_sold,
    COUNT(DISTINCT fs.sale_id) as transaction_count,

    -- Cost metrics
    SUM(fs.cost_amount) as total_cost_of_goods_sold,
    AVG(fs.cost_amount / NULLIF(fs.quantity, 0)) as avg_unit_cost,

    -- Inventory calculation (simplified)
    SUM(fs.cost_amount) / NULLIF(COUNT(DISTINCT dp.product_id), 0) as avg_inventory_cost,

    -- Turnover ratio = COGS / Average Inventory
    ROUND(
        SUM(fs.cost_amount) / NULLIF(
            SUM(fs.cost_amount) / NULLIF(COUNT(DISTINCT dp.product_id), 0),
            0
        ),
        2
    ) as inventory_turnover_ratio,

    -- Days inventory outstanding
    ROUND(365 / NULLIF(
        SUM(fs.cost_amount) / NULLIF(
            SUM(fs.cost_amount) / NULLIF(COUNT(DISTINCT dp.product_id), 0),
            0
        ),
        0
    ), 0)::int as days_inventory_outstanding,

    -- Revenue metrics
    SUM(fs.net_amount) as total_revenue,
    ROUND(AVG(fs.net_amount / NULLIF(fs.quantity, 0)), 2) as avg_selling_price_per_unit,

    -- Profitability
    SUM(fs.margin_amount) as total_profit,
    ROUND(SUM(fs.margin_amount) / NULLIF(SUM(fs.net_amount), 0) * 100, 2) as profit_margin_pct
FROM fact_sales fs
JOIN dim_product dp ON fs.product_id = dp.product_id
WHERE fs.is_return = FALSE
GROUP BY dp.category, dp.subcategory
ORDER BY inventory_turnover_ratio DESC, total_revenue DESC;

-- Query: Find fast-moving categories
-- SELECT * FROM v_inventory_turnover_analysis WHERE inventory_turnover_ratio > 10 ORDER BY inventory_turnover_ratio DESC;

-- Query: Find slow-moving categories
-- SELECT * FROM v_inventory_turnover_analysis WHERE inventory_turnover_ratio < 2 ORDER BY days_inventory_outstanding DESC;


-- ============================================================
-- QUERY 4: Churn Risk Detection (Inactive Customers)
-- ============================================================
-- Identifies customers at risk of churning (>90 days inactive)
-- Use case: Retention campaigns, customer win-back initiatives

CREATE OR REPLACE VIEW v_churn_risk_detection AS
SELECT
    fs.customer_id,
    dc.loyalty_member,
    MAX(fs.sale_date) as last_purchase_date,
    CURRENT_DATE::date - MAX(fs.sale_date) as days_since_purchase,
    COUNT(DISTINCT fs.sale_id) as lifetime_purchases,
    SUM(fs.net_amount) as lifetime_spend,
    MIN(fs.sale_date) as first_purchase_date,

    -- Churn risk category
    CASE
        WHEN CURRENT_DATE::date - MAX(fs.sale_date) > 90 THEN 'High Risk (>90 days)'
        WHEN CURRENT_DATE::date - MAX(fs.sale_date) > 60 THEN 'Medium Risk (60-90 days)'
        WHEN CURRENT_DATE::date - MAX(fs.sale_date) > 30 THEN 'Low Risk (30-60 days)'
        ELSE 'Active'
    END as churn_risk_category,

    -- Risk score (0-100, where 100 is highest risk)
    LEAST(100, GREATEST(0, ROUND(
        ((CURRENT_DATE::date - MAX(fs.sale_date) - 30)::numeric / 180) * 100
    ))::int) as churn_risk_score,

    -- Customer lifetime
    (MAX(fs.sale_date) - MIN(fs.sale_date)) as days_as_customer,

    -- Purchase frequency (purchases per month)
    ROUND(
        COUNT(DISTINCT fs.sale_id)::numeric / NULLIF(
            (MAX(fs.sale_date) - MIN(fs.sale_date))::numeric / 30,
            0
        ),
        2
    ) as purchases_per_month,

    -- Average order value (AOV)
    ROUND(SUM(fs.net_amount) / NULLIF(COUNT(DISTINCT fs.sale_id), 0), 2) as avg_order_value
FROM fact_sales fs
JOIN dim_customer dc ON fs.customer_id = dc.customer_id
WHERE fs.is_return = FALSE
GROUP BY fs.customer_id, dc.loyalty_member
HAVING CURRENT_DATE::date - MAX(fs.sale_date) >= 30
ORDER BY days_since_purchase DESC;

-- Query: Get high-risk customers for immediate outreach
-- SELECT * FROM v_churn_risk_detection WHERE churn_risk_category = 'High Risk (>90 days)' ORDER BY lifetime_spend DESC LIMIT 100;

-- Query: Show churn risk by membership status
-- SELECT churn_risk_category, loyalty_member, COUNT(*) as customer_count, AVG(lifetime_spend) as avg_spend FROM v_churn_risk_detection GROUP BY churn_risk_category, loyalty_member ORDER BY churn_risk_category;


-- ============================================================
-- BONUS VIEWS: Store Performance & Daily Aggregations
-- ============================================================

-- Store Performance Rankings
CREATE OR REPLACE VIEW v_store_performance_ranking AS
SELECT
    ds.store_id,
    ds.store_name,
    ds.region,
    ds.country,
    ds.store_type,
    COUNT(DISTINCT fs.sale_id) as transaction_count,
    SUM(fs.net_amount) as total_revenue,
    SUM(fs.margin_amount) as total_profit,
    ROUND(SUM(fs.margin_amount) / NULLIF(SUM(fs.net_amount), 0) * 100, 2) as profit_margin_pct,
    COUNT(DISTINCT fs.customer_id) as unique_customers,
    SUM(fs.quantity) as units_sold,
    ROUND(SUM(fs.net_amount) / NULLIF(COUNT(DISTINCT fs.sale_id), 0), 2) as avg_transaction_value,
    ROW_NUMBER() OVER (PARTITION BY ds.region ORDER BY SUM(fs.net_amount) DESC) as rank_in_region,
    ROW_NUMBER() OVER (ORDER BY SUM(fs.net_amount) DESC) as rank_overall
FROM fact_sales fs
JOIN dim_store ds ON fs.store_id = ds.store_id
WHERE fs.is_return = FALSE
GROUP BY ds.store_id, ds.store_name, ds.region, ds.country, ds.store_type
ORDER BY total_revenue DESC;

-- Daily Sales Summary
CREATE OR REPLACE VIEW v_daily_sales_summary AS
SELECT
    fs.sale_date,
    ds.region,
    ds.country,
    dp.category,
    COUNT(*) as transaction_count,
    SUM(fs.quantity) as total_units_sold,
    SUM(fs.net_amount) as total_sales_revenue,
    SUM(fs.cost_amount) as total_cost,
    SUM(fs.margin_amount) as total_profit,
    ROUND(SUM(fs.margin_amount) / NULLIF(SUM(fs.net_amount), 0) * 100, 2) as profit_margin_pct,
    COUNT(DISTINCT fs.customer_id) as unique_customers,
    COUNT(DISTINCT fs.store_id) as stores_active
FROM fact_sales fs
JOIN dim_store ds ON fs.store_id = ds.store_id
JOIN dim_product dp ON fs.product_id = dp.product_id
WHERE fs.is_return = FALSE
GROUP BY fs.sale_date, ds.region, ds.country, dp.category
ORDER BY fs.sale_date DESC, ds.region;
