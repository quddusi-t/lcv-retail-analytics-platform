# LCV Retail Analytics Platform — 5-Week Development Roadmap

**Timeline**: 5 weeks @ ~3 hours/day = ~75 hours total
**Start Date**: February 15, 2026
**Target Completion**: March 21, 2026

---

## 📋 Executive Summary

This roadmap breaks down the end-to-end data platform build into five focused weeks. Each week builds on the previous, progressing from **data modeling** → **ETL** → **warehouse** → **analytics** → **AI integration**.

---

## **WEEK 1: Data Modeling & SQL Foundation**

### Goal
Design a production-grade star schema and master advanced SQL queries for retail analytics.

### Tasks

#### **Day 1–2: Schema Design & Documentation**
- [x] Review SCHEMA/star_schema.sql structure
- [ ] Create ERD (Entity-Relationship Diagram) — tables, relationships, keys (optional visualization)
- [x] Document **Conceptual Model** (business entities: Customer, Store, Product, Sale) — see data_dictionary.md
- [x] Document **Logical Model** (normalized structure + primary/foreign keys) — see data_dictionary.md
- [x] Document **Physical Model** (indexes, partitioning strategy) — see data_dictionary.md
- **Output**: `SCHEMA/data_dictionary.md` ✅, `src/analytics/queries.sql` ✅

#### **Day 3–4: Generate Synthetic Data**
- [x] Create `src/postgres/seed_synthetic_data.py`
- [x] Generate 50 stores across 5 regions
- [x] Generate 500 products (categories: textile, accessories, seasonal)
- [x] Generate 10,000 unique customers
- [x] Generate ~1M sales transactions (24 months)
- [x] Add returns, discounts, loyalty points
- **Output**: PostgreSQL database populated with test data ✅

#### **Day 5+: Advanced SQL Queries**
- [x] Write query: **YoY Sales Growth** (Year-over-Year comparison) — v_yoy_sales_growth ✅
- [x] Write query: **RFM Segmentation** (Recency, Frequency, Monetary scoring) — v_rfm_customer_segments ✅
- [x] Write query: **Inventory Turnover** by product category — v_inventory_turnover_analysis ✅
- [x] Write query: **Churn Detection** (inactive customers: >90 days no purchase) — v_churn_risk_detection ✅
- [x] Optimize queries: Add indexes, explain plans, benchmark runtime — indexes created in seed script ✅
- **Output**: `src/analytics/queries.sql` (6 views + bonus views) ✅

### Deliverables

| File | Purpose |
|------|---------|
| `SCHEMA/star_schema.sql` | DDL for FactSales + Dimensions |
| `SCHEMA/data_dictionary.md` | Column definitions + business logic |
| `SCHEMA/erd_diagram.png` | Visual schema design |
| `src/postgres/seed_synthetic_data.py` | Synthetic data generator |
| `src/analytics/views.sql` | Optimized KPI queries |
| `GOVERNANCE.md` | Data lineage & quality rules |

### Success Criteria
- ✅ PostgreSQL database structure ready with schema DDL
- ✅ Synthetic data generator created (50 stores, 500+ products, 10k customers, ~1M transactions)
- ✅ All 4+ SQL queries written as views and documented
- ✅ Schema documented with conceptual/logical/physical models in data_dictionary.md
- ✅ Git commits: 4 atomic commits
  1. feat: add synthetic data generator
  2. feat: add advanced SQL queries (YoY, RFM, inventory, churn)
  3. docs: add comprehensive data dictionary
  4. (optional) create ERD diagram

**WEEK 1 STATUS**: ✅ COMPLETE (Core deliverables done. Ready to test data generation next.)

---

## **Status Summary**

### Completed ✅
- [x] Week 1: Data Modeling & SQL Foundation (COMPLETE)

### In Progress 🔄
- [ ] Week 2: ETL Pipeline & Data Quality (STARTING SOON)

### Not Started ⏳
- [ ] Week 3: BigQuery Analytics Layer & Performance Optimization
- [ ] Week 4: BI Dashboards & KPI Design
- [ ] Week 5: ML Models & API Integration

---

## **WEEK 2: ETL Pipeline & Data Quality**

### Goal
Build an Extract-Load pipeline and set up dbt for transformations.

### Tasks

#### **Day 1–2: Extract & Load to Cloud Storage**
- [ ] Install Google Cloud SDK + authenticate
- [ ] Create `src/etl/postgres_to_gcs.py`
  - Query Postgres nightly (simulate batch job)
  - Export FactSales + Dimensions as Parquet files
  - Upload to Google Cloud Storage (GCS) bucket
- [ ] Test locally with mock GCS (or free BigQuery sandbox)
- **Output**: Daily Parquet exports in GCS

