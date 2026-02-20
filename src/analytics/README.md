# Analytics Module

This module contains SQL views and KPI definitions for reporting, dashboards, and business intelligence.

---

## 📦 Contents

- `queries.sql` – Reusable SQL queries for analytics
- KPI definitions and metrics
- Dashboard query library

---

## 🚀 Quick Start

### Prerequisites

- PostgreSQL or BigQuery database with [ETL pipeline](../etl/README.md) run
- SQL client (psql, BigQuery Console, or DBeaver)
- Familiarity with the [data schema](../postgres/README.md#-generated-schema)

### Access Analytics

**PostgreSQL (Local Dev)**

```bash
psql -h localhost -U your_username -d lcv_retail_db
SELECT * FROM public."fact_sales" LIMIT 10;
```

**BigQuery (Cloud)**

```bash
bq query --use_legacy_sql=false "
  SELECT * FROM \`your_project.retail_analytics.fact_sales\` LIMIT 10
"
```

---

## 📊 Key Metrics

### Sales Metrics

- **Total Revenue**: Sum of net sales amounts
- **Gross Margin**: (Revenue - COGS) / Revenue
- **Discount Rate**: Sum of discounts / Sum of gross sales
- **Return Rate**: Count of returns / Count of all sales
- **Avg Transaction Value**: Total revenue / Number of transactions

### Store Metrics

- **Sales by Region**: Regional performance breakdown
- **Sales by Store Type**: Flagship vs Standard vs Pop-up performance
- **Store Footfall** (implied): Transaction count by store
- **Sales per Square Meter**: Revenue / store square footage

### Product Metrics

- **Top Products**: Revenue, units sold, margin contribution
- **Category Performance**: Sales by product category
- **Seasonality**: Sales patterns by season
- **Price Elasticity**: Units sold vs discount %

### Customer Metrics

- **Customer Lifetime Value (CLV)**: Total spend per customer
- **Loyalty Rate**: % of loyalty members
- **Repeat Purchase Rate**: Customers with 2+ transactions
- **Churn Rate**: Customers with no recent purchases

---

## 📈 Common Queries

### Sale Trends Over Time

```sql
SELECT
  DATE_TRUNC('month', sale_date::date) AS month,
  SUM(net_amount) AS monthly_revenue,
  COUNT(*) AS transaction_count
FROM fact_sales
GROUP BY DATE_TRUNC('month', sale_date::date)
ORDER BY month DESC;
```

### Top 10 Products by Revenue

```sql
SELECT
  p.product_name,
  p.category,
  SUM(s.net_amount) AS total_revenue,
  COUNT(s.sale_id) AS units_sold,
  ROUND(SUM(s.margin_amount) / SUM(s.net_amount), 3) AS margin_pct
FROM fact_sales s
JOIN dim_product p ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 10;
```

### Customer Lifetime Value

```sql
SELECT
  c.customer_id,
  c.status,
  SUM(s.net_amount) AS lifetime_spend,
  COUNT(DISTINCT DATE(s.sale_date)) AS purchase_days,
  MAX(s.sale_date) AS last_purchase_date,
  CASE
    WHEN MAX(s.sale_date) < NOW() - INTERVAL '90 days' THEN 'Churned'
    ELSE 'Active'
  END AS customer_status
FROM dim_customer c
LEFT JOIN fact_sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.status
ORDER BY lifetime_spend DESC;
```

### Sales by Region and Store Type

```sql
SELECT
  s.region,
  s.store_type,
  COUNT(DISTINCT s.store_id) AS num_stores,
  SUM(f.net_amount) AS total_revenue,
  AVG(f.net_amount) AS avg_transaction,
  COUNT(*) AS transaction_count
FROM fact_sales f
JOIN dim_store s ON f.store_id = s.store_id
GROUP BY s.region, s.store_type
ORDER BY total_revenue DESC;
```

---

## 📊 Dashboard Integration

### Tableau / Looker Connection

```
Database: BigQuery (Google Cloud)
Project: your_project_id
Dataset: retail_analytics
Authentication: Service account JSON
```

### Power BI Connection

```
Server: bigquery.googleapis.com
Database: your_project_id.retail_analytics
Authentication: Microsoft Account → Google Service Account token
```

---

## 🔍 Data Quality Checks

### Row Counts

Verify expected data volumes:

```sql
SELECT 'fact_sales' AS table_name, COUNT(*) FROM fact_sales
UNION ALL
SELECT 'dim_customer', COUNT(*) FROM dim_customer
UNION ALL
SELECT 'dim_store', COUNT(*) FROM dim_store
UNION ALL
SELECT 'dim_product', COUNT(*) FROM dim_product
UNION ALL
SELECT 'dim_date', COUNT(*) FROM dim_date;
```

### Null Checks

```sql
SELECT
  COUNT(CASE WHEN sale_id IS NULL THEN 1 END) AS null_sale_id,
  COUNT(CASE WHEN store_id IS NULL THEN 1 END) AS null_store_id,
  COUNT(CASE WHEN product_id IS NULL THEN 1 END) AS null_product_id,
  COUNT(CASE WHEN net_amount IS NULL THEN 1 END) AS null_net_amount
FROM fact_sales;
```

### Referential Integrity

```sql
-- Check all store_ids in fact_sales exist in dim_store
SELECT COUNT(*) AS orphaned_records
FROM fact_sales f
WHERE NOT EXISTS (SELECT 1 FROM dim_store s WHERE s.store_id = f.store_id);
```

---

## 📁 Query Organization

Organize queries by domain:

- `sales_metrics.sql` – Revenue, margin, discount analysis
- `store_metrics.sql` – Store performance, regional analysis
- `product_metrics.sql` – Product performance, category trends
- `customer_metrics.sql` – CLV, loyalty, churn analysis
- `anomaly_detection.sql` – Outliers and data quality flags

---

## 📝 Notes

- All queries are written to be **database-agnostic** (PostgreSQL and BigQuery compatible)
- Use **CTEs (WITH clauses)** for readability and reusability
- Add **comments** to complex logic
- Test queries on **small date ranges** before running on full dataset
- Use **EXPLAIN PLAN** to optimize slow queries
