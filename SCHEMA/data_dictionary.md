# 📊 LCV Retail Analytics Platform — Data Dictionary

**Complete documentation of the star schema, business definitions, and data lineage.**

---

## Overview

This data warehouse follows a **star schema** dimensional model optimized for retail analytics. The schema consists of:
- **1 Fact Table**: `fact_sales` (transactions at granular level)
- **5 Dimension Tables**: Date, Product, Store, Customer, and supporting tables
- **6 Analytical Views**: Pre-calculated metrics ready for BI consumption

---

## Dimensional Model Architecture

### Star Schema Structure

```
                    dim_date
                        |
                        |
dim_store ------- fact_sales ------- dim_product
                        |
                        |
                   dim_customer
```

### Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Granularity** | One row per transaction (sale_id = grain) |
| **Additive Facts** | All measures in fact_sales are additive |
| **Slowly Changing Dimensions** | Product dimensions support SCD Type 2 |
| **Conformed Dimensions** | Shared date dimension across all facts |
| **Denormalization** | Dimension tables intentionally denormalized for query speed |

---

## Fact Table: `fact_sales`

**Business Definition**: Every transaction from point of sale (POS) systems across all LCV stores.

**Grain**: One row per individual sale transaction (uniquely identified by `sale_id`).

**Volume**: ~1,000,000 rows (based on synthetic data generation).

### Column Definitions

| Column | Data Type | Nullable | Business Definition | Constraints |
|--------|-----------|----------|---------------------|-------------|
| `sale_id` | INTEGER | NOT NULL | Unique transaction identifier | PRIMARY KEY |
| `store_id` | INTEGER | NOT NULL | Reference to store location | FK → dim_store |
| `product_id` | INTEGER | NOT NULL | Reference to product sold | FK → dim_product |
| `customer_id` | INTEGER | YES | Reference to loyalty member (NULL for non-members) | FK → dim_customer |
| `sale_date` | DATE | NOT NULL | Date of transaction | Non-NULL, indexed |
| `quantity` | INTEGER | NOT NULL | Units sold | CHECK > 0 |
| `unit_price` | DECIMAL(10,2) | NOT NULL | Price per unit at time of sale | Positive |
| `total_amount` | DECIMAL(10,2) | NOT NULL | Gross revenue (quantity × unit_price) | |
| `discount_pct` | DECIMAL(5,2) | YES | Discount percentage applied (0-100) | 0-100 range |
| `discount_amount` | DECIMAL(10,2) | YES | Absolute discount in currency | |
| `net_amount` | DECIMAL(10,2) | NOT NULL | Total after discount (total_amount - discount_amount) | CHECK >= 0 |
| `cost_amount` | DECIMAL(10,2) | NOT NULL | Product cost (COGS) | CHECK > 0 |
| `margin_amount` | DECIMAL(10,2) | NOT NULL | Profit (net_amount - cost_amount) | Validated: ABS(net - cost - margin) < 0.01 |
| `payment_method` | VARCHAR(20) | NOT NULL | How customer paid | Values: 'Cash', 'Credit Card', 'Debit Card', 'Mobile Pay' |
| `is_return` | BOOLEAN | NOT NULL | Is this a return transaction? | FALSE = sale, TRUE = return |
| `created_at` | TIMESTAMP | NOT NULL | Record creation timestamp | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP | NOT NULL | Last update timestamp | DEFAULT CURRENT_TIMESTAMP |

### Key Business Rules

- **Returns**: Negative quantities/amounts with `is_return = TRUE`
- **Margin Validation**: `margin_amount = net_amount - cost_amount` (within $0.01)
- **Non-Member Sales**: `customer_id` is NULL for cash transactions without loyalty enrollment
- **Null Dates**: Should never occur (data quality check)
- **Referential Integrity**: All FK relationships enforced at database level

### Performance Indexes

```sql
-- Fact table indexes (critical for query performance)
idx_fact_sales_date                    -- Daily aggregations
idx_fact_sales_store                   -- Store-level reporting
idx_fact_sales_product                 -- Product performance
idx_fact_sales_customer                -- Customer analytics
idx_fact_sales_store_product_date      -- Complex multi-dimensional queries
```

