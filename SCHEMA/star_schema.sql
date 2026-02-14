-- LCV Retail Analytics Platform
-- Star Schema (Dimensional Model)
-- PostgreSQL DDL

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

-- 1. Date Dimension (pre-populated for 2023-2025)
CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,
    date_value DATE NOT NULL UNIQUE,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    week_of_year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    quarter INTEGER NOT NULL,
    fiscal_quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    fiscal_year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_holiday BOOLEAN DEFAULT FALSE,
    holiday_name VARCHAR(100)
);

-- 2. Product Dimension (with SCD Type 2 support)
CREATE TABLE IF NOT EXISTS dim_product (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    product_code VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    color VARCHAR(50),
    size VARCHAR(20),
    material VARCHAR(100),
    season VARCHAR(20),
    brand VARCHAR(100),
    unit_cost DECIMAL(10, 2) NOT NULL,
    list_price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    scd_start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    scd_end_date DATE,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for SCD lookups
CREATE INDEX idx_dim_product_scd ON dim_product(product_id, scd_start_date, scd_end_date);
CREATE INDEX idx_dim_product_current ON dim_product(is_current);

-- 3. Store Dimension
CREATE TABLE IF NOT EXISTS dim_store (
    store_id INTEGER PRIMARY KEY,
    store_name VARCHAR(255) NOT NULL,
    store_code VARCHAR(50) NOT NULL UNIQUE,
    region VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(10, 8),
    store_type VARCHAR(50) NOT NULL,
    opening_date DATE NOT NULL,
    closing_date DATE,
    store_manager VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    square_meters INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for common queries
CREATE INDEX idx_dim_store_region ON dim_store(region, country);
CREATE INDEX idx_dim_store_status ON dim_store(status);

-- 4. Customer Dimension (Optional, for loyalty analysis)
CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id INTEGER PRIMARY KEY,
    loyalty_member BOOLEAN NOT NULL DEFAULT FALSE,
    join_date DATE,
    first_purchase_date DATE,
    last_purchase_date DATE,
    lifetime_purchases INTEGER DEFAULT 0,
    lifetime_spend DECIMAL(12, 2) DEFAULT 0,
    country VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- FACT TABLE
-- ============================================================

-- Central fact table: one row per transaction
CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    customer_id INTEGER,  -- NULL if non-loyalty customer
    sale_date DATE NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    discount_pct DECIMAL(5, 2),
    discount_amount DECIMAL(10, 2),
    net_amount DECIMAL(10, 2) NOT NULL,
    cost_amount DECIMAL(10, 2) NOT NULL,
    margin_amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    is_return BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign Keys
    CONSTRAINT fk_fact_sales_store FOREIGN KEY (store_id) REFERENCES dim_store(store_id),
    CONSTRAINT fk_fact_sales_product FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    CONSTRAINT fk_fact_sales_customer FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
);

-- Indexes for fact table (critical for performance)
CREATE INDEX idx_fact_sales_date ON fact_sales(sale_date);
CREATE INDEX idx_fact_sales_store ON fact_sales(store_id);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_id);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_id);
CREATE INDEX idx_fact_sales_store_product_date ON fact_sales(store_id, product_id, sale_date);

-- Constraint: quantity > 0
ALTER TABLE fact_sales ADD CONSTRAINT check_quantity_positive CHECK (quantity > 0);

-- Constraint: net_amount >= 0
ALTER TABLE fact_sales ADD CONSTRAINT check_net_amount_non_negative CHECK (net_amount >= 0);

-- Constraint: cost_amount > 0
ALTER TABLE fact_sales ADD CONSTRAINT check_cost_amount_positive CHECK (cost_amount > 0);

-- Constraint: margin = net - cost
ALTER TABLE fact_sales ADD CONSTRAINT check_margin_calculation
    CHECK (ABS((net_amount - cost_amount) - margin_amount) < 0.01);

-- ============================================================
-- ANALYTIC VIEWS
-- ============================================================

