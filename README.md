# LCV Retail Analytics Platform

A comprehensive **end-to-end data warehouse and analytics platform** designed to simulate LC Waikiki's (LCV) global retail operations. This project demonstrates advanced data engineering, analytics, and machine learning skills aligned with enterprise-scale data platforms.

---

## 🎯 Project Overview

**Objective:** Build a production-grade analytics platform that transforms raw transactional data from retail sources into actionable business intelligence and predictive insights.

**Context:** LC Waikiki operates 1,300+ stores across 60+ countries. This project simulates their data flow and builds the kind of analytics infrastructure they rely on for decision-making.

**Scope:**
- **Source System**: Mock Point-of-Sale (POS) data in PostgreSQL
- **Data Warehouse**: Google BigQuery with star schema
- **Transformations**: dbt for ETL/ELT pipelines
- **Analytics**: SQL views for KPI calculations
- **BI Dashboard**: Looker Studio for visualization
- **ML Model**: Churn prediction + Demand forecasting API
- **Governance**: Data dictionary, lineage, quality checks

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL (Source)                       │
│  FactSales | DimProduct | DimStore | DimDate | DimCustomer  │
└────────────────┬────────────────────────────────────────────┘
                 │ Extract
                 ▼
┌─────────────────────────────────────────────────────────────┐
│            Google Cloud Storage (GCS - Staging)             │
│            Parquet files (daily batches)                     │
└────────────────┬────────────────────────────────────────────┘
                 │ Load
                 ▼
┌─────────────────────────────────────────────────────────────┐
│         Google BigQuery (Data Warehouse)                     │
│  Raw Layer    │    Staging Layer    │    Mart Layer          │
│  (raw_sales)  │ (stg_sales_clean)   │ (fct_sales_v2)        │
└────────────────┬────────────────────────────────────────────┘
                 │ Transform (dbt)
                 ▼
┌─────────────────────────────────────────────────────────────┐
│            Analytic Views (Consumption Layer)               │
│  YoY Growth | RFM Scores | Churn Risk | Forecasts           │
└────────────────┬────────────────────────────────────────────┘
                 │
      ┌──────────┼──────────┐
      ▼          ▼          ▼
    [BI]      [ML API]    [Exports]
  Looker    Churn/Demand   Reports
  Studio    Predictions
```

---

## 📊 Key Features

### 1. **Data Modeling** (Week 1)
- **Star Schema**: FactSales + Dimension tables (Product, Store, Date, Customer)
- **Slowly Changing Dimensions (SCD)**: Handle product price/store location changes
- **Normalized OLTP** + **Denormalized Analytics** structures
- Full ERD documentation

### 2. **Advanced SQL** (Week 1–2)
- Year-over-Year (YoY) sales growth analysis
- Customer segmentation via RFM (Recency, Frequency, Monetary)
- Inventory turnover by product category
- Churn detection (inactive customers)
- Window functions, CTEs, query optimization

### 3. **ETL/ELT Pipeline** (Week 2–3)
- Extract data from Postgres → Cloud Storage (Parquet)
- Load into BigQuery raw layer (daily ingestion)
- dbt transformations: staging → marts
- Data quality checks (duplicates, nulls, referential integrity)

### 4. **Performance & Cost Optimization** (Week 2–3)
- Partition FactSales by `sale_date` (reduce scanned bytes)
- Clustering by `store_id` + `product_id` (faster aggregations)
- Query cost benchmarking and improvements
- Documentation of optimization wins

### 5. **BI Dashboard** (Week 4)
- **Sales Performance**: Total revenue, trend analysis, regional breakdown
- **Customer Metrics**: Acquisition, retention, lifetime value (CLV)
- **Inventory Insights**: Turnover rates, stockouts, reorder levels
- **KPI Tracking**: Define business metrics (e.g., "Sell-through Rate", "Inventory Days")

### 6. **Churn Prediction** (Week 5)
- **Behavioral Churn**: Flag inactive customers (no purchase in 90+ days)
- **ML Model**: Logistic Regression / Random Forest to predict churn probability
- **FastAPI Endpoint**: `/churn-risk?customer_id=123` for real-time predictions
- Feature engineering: RFM, purchase trend, loyalty program status

### 7. **Demand Forecasting** (Week 5)
- Predict next month's sales by product/store
- Time-series or ensemble model (ARIMA / Prophet / XGBoost)
- API endpoint for integration with planning systems

---

## 📁 Project Structure

```
lcv-retail-analytics-platform/
├── .gitignore                      # Git ignore rules
├── README.md                       # This file
├── ROADMAP.md                      # 5-week detailed plan
├── GOVERNANCE.md                   # Data dictionary & lineage
│
├── SCHEMA/
│   ├── star_schema.sql             # Star schema DDL
│   ├── erd_diagram.png             # Entity-Relationship Diagram
│   └── data_dictionary.md          # Column definitions & lineage
│
├── src/
│   ├── postgres/
│   │   ├── init.sql                # Schema setup
│   │   └── seed_synthetic_data.py  # Generate test data
│   │
│   ├── etl/
│   │   ├── postgres_to_gcs.py      # Extract & load to GCS
│   │   ├── dbt_project/            # dbt models (transformations)
│   │   │   ├── models/
│   │   │   │   ├── staging/        # Raw → Clean
│   │   │   │   └── marts/          # Analytics-ready tables
│   │   │   └── dbt_project.yml
│   │   └── requirements.txt
│   │
│   ├── analytics/
│   │   ├── views.sql               # KPI views & analysis queries
│   │   └── kpi_definitions.md      # Business logic for each KPI
│   │
│   └── ml/
│       ├── churn_model.py          # Churn prediction model
│       ├── demand_forecast.py      # Demand forecasting model
│       ├── api.py                  # FastAPI endpoints
│       └── requirements.txt
│
├── dashboards/
│   ├── looker_studio_config.md     # Dashboard setup guide
│   └── queries.sql                 # Pre-built dashboard queries
│
├── tests/
│   ├── data_quality_checks.py      # dbt tests + custom checks
│   └── test_ml_models.py           # Model performance tests
│
└── docs/
    ├── ARCHITECTURE.md             # System design decisions
    └── PERFORMANCE_LOG.md          # Query optimization results