---

## Dimension Table: `dim_date`

**Business Definition**: Complete date dimension covering 2 years (730 days) in the past.

**Grain**: One row per calendar day.

**Pre-populated**: YES (populated at schema initialization)

### Column Definitions

| Column | Data Type | Business Definition | Example |
|--------|-----------|---------------------|---------|
| `date_id` | INTEGER PRIMARY KEY | Unique date identifier in YYYYMMDD format | 20250219 |
| `date_value` | DATE UNIQUE | Calendar date | 2025-02-19 |
| `day_of_week` | INTEGER | Day number (1=Monday, 7=Sunday) | 3 (Wednesday) |
| `day_name` | VARCHAR(20) | Full day name | 'Wednesday' |
| `week_of_year` | INTEGER | ISO week number | 8 |
| `month` | INTEGER | Month number (1-12) | 2 |
| `month_name` | VARCHAR(20) | Full month name | 'February' |
| `quarter` | INTEGER | Fiscal quarter (1-4) | 1 |
| `fiscal_quarter` | INTEGER | Fiscal quarter (can differ from calendar) | 1 |
| `year` | INTEGER | Calendar year | 2025 |
| `fiscal_year` | INTEGER | Fiscal year (can differ from calendar) | 2025 |
| `is_weekend` | BOOLEAN | Is this a weekend day? | TRUE/FALSE |
| `is_holiday` | BOOLEAN | Is this a holiday? | FALSE (not populated) |
| `holiday_name` | VARCHAR(100) | Name of holiday if applicable | NULL |

### Business Usage

- **Time-based filtering**: `WHERE sale_date >= date_trunc('month', CURRENT_DATE)`
- **Day-of-week analysis**: `GROUP BY dim_date.day_name` for weekday patterns
- **Fiscal period reporting**: Using fiscal_quarter/fiscal_year for company-specific periods
- **Holiday adjustments**: `is_holiday` flag for anomaly detection

---

## Dimension Table: `dim_store`

**Business Definition**: Every physical or logical retail location (store, warehouse, pop-up, etc.).

**Grain**: One row per unique store location.

**Slowly Changing**: Type 1 (overwrite) — location status changes update in-place

### Column Definitions

| Column | Data Type | Nullable | Business Definition | Example |
|--------|-----------|----------|---------------------|---------|
| `store_id` | INTEGER PRIMARY KEY | NOT NULL | Unique store identifier | 1, 2, 3, ..., 50 |
| `store_name` | VARCHAR(255) | NOT NULL | Human-readable store name | "Store 1 - North" |
| `store_code` | VARCHAR(50) UNIQUE | NOT NULL | Internal store code (POS system) | "ST0001" |
| `region` | VARCHAR(100) | NOT NULL | Geographic region | "North", "South", "East", "West", "Central" |
| `country` | VARCHAR(100) | NOT NULL | Country code or name | "USA" |
| `city` | VARCHAR(100) | NOT NULL | City where store is located | "New York" |
| `latitude` | DECIMAL(10,8) | YES | Geographic latitude | 40.7128 |
| `longitude` | DECIMAL(10,8) | YES | Geographic longitude | -74.0060 |
| `store_type` | VARCHAR(50) | NOT NULL | Type of store location | "Flagship", "Standard", "Express", "Pop-up" |
| `opening_date` | DATE | NOT NULL | Date store opened | 2020-01-15 |
| `closing_date` | DATE | YES | Date store closed (if applicable) | NULL (still open) |
| `store_manager` | VARCHAR(100) | YES | Current store manager name | "John Doe" |
| `status` | VARCHAR(20) | NOT NULL | Current operational status | "Active", "Inactive", "Closing Soon" |
| `square_meters` | INTEGER | YES | Store floor area in square meters | 5000 |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | 2024-01-01 12:00:00 |
| `updated_at` | TIMESTAMP | NOT NULL | Last record update time | 2025-02-19 10:30:00 |

### Business Definitions

- **store_id**: Immutable identifier (never changes)
- **store_type**: Impacts expected sales volume and customer demographics
- **status**: "Active" = open and transacting; "Inactive" = closed; "Closing Soon" = planned closure
- **Geographic fields**: Enable regional analysis and multi-store comparisons