-- View 1: Daily Sales Summary
CREATE OR REPLACE VIEW v_sales_daily AS
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
    ROUND(SUM(fs.margin_amount) / NULLIF(SUM(fs.net_amount), 0) * 100, 2) as profit_margin_pct
FROM fact_sales fs
JOIN dim_store ds ON fs.store_id = ds.store_id
JOIN dim_product dp ON fs.product_id = dp.product_id
WHERE fs.is_return = FALSE
GROUP BY fs.sale_date, ds.region, ds.country, dp.category
ORDER BY fs.sale_date DESC, ds.region;

-- View 2: Customer RFM Segmentation
CREATE OR REPLACE VIEW v_rfm_segments AS
SELECT
    fs.customer_id,
    dc.loyalty_member,
    CURRENT_DATE::date - MAX(fs.sale_date) as recency_days,
    COUNT(DISTINCT fs.sale_id) as frequency_purchases,
    SUM(fs.net_amount) as monetary_value,
    -- Simple RFM scoring (1-5 scale)
    ROUND(5.0 - (CURRENT_DATE::date - MAX(fs.sale_date))::numeric / 90, 0)::int as recency_score,
    ROUND(LEAST(5, COUNT(DISTINCT fs.sale_id)::numeric / 10), 0)::int as frequency_score,
    ROUND(LEAST(5, SUM(fs.net_amount) / 500), 0)::int as monetary_score
FROM fact_sales fs
JOIN dim_customer dc ON fs.customer_id = dc.customer_id
WHERE fs.is_return = FALSE
GROUP BY fs.customer_id, dc.loyalty_member;

-- View 3: Churn Risk Detection (inactive customers)
CREATE OR REPLACE VIEW v_churn_risk AS
SELECT
    fs.customer_id,
    MAX(fs.sale_date) as last_purchase_date,
    CURRENT_DATE::date - MAX(fs.sale_date) as days_since_purchase,
    COUNT(DISTINCT fs.sale_id) as lifetime_purchases,
    SUM(fs.net_amount) as lifetime_spend,
    CASE
        WHEN CURRENT_DATE::date - MAX(fs.sale_date) > 90 THEN 'High Risk (>90 days)'
        WHEN CURRENT_DATE::date - MAX(fs.sale_date) > 60 THEN 'Medium Risk (60-90 days)'
        WHEN CURRENT_DATE::date - MAX(fs.sale_date) > 30 THEN 'Low Risk (30-60 days)'
        ELSE 'Active'
    END as churn_risk_category
FROM fact_sales fs
WHERE fs.is_return = FALSE
GROUP BY fs.customer_id
HAVING CURRENT_DATE::date - MAX(fs.sale_date) >= 30
ORDER BY days_since_purchase DESC;

-- View 4: Inventory Turnover by Category
CREATE OR REPLACE VIEW v_inventory_turnover AS
SELECT
    dp.category,
    dp.subcategory,
    COUNT(DISTINCT dp.product_id) as product_count,
    SUM(fs.quantity) as total_units_sold,
    SUM(fs.cost_amount) / NULLIF(COUNT(DISTINCT dp.product_id), 0) as avg_inventory_value,
    SUM(fs.cost_amount) / NULLIF(SUM(fs.cost_amount) / NULLIF(COUNT(DISTINCT dp.product_id), 0), 0) as turnover_ratio
FROM fact_sales fs
JOIN dim_product dp ON fs.product_id = dp.product_id
WHERE fs.is_return = FALSE
GROUP BY dp.category, dp.subcategory
ORDER BY turnover_ratio DESC;