```

---

## 🚀 Quick Start

### Prerequisites
- PostgreSQL 12+
- Python 3.9+
- Google Cloud account (free tier for BigQuery)
- Git

### Local Setup

```bash
# Clone and navigate
cd lcv-retail-analytics-platform

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL
psql -U postgres -f SCHEMA/star_schema.sql

# Generate synthetic data
python src/postgres/seed_synthetic_data.py

# Run ETL pipeline (local testing)
python src/etl/postgres_to_gcs.py --local

# Run dbt transformations
cd src/etl/dbt_project
dbt run
dbt test
```

### BigQuery Setup

```bash
# Create BigQuery dataset
bq mk --dataset --location=US retail_analytics

# Load sample data
bq load --source_format=PARQUET retail_analytics.raw_sales gs://your-bucket/sales/*.parquet

# Transform with dbt
dbt run --profiles-dir .
```

---

## 📈 Skills Demonstrated

| Requirement (LCW Job Description) | How This Project Shows It |
|---|---|
| **Advanced SQL** | Complex queries: window functions, CTEs, performance tuning with indexes |
| **Data Modeling** | Star schema + normalized OLTP; conceptual → logical → physical models |
| **Cloud Platforms** | BigQuery, Cloud Storage, dbt; partitioning & clustering for cost optimization |
| **ETL/ELT Pipelines** | Postgres → GCS → BigQuery; dbt transformations; daily automation |
| **Analytics Products** | Looker Studio dashboards; clear KPI definitions; business-focused insights |
| **Data Governance** | Data dictionary, lineage tracking, quality checks, SCD handling |
| **AI Integration** | Churn prediction + demand forecasting APIs; feature engineering for ML |

---

## 📊 Datasets

**Synthetic Data Scope** (for demo):
- **Stores**: 50 locations (1–50 store_id)
- **Products**: 500 products (categories: textile, accessories, footwear)
- **Customers**: 10,000 unique customers
- **Time Range**: 24 months of transaction history
- **Transaction Volume**: ~1M sales records

This is enough to demonstrate performance optimization and pattern analysis without needing real LCV data.

---

## 🔐 Data Governance

- **Data Dictionary**: Column definitions, data types, and business logic ([GOVERNANCE.md](GOVERNANCE.md))
- **Lineage**: Source → Staging → Marts tracking in dbt
- **Quality Checks**: dbt tests + custom Python validations
- **SCD Handling**: Type 2 (track history) for product prices and store attributes

---

## 🎓 Learning Outcomes

After completing this project, you will have hands-on experience with:
- ✅ Enterprise data warehouse design
- ✅ Cloud data platform development (GCP)
- ✅ SQL optimization for cost and performance
- ✅ ETL/ELT pipeline orchestration
- ✅ BI and dashboard design
- ✅ End-to-end ML model deployment
- ✅ Data governance and documentation

---

## 📅 Timeline

- **Week 1**: Data modeling + SQL (5 working days)
- **Week 2**: ETL pipeline + transformations (5 working days)
- **Week 3**: BigQuery + performance optimization (5 working days)
- **Week 4**: BI dashboards + KPIs (5 working days)
- **Week 5**: ML models + API + documentation (5 working days)

**Effort**: ~3 hours/day = **~75 hours total**

---

## 🔗 Documentation

- [ROADMAP.md](ROADMAP.md) — Detailed week-by-week plan
- [GOVERNANCE.md](GOVERNANCE.md) — Data dictionary & lineage
- [SCHEMA/](SCHEMA/) — Data modeling details
- [src/analytics/kpi_definitions.md](src/analytics/kpi_definitions.md) — Business metric definitions

---

## 👤 Author

Built as a portfolio project to demonstrate data engineering + analytics skills for LC Waikiki (LCW) opportunities.

---

## 📝 License

MIT

---

**Status**: 🚀 In Progress (Week 1 starting soon)

*Last Updated: February 14, 2026*