### Indexes

```sql
idx_dim_store_region              -- Regional rollups
idx_dim_store_status              -- Filter by operational status
```

---

## Dimension Table: `dim_product`

**Business Definition**: Every SKU (Stock Keeping Unit) sold across all LCV locations.

**Grain**: One row per product (with SCD Type 2 support for price changes).

**Slowly Changing**: Type 2 (slowly changing) — price changes create new rows with valid date ranges

### Column Definitions

| Column | Data Type | Nullable | Business Definition | Example |
|--------|-----------|----------|---------------------|---------|
| `product_id` | INTEGER PRIMARY KEY | NOT NULL | Unique product identifier | 1, 2, 3, ..., 500 |
| `product_name` | VARCHAR(255) | NOT NULL | Product display name | "T-Shirt - Classic Blue" |
| `product_code` | VARCHAR(50) UNIQUE | NOT NULL | SKU code from inventory system | "PRD00001" |
| `category` | VARCHAR(100) | NOT NULL | High-level product category | "Textile", "Accessories", "Seasonal" |
| `subcategory` | VARCHAR(100) | YES | Subcategory for drill-down | "Dresses", "Hats", "Thermal" |
| `color` | VARCHAR(50) | YES | Product color | "Red", "Blue", "Black" |
| `size` | VARCHAR(20) | YES | Size dimension | "S", "M", "L", "XL" |
| `material` | VARCHAR(100) | YES | Material composition | "Cotton", "Polyester", "Wool" |
| `season` | VARCHAR(20) | YES | Season when product is sold | "Summer", "Winter", "Year-Round" |
| `brand` | VARCHAR(100) | YES | Brand or supplier | "Brand A", "Generic" |
| `unit_cost` | DECIMAL(10,2) | NOT NULL | Cost to acquire product | 10.00 |
| `list_price` | DECIMAL(10,2) | NOT NULL | Suggested retail price | 29.99 |
| `status` | VARCHAR(20) | NOT NULL | Product status | "Active", "Discontinued", "Coming Soon" |
| `scd_start_date` | DATE | NOT NULL | When this version became valid (SCD Type 2) | 2024-01-01 |
| `scd_end_date` | DATE | YES | When this version expired (SCD Type 2) | NULL (current) |
| `is_current` | BOOLEAN | NOT NULL | Is this the current valid version? | TRUE/FALSE |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | |
| `updated_at` | TIMESTAMP | NOT NULL | Last update time | |

### SCD Type 2 Example

When a product price changes, a new row is inserted:

```
product_id | product_name | list_price | scd_start_date | scd_end_date | is_current
-----------+--------------+------------+----------------+--------------+-----------
1          | T-Shirt      | 19.99      | 2024-01-01     | 2024-06-30   | FALSE
1          | T-Shirt      | 24.99      | 2024-07-01     | NULL         | TRUE
```

Queries joining to `dim_product` on `sale_date` will get the correct historical price.

### Indexes

```sql
idx_dim_product_scd                -- Lookups by valid date range
idx_dim_product_current            -- Quick filter for current products only
```

---

## Dimension Table: `dim_customer`

**Business Definition**: Customer loyalty program members and tracked purchasers.

**Grain**: One row per unique customer ID.

**Note**: Non-loyalty customers appear in fact_sales with `customer_id = NULL`

### Column Definitions

| Column | Data Type | Nullable | Business Definition | Example |
|--------|-----------|----------|---------------------|---------|
| `customer_id` | INTEGER PRIMARY KEY | NOT NULL | Unique customer identifier | 1, 2, 3, ..., 10000 |
| `loyalty_member` | BOOLEAN | NOT NULL | Is enrolled in loyalty program? | TRUE/FALSE |
| `join_date` | DATE | YES | Date joined loyalty program | 2023-01-15 |
| `first_purchase_date` | DATE | YES | Date of first purchase | 2023-01-15 |
| `last_purchase_date` | DATE | YES | Date of most recent purchase | 2025-02-15 |
| `lifetime_purchases` | INTEGER | YES | Total number of transactions | 42 |
| `lifetime_spend` | DECIMAL(12,2) | YES | Total spend to date | 1250.75 |
| `country` | VARCHAR(100) | YES | Customer's country | "USA" |
| `status` | VARCHAR(20) | NOT NULL | Customer status | "Active", "Inactive", "Churned" |
| `created_at` | TIMESTAMP | NOT NULL | Record creation time | |
| `updated_at` | TIMESTAMP | NOT NULL | Last update time | |

