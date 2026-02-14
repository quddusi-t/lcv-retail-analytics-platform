# Data Governance & Lineage

LCV Retail Analytics Platform — Data Dictionary, Quality Rules, and Lineage Tracking

---

## 📋 Table of Contents

1. [Data Dictionary](#data-dictionary)
2. [Data Quality Rules](#data-quality-rules)
3. [Data Lineage](#data-lineage)
4. [Slowly Changing Dimensions (SCD)](#slowly-changing-dimensions)
5. [Access & Security](#access--security)

---

## 📚 Data Dictionary

### Source Layer (PostgreSQL - OLTP)

#### **Table: `fact_sales`**
Primary transactional fact table capturing every retail transaction.

| Column | Type | Key | Nullable | Definition |
|--------|------|-----|----------|-----------|
| `sale_id` | INT | PK | NO | Unique identifier for each transaction |
| `store_id` | INT | FK | NO | Reference to store (dim_store) |
| `product_id` | INT | FK | NO | Reference to product (dim_product) |
| `customer_id` | INT | FK | YES | Reference to customer; NULL for non-loyalty |
| `sale_date` | DATE | | NO | Date of transaction (YYYY-MM-DD) |
| `quantity` | INT | | NO | Units sold (must be >0) |
| `unit_price` | DECIMAL(10,2) | | NO | Price per unit at point of sale |
| `total_amount` | DECIMAL(10,2) | | NO | Quantity × Unit Price (before discount) |
| `discount_pct` | DECIMAL(5,2) | | YES | Discount percentage (0–100) |
| `discount_amount` | DECIMAL(10,2) | | YES | Discount in currency units |
| `net_amount` | DECIMAL(10,2) | | NO | Total amount - Discount (revenue) |
| `cost_amount` | DECIMAL(10,2) | | NO | COGS (cost of goods sold) |
| `margin_amount` | DECIMAL(10,2) | Calculated | NO | Net amount - Cost amount (profit) |
| `payment_method` | VARCHAR(20) | | NO | Credit card, Cash, Loyalty app, etc. |
| `is_return` | BOOLEAN | | NO | TRUE = return; FALSE = sale |
| `created_at` | TIMESTAMP | | NO | Record creation timestamp (UTC) |
| `updated_at` | TIMESTAMP | | NO | Last update timestamp |

**Calculated Columns** (for reference):
```
margin_amount = net_amount - cost_amount
```

---

#### **Table: `dim_product`**
Product dimension with slowly changing attributes.

| Column | Type | Key | Nullable | Definition |
|--------|------|-----|----------|-----------|
| `product_id` | INT | PK | NO | Unique product identifier |
| `product_name` | VARCHAR(255) | | NO | Product display name |
| `product_code` | VARCHAR(50) | UQ | NO | SKU / inventory code |
| `category` | VARCHAR(100) | | NO | Product category (Textile, Accessory, Footwear) |
| `subcategory` | VARCHAR(100) | | YES | Sub-classification |
| `color` | VARCHAR(50) | | YES | Primary color (e.g., Black, Navy Blue) |
| `size` | VARCHAR(20) | | YES | Size (XS, S, M, L, XL for textile; numeric for shoes) |
| `material` | VARCHAR(100) | | YES | Fabric/material type |
| `season` | VARCHAR(20) | | YES | Seasonal designation (Winter, Summer, All-Year) |
| `brand` | VARCHAR(100) | | YES | Brand name (if applicable) |
| `unit_cost` | DECIMAL(10,2) | | NO | Standard cost per unit (COGS basis) |
| `list_price` | DECIMAL(10,2) | | NO | Regular selling price |
| `status` | VARCHAR(20) | | NO | Active, Discontinued, Seasonal_Only |
| `scd_start_date` | DATE | | NO | When this version became effective (SCD Type 2) |
| `scd_end_date` | DATE | | YES | When this version ended (NULL = current) |
| `is_current` | BOOLEAN | | NO | TRUE = current record; FALSE = historical |

**Business Logic**:
- When `list_price` changes, create a new `dim_product` record with updated `scd_start_date`
- Historical analysis uses `scd_start_date` and `scd_end_date` to track product price evolution

---

#### **Table: `dim_store`**
Store dimension capturing location and performance attributes.

| Column | Type | Key | Nullable | Definition |
|--------|------|-----|----------|-----------|
| `store_id` | INT | PK | NO | Unique store identifier |
| `store_name` | VARCHAR(255) | | NO | Store display name |
| `store_code` | VARCHAR(50) | UQ | NO | Internal store code |
| `region` | VARCHAR(100) | | NO | Geographic region (e.g., North America, Europe) |
| `country` | VARCHAR(100) | | NO | Country code (TR, US, DE, etc.) |
| `city` | VARCHAR(100) | | NO | City name |
| `latitude` | DECIMAL(10,8) | | YES | Geographic latitude for mapping |
| `longitude` | DECIMAL(10,8) | | YES | Geographic longitude for mapping |
| `store_type` | VARCHAR(50) | | NO | Flagship, Outlet, Partner, etc. |
| `opening_date` | DATE | | NO | When store opened |
| `closing_date` | DATE | | YES | When store closed (NULL = active) |
| `store_manager` | VARCHAR(100) | | YES | Manager name (for accountability) |
| `status` | VARCHAR(20) | | NO | Active, Planning, Closed |
| `square_meters` | INT | | YES | Store floor space |

---

#### **Table: `dim_customer`** (Optional, for loyalty analysis)

| Column | Type | Key | Nullable | Definition |
|--------|------|-----|----------|-----------|
| `customer_id` | INT | PK | NO | Unique customer identifier |
| `loyalty_member` | BOOLEAN | | NO | Part of loyalty program? |
| `join_date` | DATE | | YES | When customer joined loyalty program |
| `first_purchase_date` | DATE | | NO | Customer's first ever purchase |
| `last_purchase_date` | DATE | | YES | Most recent purchase (updated nightly) |
| `lifetime_purchases` | INT | | NO | Total purchases in dataset |
| `lifetime_spend` | DECIMAL(12,2) | | NO | Total spend in dataset |
| `country` | VARCHAR(100) | | YES | Customer country (if available) |

---

### Analytics Layer (BigQuery - Warehouse)

#### **Staging: `stg_sales_clean`**
Cleaned, deduplicated sales data.

| Column | Definition |
|--------|-----------|
| All from `fact_sales` | + data quality validations |
| `_dbt_source_relation` | Source table lineage (comes from Postgres) |
| `_loaded_at` | When record was loaded to BigQuery |

**Quality Checks Applied**:
- No duplicate sale_ids
- quantity > 0
- net_amount ≥ 0
- cost_amount > 0
- margin_amount = net_amount - cost_amount

---

#### **Mart: `fct_sales_v2`**
Analytics-optimized fact table.

| Column | Type | Definition |
|--------|------|-----------|
| `sale_key` | INT | Surrogate key for optimization |
| `sale_id` | INT | Natural key |
| `product_id` | INT | Product reference |
| `store_id` | INT | Store reference |
| `customer_id` | INT | Customer reference |
| `date_id` | INT | Date dimension reference |
| `quantity` | INT | Units sold |
| `net_amount` | DECIMAL | Revenue (after discount) |
| `cost_amount` | DECIMAL | COGS |
| `margin_amount` | DECIMAL | Profit |

**Partitioning**: `sale_date` (daily)  
**Clustering**: `store_id`, `product_id`, `customer_id`

---

#### **Mart: `dim_product_final`**
Product dimension with SCD Type 2 support.

| Column | Type | Purpose |
|--------|------|---------|
| `product_id` | INT | Natural key |
| `product_name` | VARCHAR | Display |
| `category` | VARCHAR | Classification |
| `list_price` | DECIMAL | Regular price |
| `scd_start_date` | DATE | SCD Type 2: when version started |
| `scd_end_date` | DATE | SCD Type 2: when version ended |
| `is_current` | BOOLEAN | Flag for current version |

**Why SCD Type 2?**  
When a product's price changes, we preserve the historical price to accurately report margins on past transactions.

---

#### **Mart: `dim_store_final`**
Store dimension with hierarchy.

| Column | Type | Purpose |
|--------|------|---------|
| `store_id` | INT | Natural key |
| `store_name` | VARCHAR | Display |
| `region` | VARCHAR | Geographic rollup |
| `country` | VARCHAR | Second-level rollup |
| `city` | VARCHAR | Detail |

---

#### **Mart: `dim_date_final`**
Date dimension for time-based analysis.

| Column | Type | Purpose |
|--------|------|---------|
| `date_id` | INT | Surrogate key (YYYYMMDD format) |
| `date` | DATE | Calendar date |
| `day_of_week` | INT | 1–7 (Monday–Sunday) |
| `day_name` | VARCHAR | Monday, Tuesday, etc. |
| `week_of_year` | INT | Fiscal week number |
| `month` | INT | Month number (1–12) |
| `month_name` | VARCHAR | January, February, etc. |
| `quarter` | INT | 1–4 |
| `fiscal_quarter` | INT | LCV's fiscal quarters |
| `year` | INT | Calendar year |
| `fiscal_year` | INT | LCV's fiscal year |
| `is_weekend` | BOOLEAN | TRUE for Sat/Sun |

---

## 🔒 Data Quality Rules

### Source Validation (PostgreSQL)

**Rule 1: No Null Primary Keys**
```sql
-- All sale_id, store_id, product_id must be non-null
SELECT COUNT(*) FROM fact_sales WHERE sale_id IS NULL;  -- Should = 0
```

**Rule 2: Referential Integrity**
```sql
-- All store_id must exist in dim_store
SELECT COUNT(DISTINCT store_id) FROM fact_sales
WHERE store_id NOT IN (SELECT store_id FROM dim_store);  -- Should = 0
```

**Rule 3: Positive Quantities**
```sql
-- No negative or zero quantities
SELECT COUNT(*) FROM fact_sales WHERE quantity <= 0;  -- Should = 0
```

**Rule 4: Revenue >= 0**
```sql
-- No negative net amounts (after discount cannot exceed original)
SELECT COUNT(*) FROM fact_sales WHERE net_amount < 0;  -- Should = 0
```

**Rule 5: Cost > 0**
```sql
-- Cost of goods sold always positive
SELECT COUNT(*) FROM fact_sales WHERE cost_amount <= 0;  -- Should = 0
```

**Rule 6: No Duplicate Transactions**
```sql
-- sale_id must be unique
SELECT sale_id, COUNT(*) FROM fact_sales GROUP BY sale_id HAVING COUNT(*) > 1;  -- Should = 0
```

**Rule 7: Margin Logic**
```sql
-- Margin must equal net_amount - cost_amount (tolerance ±0.01)
SELECT COUNT(*) FROM fact_sales 
WHERE ABS((net_amount - cost_amount) - margin_amount) > 0.01;  -- Should = 0
```

### Warehouse Validation (BigQuery - dbt tests)

All quality checks are codified in dbt:

```yaml
# dbt_project/models/staging/staging.yml
version: 2

models:
  - name: stg_sales_clean
    tests:
      - dbt_utils.not_null_proportion:
          column_name: sale_id
          at_least: 1.0
      - dbt_utils.relationships:
          column_name: store_id
          to: table_name(dim_store)
          field: store_id
      - dbt_utils.accepted_values:
          column_name: payment_method
          values: ['credit_card', 'cash', 'loyalty_app', 'check']
```

---

## 📍 Data Lineage

### High-Level Flow

```
PostgreSQL (Transactional Source)
    ↓
    ├─ fact_sales (1M+ rows)
    ├─ dim_product (500 products)
    ├─ dim_store (50 stores)
    └─ dim_customer (10K customers)
    ↓
[Daily Batch Job: postgres_to_gcs.py]
    ↓
Google Cloud Storage (GCS) — Parquet files
    ├─ gs://lcv-bucket/sales/*.parquet
    ├─ gs://lcv-bucket/products/*.parquet
    └─ gs://lcv-bucket/stores/*.parquet
    ↓
[Load into BigQuery Raw Layer]
    ↓
BigQuery: retail_analytics_raw dataset
    ├─ raw_sales
    ├─ raw_products
    ├─ raw_stores
    └─ raw_customers
    ↓
[dbt Staging Models: stg_*_clean]
    ├─ Deduplication
    ├─ Type conversions
    ├─ Null handling
    └─ Quality checks
    ↓
BigQuery: retail_analytics_staging dataset
    ├─ stg_sales_clean
    ├─ stg_products_clean
    ├─ stg_stores_clean
    └─ stg_customers_clean
    ↓
[dbt Mart Models: fct_*, dim_*_final]
    ├─ Star schema joins
    ├─ Slowly changing dimension logic
    ├─ Aggregations
    └─ SCD Type 2 tracking
    ↓
BigQuery: retail_analytics_marts dataset
    ├─ fct_sales_v2
    ├─ dim_product_final
    ├─ dim_store_final
    ├─ dim_date_final
    └─ dim_customer_final
    ↓
[Analytics Layer: SQL Views]
    ├─ v_sales_by_region_daily
    ├─ v_churn_risk_customers
    ├─ v_rfm_segments
    ├─ v_inventory_turnover
    └─ v_customer_ltv
    ↓
[BI & ML Consumption]
    ├─ Looker Studio (Dashboards)
    ├─ FastAPI ML Endpoints (/churn-risk, /forecast)
    └─ Business Reports
```

### Column-Level Lineage Example

**How `margin_amount` flows through system:**

```
Postgres fact_sales.margin_amount (calculated)
    ↓ (ETL extraction)
GCS Parquet file: sales.parquet → margin_amount column
    ↓ (Load to BigQuery)
raw_sales.margin_amount
    ↓ (dbt staging: no change, just validation)
stg_sales_clean.margin_amount
    ↓ (dbt mart: alias into fct_sales_v2)
fct_sales_v2.margin_amount
    ↓ (Analytics: aggregation)
v_revenue_daily.total_margin (SUM of margin_amount by date)
    ↓ (BI retrieval)
Looker Studio: "Total Profit" widget
```

### Data Freshness SLA

| Dataset | Load Frequency | Refresh Schedule |
|---------|---|---|
| PostgreSQL (Source) | Real-time (OLTP) | Transactional |
| GCS (Staging) | Daily batch | 2 AM UTC |
| BigQuery raw layer | Daily batch | 2:15 AM UTC |
| dbt staging → marts | Daily batch | 2:30 AM UTC |
| Analytics views | Daily refresh | 3:00 AM UTC |
| BI Dashboard | Hourly (Looker Studio cache) | Auto-refresh |

---

## 🔄 Slowly Changing Dimensions (SCD)

### Why SCD Type 2?

**Scenario**: A textile product's list_price drops from 50 EUR to 35 EUR on March 1.

**Without SCD**: Historical transactions would show the new price, distorting margin analysis.

**With SCD Type 2**: We track both prices with effective date ranges.

### Implementation in dbt

```sql
-- dbt model: models/marts/dim_product_final.sql

SELECT
    product_id,
    product_name,
    category,
    list_price,
    scd_start_date,
    scd_end_date,
    CASE WHEN scd_end_date IS NULL THEN TRUE ELSE FALSE END AS is_current
FROM {{ ref('stg_products_clean') }}

-- In production, this would:
-- 1. Detect rows where list_price changed
-- 2. Set scd_end_date on old row to yesterday
-- 3. Insert new row with scd_start_date = today and scd_end_date = NULL
```

### Querying with SCD Type 2

```sql
-- Report on sales with product prices at time of sale
SELECT
    fs.sale_id,
    fs.sale_date,
    dp.product_name,
    dp.list_price,  -- Price on that day
    fs.unit_price,  -- Actual transaction price
    fs.margin_amount
FROM fct_sales_v2 fs
JOIN dim_product_final dp ON 
    fs.product_id = dp.product_id
    AND fs.sale_date BETWEEN dp.scd_start_date AND COALESCE(dp.scd_end_date, CURRENT_DATE)
WHERE fs.sale_date >= '2025-01-01';
```

---

## 🔐 Access & Security

### Role-Based Access Control (RBAC)

| Role | BigQuery Access | Purpose |
|------|---|---|
| `data_engineer` | All datasets (read/write) | Build & maintain pipelines |
| `analytics_engineer` | raw, staging (read); marts (read/write) | Transform data, monitor quality |
| `analyst` | marts, views (read only) | Query for insights |
| `bi_developer` | marts, views (read only) | Build dashboards |
| `data_scientist` | marts (read only) | Train ML models |
| `executive` | views, dashboards (read only) | High-level reporting |

### Sensitive Data Handling

**None** in this project (synthetic data only). But in production:

1. **PII (Personally Identifiable Information)**: Customer names, emails → Mask or exclude
2. **Financial Data**: Transaction amounts → Aggregate before sharing
3. **Audit Trail**: Track who accessed what, when

### Backup & Disaster Recovery

- BigQuery maintains automatic backups (automatic snapshots at 48-hour intervals)
- GCS data replicated across regions (standard replication)
- dbt models versioned in Git — can rebuild warehouse from scratch

---

## 📝 Governance Checklist

✅ **Data Dictionary**: Complete with business definitions  
✅ **Quality Rules**: SQL assertions for validating data  
✅ **Lineage Tracking**: Column-to-column flow documented  
✅ **SCD Strategy**: Product prices tracked historically  
✅ **Access Control**: Roles defined for different personas  
✅ **Freshness SLA**: Load schedules documented  
✅ **Backup & Recovery**: Disaster recovery approach noted  

---

**Last Updated**: February 14, 2026  
**Next Review**: After Week 1 (implementation of staging models)