#### **Day 3–4: Load to BigQuery & Set Up dbt**
- [ ] Create BigQuery dataset (`retail_analytics_raw`)
- [ ] Load Parquet files into raw tables (`raw_sales`, `raw_products`, etc.)
- [ ] Initialize dbt project: `dbt init dbt_project`
- [ ] Create dbt staging models:
  - `stg_sales_clean` (deduplication, null handling, data type fixes)
  - `stg_products_clean` (standardize text, handle nulls)
  - `stg_stores_clean` (region/store level hierarchy)
- [ ] Run: `dbt run` → verify staging models created in BigQuery
- **Output**: BigQuery staging layer ready

#### **Day 5+: Data Quality Checks**
- [ ] Create `tests/data_quality_checks.py`
  - Check for duplicate transaction IDs
  - Verify no negative sales amounts
  - Validate all sales have valid store_id / product_id
  - Check for orphaned foreign keys
- [ ] Integrate dbt tests in `dbt_project/models/staging/`
- [ ] Run dbt tests: `dbt test` (all should pass)
- **Output**: Automated quality suite in place

### Deliverables

| File | Purpose |
|------|---------|
| `src/etl/postgres_to_gcs.py` | Daily batch extract script |
| `src/etl/dbt_project/` | dbt models (staging + tests) |
| `tests/data_quality_checks.py` | Custom quality checks |
| `src/etl/requirements.txt` | Python dependencies (dbt, pandas, etc.) |

### Success Criteria
- ✅ Data daily loaded from Postgres → GCS → BigQuery
- ✅ BigQuery staging tables have clean, deduplicated data
- ✅ dbt tests pass (0 failures)
- ✅ Git commits: 3–4 (postgres_to_gcs, dbt models, quality tests)

---

## **WEEK 3: BigQuery Analytics Layer & Performance Optimization**

### Goal
Build optimized analytics tables in BigQuery and demonstrate cost/performance improvements.

### Tasks

#### **Day 1–2: Create Analytics Mart**
- [ ] Create dbt mart models:
  - `fct_sales_v2` (fact table with all grain: sale_id)
  - `dim_product_final` (slowly changing dimension for prices)
  - `dim_store_final` (with region hierarchy)
  - `dim_date_final` (date table with fiscal periods)
- [ ] Run transformations: `dbt run`
- [ ] Verify mart tables in BigQuery
- **Output**: Production-ready analytics tables

#### **Day 3: Partitioning & Clustering Strategy**
- [ ] Partition `fct_sales_v2` by `sale_date` (daily)
- [ ] Cluster by `store_id`, `product_id`
- [ ] Create materialized views for hot queries:
  - `v_sales_by_region_daily` (YoY + current)
  - `v_churn_risk_customers` (inactive flags)
  - `v_rfm_segments` (customer scores)
- [ ] Document partitioning logic in `docs/PERFORMANCE_LOG.md`
- **Output**: Optimized warehouse schema

#### **Day 4–5: Performance Benchmarking**
- [ ] Run unoptimized query (full scan): benchmark runtime + bytes scanned
- [ ] Run optimized query (partition + cluster): benchmark again
- [ ] Calculate cost savings:
  ```
  Cost Reduction = (Bytes Unoptimized - Bytes Optimized) / Bytes Unoptimized * 100%
  ```
- [ ] Document results in `docs/PERFORMANCE_LOG.md`
  - Example: "Query time: 8.2s → 0.3s (96% savings)"
- [ ] Create summary README for optimization wins
- **Output**: Performance report with benchmarks

### Deliverables

| File | Purpose |
|------|---------|
| `src/etl/dbt_project/models/marts/` | Analytics mart models |
| `src/analytics/views.sql` | Materialized views |
| `docs/PERFORMANCE_LOG.md` | Benchmark results + cost analysis |
| `.github/workflows/dbt_run.yml` | CI/CD for dbt (optional) |

### Success Criteria
- ✅ Analytics mart tables created and tested
- ✅ Partitioning/clustering demonstrably improves performance (>50% faster)
- ✅ Query cost benchmarked and documented
- ✅ Git commits: 3–4 (mart models, clustering, performance docs)

---

## **WEEK 4: BI Dashboards & KPI Design**

### Goal
Build interactive dashboards in Looker Studio (or alternative) with clear KPI definitions.

### Tasks

#### **Day 1–2: KPI Definition & Metrics**
- [ ] Document KPI definitions in `src/analytics/kpi_definitions.md`:
  - **Total Revenue**: Sum of all sales
  - **YoY Growth**: % change from prior year
  - **Store Performance**: Revenue + margin by store
  - **Customer LTV**: Lifetime value based on transaction history
  - **Inventory Turnover**: COGS / Average Inventory
  - **Sell-Through Rate**: Units sold / Units received