### Business Definitions

- **loyalty_member**: Only TRUE members have customer_id; non-members show NULL in fact_sales
- **lifetime_spend**: Calculated field updated after each transaction (for fast reporting)
- **status**: "Active" = purchased in last 30 days; "Churned" = >90 days inactive

---

## Analytical Views

Pre-built views for common analytical use cases. These should be refreshed nightly or on-demand.

### View 1: `v_yoy_sales_growth`

**Purpose**: Compare sales month-by-month across years to identify growth and seasonality.

**Key Columns**:
- `year, month, month_name`: Time period
- `monthly_revenue`: Net sales for the month
- `prev_year_revenue`: Same month previous year
- `yoy_growth_pct`: Percentage change year-over-year
- `transaction_count, units_sold`: Transaction volume metrics

**Use Case**: Executive dashboards, trend analysis, seasonal forecasting

### View 2: `v_rfm_customer_segments`

**Purpose**: Segment customers by Recency, Frequency, Monetary value for targeted marketing.

**Key Columns**:
- `customer_id, loyalty_member`: Customer identity
- `recency_days`: Days since last purchase
- `frequency_purchases`: Total transactions
- `monetary_value`: Total spend
- `recency_score, frequency_score, monetary_score`: Individual scores (1-5)
- `rfm_combined_score`: Average of 3 scores
- `customer_segment`: Classification (VIP, Core, Developing, At-Risk)

**Use Case**: Customer retention strategies, personalized marketing, loyalty programs

### View 3: `v_inventory_turnover_analysis`

**Purpose**: Measure how quickly products sell (inventory velocity).

**Key Columns**:
- `category, subcategory`: Product grouping
- `product_count`: Number of unique products
- `total_units_sold`: Units moved
- `inventory_turnover_ratio`: COGS / Average Inventory (higher = better)
- `days_inventory_outstanding`: Average time item sits in inventory
- `profit_margin_pct`: Category profitability

**Formula**: **Turnover Ratio = Total Cost of Goods Sold / Average Inventory Value**
- High ratio (>10): Fast-moving, good sell-through
- Low ratio (<2): Slow-moving, potential markdown candidates

**Use Case**: Merchandise planning, supply chain optimization, markdowns

### View 4: `v_churn_risk_detection`

**Purpose**: Identify customers at risk of churning (inactivity >30 days).

**Key Columns**:
- `customer_id, loyalty_member`: Customer identity
- `last_purchase_date`: When they last bought
- `days_since_purchase`: Days elapsed
- `churn_risk_category`: High/Medium/Low/Active
- `churn_risk_score`: 0-100 (100 = highest risk)
- `lifetime_spend, purchases_per_month`: Customer value metrics

**Use Case**: Retention campaigns, win-back initiatives, customer lifetime value prioritization

### View 5: `v_store_performance_ranking`

**Purpose**: Rank stores by revenue, profit, and efficiency metrics.

**Key Columns**:
- `store_id, store_name, region, country, store_type`: Store identity
- `total_revenue, total_profit, profit_margin_pct`: Financial metrics
- `rank_in_region, rank_overall`: Competitive rankings
- `avg_transaction_value, unique_customers`: Customer metrics

**Use Case**: Store management dashboards, regional performance reviews, incentive calculations

### View 6: `v_daily_sales_summary`

**Purpose**: Daily aggregations by store, region, and product category.

**Key Columns**:
- `sale_date, region, country, category`: Dimensions
- `transaction_count, units_sold, revenue, profit`: Metrics
- `unique_customers, stores_active`: Engagement metrics

**Use Case**: Daily business health dashboards, exception reporting, trend monitoring

---

## Data Quality Rules & Checks

### Fact Table (`fact_sales`)