-- View 5: Store Performance Ranking
CREATE OR REPLACE VIEW v_store_ranking AS
SELECT
    ds.store_id,
    ds.store_name,
    ds.region,
    ds.country,
    COUNT(DISTINCT fs.sale_id) as sales_count,
    SUM(fs.net_amount) as total_revenue,
    SUM(fs.margin_amount) as total_profit,
    ROUND(SUM(fs.margin_amount) / NULLIF(SUM(fs.net_amount), 0) * 100, 2) as profit_margin_pct,
    COUNT(DISTINCT fs.customer_id) as unique_customers,
    SUM(fs.quantity) as units_sold,
    ROUND(SUM(fs.net_amount) / NULLIF(COUNT(DISTINCT fs.sale_id), 0), 2) as avg_transaction_value,
    ROW_NUMBER() OVER (PARTITION BY ds.region ORDER BY SUM(fs.net_amount) DESC) as rank_in_region
FROM fact_sales fs
JOIN dim_store ds ON fs.store_id = ds.store_id
WHERE fs.is_return = FALSE
GROUP BY ds.store_id, ds.store_name, ds.region, ds.country
ORDER BY total_revenue DESC;

-- ============================================================
-- HELPER FUNCTIONS
-- ============================================================

-- Function to calculate customer churn risk score (0-100)
CREATE OR REPLACE FUNCTION calculate_churn_score(
    p_recency_days INTEGER,
    p_frequency_purchases INTEGER,
    p_monetary_value DECIMAL
) RETURNS INTEGER AS $$
DECLARE
    v_recency_score INTEGER;
    v_frequency_score INTEGER;
    v_monetary_score INTEGER;
    v_total_score DECIMAL;
BEGIN
    -- Recency: higher days = higher churn risk
    v_recency_score := LEAST(100, GREATEST(0, (p_recency_days - 30) * 2));

    -- Frequency: lower purchases = higher churn risk
    v_frequency_score := LEAST(100, GREATEST(0, (10 - p_frequency_purchases) * 5));

    -- Monetary: lower spend = higher churn risk
    v_monetary_score := LEAST(100, GREATEST(0, (1000 - p_monetary_value) / 10));

    -- Weighted average
    v_total_score := (v_recency_score * 0.5) + (v_frequency_score * 0.3) + (v_monetary_score * 0.2);

    RETURN ROUND(v_total_score)::INTEGER;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================
-- SAMPLE QUERIES FOR TESTING
-- ============================================================

-- Query 1: YoY Sales Growth
-- SELECT
--     EXTRACT(YEAR FROM fs.sale_date) as year,
--     EXTRACT(MONTH FROM fs.sale_date) as month,
--     SUM(fs.net_amount) as revenue,
--     LAG(SUM(fs.net_amount)) OVER (PARTITION BY EXTRACT(MONTH FROM fs.sale_date) ORDER BY EXTRACT(YEAR FROM fs.sale_date)) as prev_year_revenue,
--     ROUND((SUM(fs.net_amount) - LAG(SUM(fs.net_amount)) OVER (PARTITION BY EXTRACT(MONTH FROM fs.sale_date) ORDER BY EXTRACT(YEAR FROM fs.sale_date))) /
--            LAG(SUM(fs.net_amount)) OVER (PARTITION BY EXTRACT(MONTH FROM fs.sale_date) ORDER BY EXTRACT(YEAR FROM fs.sale_date)) * 100, 2) as yoy_growth_pct
-- FROM fact_sales fs
-- WHERE fs.is_return = FALSE
-- GROUP BY EXTRACT(YEAR FROM fs.sale_date), EXTRACT(MONTH FROM fs.sale_date)
-- ORDER BY year, month;

-- Query 2: Customer Lifetime Value (CLV)
-- SELECT
--     fs.customer_id,
--     COUNT(DISTINCT fs.sale_id) as purchase_count,
--     SUM(fs.net_amount) as lifetime_value,
--     AVG(fs.net_amount) as avg_transaction_value,
--     MIN(fs.sale_date) as first_purchase,
--     MAX(fs.sale_date) as last_purchase,
--     (MAX(fs.sale_date) - MIN(fs.sale_date)) as days_as_customer
-- FROM fact_sales fs
-- WHERE fs.is_return = FALSE
-- GROUP BY fs.customer_id
-- ORDER BY lifetime_value DESC;

-- ✅ Star schema created successfully!