- [ ] Create SQL views for each KPI:
  - `v_revenue_daily`, `v_yoy_growth`, `v_store_ranking`, `v_customer_ltv`, etc.
- **Output**: `src/analytics/kpi_definitions.md` + KPI views

#### **Day 3–4: Looker Studio Dashboard**
- [ ] Connect Looker Studio to BigQuery
- [ ] Create dashboard with 5–6 key reports:
  1. **Sales Dashboard**: Total revenue, trend, regional breakdown
  2. **Customer Dashboard**: Acquisition, retention, LTV distribution
  3. **Inventory Dashboard**: Stock levels, turnover by category, reorder alerts
  4. **Store Performance**: Top/bottom stores, margin analysis
  5. **KPI Scorecard**: Key metrics at a glance
- [ ] Add filters: Date range, Store, Product Category, Region
- [ ] Export dashboard link + screenshot
- **Output**: Live Looker Studio dashboard

#### **Day 5: Documentation & Design Narrative**
- [ ] Write dashboard README: explain each chart, business logic, how to use
- [ ] Add annotations to dashboard (hover tooltips with metric definitions)
- [ ] Screenshot dashboards for GitHub portfolio
- **Output**: Dashboard guide + visuals

### Deliverables

| File | Purpose |
|------|---------|
| `src/analytics/kpi_definitions.md` | KPI business logic + SQL |
| `dashboards/looker_studio_config.md` | Dashboard setup + link |
| `dashboards/queries.sql` | Pre-built dashboard queries |
| `docs/DASHBOARD_GUIDE.md` | How-to guide for dashboards |

### Success Criteria
- ✅ Dashboard with 5+ interactive reports
- ✅ All KPIs accurately calculated from analytics mart
- ✅ Filters work (date, store, category, etc.)
- ✅ Documentation explains business context of each KPI
- ✅ Git commits: 2–3 (KPI definitions, queries, documentation)

---

## **WEEK 5: ML Models & API Integration**

### Goal
Build churn prediction and demand forecasting models; wrap in FastAPI.

### Tasks

#### **Day 1–2: Churn Prediction Model**
- [ ] Feature engineering: Extract from BigQuery or Postgres
  - **Recency**: Days since last purchase
  - **Frequency**: Purchases in last 90 days
  - **Monetary**: Total spend in last 90 days
  - **RFM Score**: Combined 1–10 rating
  - **Loyalty Status**: Program member? Points earned?
  - **Purchase Trend**: Slope of monthly purchases
- [ ] Data prep: Split train/test (80/20), handle class imbalance
- [ ] Model training: Logistic Regression or Random Forest
  - Train on historical data (12 months)
  - Evaluate: Precision, Recall, F1-Score, AUC-ROC
- [ ] Save model: `src/ml/churn_model.pkl`
- **Output**: Trained churn model + performance metrics

#### **Day 3–4: Demand Forecasting + FastAPI**
- [ ] Feature engineering: Product + Store + Time features
- [ ] Time-series model (ARIMA, Prophet, or XGBoost)
  - Forecast next month's sales by product/store
  - Evaluate: RMSE, MAE on test set
- [ ] Create FastAPI app: `src/ml/api.py`
  ```python
  @app.get("/churn-risk")
  def predict_churn(customer_id: int):
      # Call churn model
      return {"customer_id": customer_id, "churn_probability": 0.72}

  @app.get("/forecast")
  def forecast_demand(product_id: int, store_id: int, months_ahead: int = 1):
      # Call forecast model
      return {"forecast": [...]}
  ```
- [ ] Test endpoints locally
- **Output**: FastAPI server with /churn-risk + /forecast endpoints

#### **Day 5: Polish, Test & Document**
- [ ] Write tests: `tests/test_ml_models.py`
  - Test churn model predictions (sanity checks)
  - Test forecast model output ranges
  - Test API endpoints
- [ ] Create `src/ml/requirements.txt` (scikit-learn, xgboost, fastapi, etc.)
- [ ] Document model cards:
  - Training data, features, performance metrics
  - How to retrain, deploy, monitor
- [ ] Create `docs/ML_MODELS.md` (model overview)
- **Output**: Tested, documented ML pipeline

### Deliverables

| File | Purpose |
|------|---------|
| `src/ml/churn_model.pkl` | Trained churn prediction model |
| `src/ml/demand_forecast.pkl` | Trained demand forecast model |
| `src/ml/api.py` | FastAPI server |
| `src/ml/requirements.txt` | ML dependencies |
| `tests/test_ml_models.py` | Model tests |
| `docs/ML_MODELS.md` | Model documentation |