| Rule | SQL | Severity |
|------|-----|----------|
| No negative quantities | `quantity > 0` | CRITICAL |
| No negative net amounts | `net_amount >= 0` | CRITICAL |
| Cost always positive | `cost_amount > 0` | CRITICAL |
| Margin calculation correct | `ABS((net_amount - cost_amount) - margin_amount) < 0.01` | CRITICAL |
| No orphaned store IDs | All store_id values exist in dim_store | CRITICAL |
| No orphaned product IDs | All product_id values exist in dim_product | CRITICAL |
| No duplicate sale IDs | sale_id is primary key | CRITICAL |
| Discount consistency | `discount_amount <= total_amount` | HIGH |
| Return flag consistency | `is_return = TRUE OR FALSE` (never NULL) | MEDIUM |

### Dimension Tables

| Check | Validity |
|-------|----------|
| No NULL primary keys | Each dimension has non-NULL PK |
| No duplicate codes | store_code, product_code, store_code globally unique |
| Valid date ranges | scd_start_date < scd_end_date (for SCD Type 2) |
| Status values valid | Only predefined status values allowed |

---

## Data Lineage

```
POS Systems (Physical Stores)
            ↓
Extract (ETL Job - Daily)
            ↓
Postgres (raw_sales, raw_products, raw_stores, raw_customers)
            ↓
Transform (dbt models - staging → marts)
            ↓
BigQuery Analytics Database
            ├─ View: v_yoy_sales_growth (BI Dashboards)
            ├─ View: v_rfm_customer_segments (Marketing)
            ├─ View: v_inventory_turnover (Merchandising)
            ├─ View: v_churn_risk_detection (Retention)
            ├─ View: v_store_performance_ranking (Management)
            └─ View: v_daily_sales_summary (Operations)
            ↓
Looker Studio (Executive Dashboards)
```

---

## Business Metrics & KPIs

### Revenue Metrics

- **Total Revenue**: `SUM(net_amount WHERE is_return = FALSE)`
- **Revenue by Region**: `SUM(net_amount) GROUP BY region`
- **YoY Growth**: `(Current Year Revenue - Prior Year Revenue) / Prior Year Revenue * 100%`

### Profitability Metrics

- **Margin Amount**: `net_amount - cost_amount`
- **Margin %**: `SUM(margin_amount) / SUM(net_amount) * 100%`
- **COGS**: `SUM(cost_amount WHERE is_return = FALSE)`

### Customer Metrics

- **RFM Score**: Weighted combination of Recency, Frequency, Monetary
- **Customer LTV**: `SUM(net_amount) GROUP BY customer_id`
- **Churn Risk**: Customers with `days_since_purchase > 90`

### Inventory Metrics

- **Turnover Ratio**: `Total COGS / Average Inventory`
- **Days Inventory Outstanding**: `365 / Turnover Ratio`
- **Fast Movers**: Products with `turnover_ratio > 10`

### Store Metrics

- **Store Revenue**: `SUM(net_amount) GROUP BY store_id`
- **Units per Store**: `SUM(quantity) GROUP BY store_id`
- **Avg Transaction Value**: `SUM(net_amount) / COUNT(sale_id)`

---

## Refresh Cadence & SLAs

| Asset | Frequency | Latency SLA | Owner |
|-------|-----------|------------|-------|
| fact_sales | Nightly @ 1 AM UTC | <4 hours | Data Engineering |
| dim_store | Real-time | <1 hour | Operations |
| dim_product | Real-time | <1 hour | Merchandising |
| dim_customer | Nightly | <4 hours | CRM |
| Analytical Views | Nightly @ 2 AM UTC | <5 hours | Analytics |
| BI Dashboards | Every 30 mins | <30 mins | Data Viz |

---

## Related Documentation

- **Star Schema DDL**: See [SCHEMA/star_schema.sql](star_schema.sql)
- **SQL Queries**: See [src/analytics/queries.sql](../src/analytics/queries.sql)
- **ETL Pipeline**: See [src/etl/](../src/etl/)
- **dbt Models**: See [src/etl/dbt_project/](../src/etl/dbt_project/)
- **Governance**: See [GOVERNANCE.md](../GOVERNANCE.md)

---

**Last Updated**: February 19, 2026
**Version**: 1.0
**Status**: Production