### Success Criteria
- ✅ Churn model trained with >70% F1-Score
- ✅ Demand forecast RMSE <15% of mean sales
- ✅ FastAPI endpoints respond correctly (test with Postman/curl)
- ✅ All tests pass: `pytest tests/test_ml_models.py`
- ✅ Git commits: 3–4 (churn model, forecast model, API, tests)

---

## 🎯 Final Deliverable: Portfolio Package

### GitHub Repo Structure (Complete)
```
lcv-retail-analytics-platform/
├── README.md (comprehensive project overview)
├── ROADMAP.md (this file)
├── GOVERNANCE.md (data dictionary + lineage)
├── SCHEMA/ (data modeling with ERD)
├── src/ (all source code: Postgres, ETL, Analytics, ML)
├── dashboards/ (BI assets + screenshots)
├── tests/ (quality checks + model tests)
├── docs/ (performance logs, ML models, architecture)
└── .gitignore
```

### Documentation Checklist
- [x] README: Project overview, architecture, setup instructions
- [x] ROADMAP: 5-week plan with deliverables ✅ This file
- [ ] GOVERNANCE: Data dictionary, lineage, SCD strategy
- [ ] Data Modeling: ERD, conceptual/logical/physical models
- [ ] SQL Optimization: Query benchmarks, partitioning logic, cost analysis
- [ ] dbt Models: Staging → marts with test coverage
- [ ] Dashboard Guide: KPI definitions, how to use
- [ ] ML Model Cards: Features, performance, retraining guide
- [ ] Architecture Diagram: Data flow from source → insights

### Portfolio Narrative (for interviews)
When presenting this project to LCW:

1. **"I designed an end-to-end analytics platform simulating your 1,300-store operation"**
   - Star schema, dimensional modeling, SCD Type 2

2. **"I optimized queries for cost and performance"**
   - Show partitioning/clustering benchmark: "96% cost reduction"

3. **"I built governance from the ground up"**
   - Data dictionary, lineage tracking, quality checks

4. **"I connected insights to action via dashboards and APIs"**
   - Looker Studio dashboards + churn/demand prediction endpoints

5. **"I practiced the full data lifecycle your teams execute daily"**
   - ETL, transformations (dbt), analytics, ML

---

## 📊 Weekly Effort Breakdown

| Week | Hours/Day | Total Hours | Focus |
|------|-----------|------------|-------|
| 1 | 3 | 15 | Modeling + SQL |
| 2 | 3 | 15 | ETL + Quality |
| 3 | 3 | 15 | Warehouse + Performance |
| 4 | 3 | 15 | BI + KPIs |
| 5 | 3 | 15 | ML + API |
| **Total** | **3** | **~75** | **End-to-end platform** |

---

## 🔄 Git Commit Strategy

Make atomic, well-documented commits:

```bash
# Week 1
git commit -m "feat: star schema design + synthetic data generator"
git commit -m "feat: advanced SQL queries with optimization"
git commit -m "docs: data dictionary and governance rules"

# Week 2
git commit -m "feat: postgres to GCS ETL pipeline"
git commit -m "feat: dbt staging models + quality tests"

# Week 3
git commit -m "feat: BigQuery analytics mart + partitioning strategy"
git commit -m "perf: query optimization benchmarks (96% cost reduction)"

# Week 4
git commit -m "feat: KPI definitions and Looker Studio dashboard"

# Week 5
git commit -m "feat: churn prediction model and demand forecast API"
git commit -m "test: ML model tests + API endpoints"
```

---

## ❓ Common Questions

**Q: What if I get stuck?**
A: Each week is designed to be self-contained. If you hit a blocker, jump to the next task—don't let one thing halt progress.

**Q: Do I need to use all GCP services?**
A: No. You can use free tiers of BigQuery, Cloud Storage, and even mock them locally. The concepts matter more than the exact tools.

**Q: How do I handle data privacy?**
A: This is synthetic data only. No real LCV customer data. Perfect for a public portfolio on GitHub.

**Q: Can I modify this roadmap?**
A: Absolutely. Adjust tasks to your pace. The goal is a complete end-to-end project, not following a script.

---

## 🚀 Ready to Start?

You are here: **Today (Feb 19)** — Roadmap reset & ready to execute.
Start: **Now** — Week 1, Day 1 (generate synthetic data + SQL queries).

The first thing to do is set up PostgreSQL locally and run the `seed_synthetic_data.py` script.
By end of Week 1, you'll have a queryable retail database with 1M+ transactions.

**Let's go. ¡Vamos! 🔥**

---

**Last Updated**: February 19, 2026
**Status**: Starting Week 1 Implementation ⏳
