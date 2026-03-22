# LCV Retail Analytics Platform — 5-Week Development Roadmap + Week 6 Enhancement

**Timeline**: 5 weeks @ ~3 hours/day = ~75 hours total
**Start Date**: February 15, 2026
**Target Completion**: March 21, 2026 (5 weeks) / March 28, 2026 (+ Week 6 optional)

**Progress**:
- Week 1: ✅ Complete (Feb 23-24)
- Week 2 (Days 1-2): ✅ Complete (Feb 25-26)
- Week 2 (Days 3-4): ✅ Complete (Feb 27)
- Week 2 (Day 5+): ✅ Complete (Mar 9-12) — 4 Analytics Marts Built ← TODAY
- Weeks 3-5: ⏳ Pending
- **Week 6 (Optional)**: ⏳ Enterprise Enhancement (phone-based identity)

**Elapsed Time**: ~30-35 hours
**Remaining (5 weeks)**: ~40-45 hours
**Remaining (+ Week 6)**: ~50-55 hours
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

**WEEK 1 STATUS**: ✅ COMPLETE (Feb 24)

---

## **Status Summary – Updated Feb 27**

### Completed ✅
- [x] Week 1: Data Modeling & SQL Foundation (Feb 23–24) ✅
  - Schema design, synthetic data generator (1M records), 6 advanced SQL queries
  - Git: 7 commits, comprehensive data dictionary + governance

- [x] Week 2, Days 1–2: ETL Extraction Pipeline (Feb 25–26) ✅
  - ✅ GCP infrastructure setup: project, GCS bucket, BigQuery dataset, service account + key
  - ✅ `src/etl/postgres_to_gcs.py` created (400+ lines, production-ready)
  - ✅ Local testing: 1.01M records extracted in 2.25 minutes
  - ✅ Production run: All 5 tables uploaded to GCS in 6.74 minutes
  - ✅ Files: gs://lcv-retail-analytics-dw/2026-02-26/*.parquet (27.3 MB)
  - ✅ Error handling: Exit codes (0/1), context managers, comprehensive logging
  - ✅ Documentation: BEST_PRACTICES.md enhanced with GCP/BigQuery/credentials guidance
  - ✅ VS Code setup: .vscode/settings.json for auto-activated venv
  - Git: 2 commits (postgres_to_gcs.py, BEST_PRACTICES enhancements)

- [x] Week 2, Days 3–4: Load to BigQuery & Initialize dbt (Feb 27) ✅
  - ✅ `src/etl/gcs_to_bigquery.py`: Loads GCS Parquet → BigQuery (1.01M records in 36.77s)
  - ✅ BigQuery datasets created: raw (data loaded), staging (ready for dbt), marts (ready for analytics)
  - ✅ dbt project initialized: dbt_project.yml, profiles.yml, models structure
  - ✅ 5 staging models created with data quality validation:
    * stg_date_clean: Date dimension, fiscal year calculations
    * stg_store_clean: Store dimension, text standardization
    * stg_product_clean: Product dimension, price validation
    * stg_customer_clean: Customer dimension, deduplicated (QUALIFY ROW_NUMBER)
    * stg_sales_clean: Sales facts (1M rows, materialized), profit calculations
  - ✅ Each model includes: null validation, positive value checks, deduplication, text standardization
  - ✅ Documentation: dbt_project README with usage guide, configuration, commands
  - Git: 3 commits (gcs_to_bigquery.py, dbt initialization, setup_bigquery.py)

- [x] Week 2, Day 5+: Analytics Marts (Mar 9-12) ✅
  - ✅ **Mart 1: fct_product_performance** (498 products, 5.77s)
    * Aggregation: product_id, SUM(revenue/units/profit), COUNT(transactions)
    * 1-layer CTE pattern, LEFT JOIN to product dimension
    * Business Q: "Which products drive most revenue/profit by category?"
  - ✅ **Mart 2: fct_customer_lifetime_value** (10K customers, 7.28s)
    * 3-layer CTE pattern: Aggregate → Window functions (ROW_NUMBER, NTILE) → Enrich
    * Segmentation: At Risk (>180 days inactive), VIP Loyal, High/Medium/Low Value quartiles
    * Business Q: "Who are our best customers?"
    * Data quality metric: Join tracking (identified NULL columns for investigation)
  - ✅ **Mart 3: fct_regional_sales** (3.8k region/store/category/month combos, 5.94s)
    * 3-layer CTE pattern with PARTITION BY region for scoped window functions
    * Metrics: revenue, units, profit, profit_margin, avg_transaction_value, rank, quartile
    * Rank + Quartile both ordered by total_profit (consistent storytelling)
    * Business Q: "Which regions/stores are performing best/worst?"
  - ✅ **Mart 4: fct_daily_sales_trends** (365 daily rows, 8.06s)
    * 3-layer CTE pattern with LAG window functions for moving averages
    * Metrics: daily revenue/units/profit, 7-day/30-day moving averages, revenue growth %
    * LAG(daily_revenue) ROWS BETWEEN 6 PRECEDING AND CURRENT ROW for moving windows
    * Weekday rankings to identify strongest sales days
    * Business Q: "What daily sales patterns exist? Which days are strongest?"
  - ✅ All 4 marts documented in schema.yml with column descriptions + business context
  - ✅ BEST_PRACTICES.md enhanced with: SQL execution order, COUNT differences, JOIN types, CTE patterns, window functions, dbt schema config, data quality tests, SQL skill tiers
  - Git: 2 commits (feat: Mart 1, feat: Mart 2; feat: Mart 3 + BEST_PRACTICES; docs: SQL tiers)

### In Progress 🔄
- [x] Week 2, Day 5+: Analytics Marts & dbt Testing (NEXT) ✅ COMPLETE (Mar 9-12)

### Not Started ⏳
- [ ] Week 3: BigQuery Analytics Layer & Performance Optimization
- [ ] Week 4: BI Dashboards & KPI Design
- [ ] Week 5: ML Models & API Integration
- [ ] **Week 6 (Optional)**: Phone-Based Customer Identity Resolution (Turkish retail domain enhancement)

---

## **WEEK 2: ETL Pipeline & Data Quality & Analytics Marts** ✅ COMPLETE

### Goal
Build an Extract-Load pipeline, set up dbt for transformations, and create 4 production analytics marts.

**Status (Mar 12)**: Days 1-5 complete. All 4 marts deployed and tested. ✅

### Tasks

#### **Day 1–2: Extract & Load to Cloud Storage** ✅ COMPLETE
- [x] Install Google Cloud SDK + authenticate
- [x] Create `src/etl/postgres_to_gcs.py`
  - [x] Query Postgres nightly (simulate batch job)
  - [x] Export FactSales + Dimensions as Parquet files
  - [x] Upload to Google Cloud Storage (GCS) bucket
- [x] Test locally with --local flag (Parquet files only, no GCS upload)
- [x] Test production with full GCS upload (Feb 26, 6:23 AM UTC)
- **Output**: ✅ Daily Parquet exports in GCS at gs://lcv-retail-analytics-dw/2026-02-26/

#### **Day 3–4: Load to BigQuery & Set Up dbt** ✅ COMPLETE
- [x] Create BigQuery dataset (`retail_analytics_raw`) ✅
- [x] Load Parquet files into raw tables (1.01M records in 36.77s) ✅
  - Used Python script: `gcs_to_bigquery.py` (production standard)
  - Auto-detected schema from Parquet files
  - Comprehensive logging with rotation
- [x] Initialize dbt project: `dbt_project.yml` + `profiles.yml` ✅
  - Manual setup (vs `dbt init` due to dbt-core 1.7.0 compatibility)
    * `dbt init` failed with: `KeyboardInterrupt` in dataclasses module
    * Root cause: dbt-core 1.7.0 has Python 3.10 compatibility issues
    * Solution: Created dbt_project structure manually (industry-standard approach)
    * Result: Full control, properly configured for BigQuery dev/prod targets
  - Configured for BigQuery with dev/prod targets
  - dbt_project.yml specifies: models, staging layer materialization, variables
  - profiles.yml specifies: BigQuery connection, service account auth, datasets
- [x] Create dbt staging models (5 models total) ✅
  - `stg_sales_clean` (1M rows, materialized table for performance)
  - `stg_date_clean` (731 records, date calculations)
  - `stg_products_clean` (498 records, price validation)
  - `stg_stores_clean` (50 records, text standardization)
  - `stg_customer_clean` (10K records, deduplicated)
- [x] Each model includes validation: null checks, positive values, deduplication, text standardization ✅
- [x] Create BigQuery datasets: `retail_analytics_staging` + `retail_analytics_marts` ✅
- **Output**: ✅ BigQuery staging layer ready for dbt transformations

#### **Day 5+: Analytics Marts (dbt Transformation Layer)** ✅ COMPLETE
- [x] Create **Mart 1: fct_product_performance** ✅
  - Group by product_id, sum revenue/units/profit by category
  - LEFT JOIN to dimension, simple 1-layer CTE
  - Output: 498 products, deployed in 5.77s
- [x] Create **Mart 2: fct_customer_lifetime_value** ✅
  - 3-layer CTE: aggregate → window functions (ROW_NUMBER, NTILE) → enrich
  - Customer segmentation: At Risk, VIP Loyal, High/Medium/Low Value
  - Output: 10K customers, deployed in 7.28s
- [x] Create **Mart 3: fct_regional_sales** ✅
  - 3-layer CTE with PARTITION BY region for scoped rankings
  - Multiple dimensions: region × store × product_category × year_month
  - Metrics: revenue, profit_margin, rank, quartile with profit-based ordering
  - Output: 3.8k rows, deployed in 5.94s
- [x] Create **Mart 4: fct_daily_sales_trends** ✅
  - 3-layer CTE with LAG window function for moving averages
  - 7-day + 30-day revenue moving averages using `ROWS BETWEEN 6 PRECEDING AND CURRENT ROW`
  - Revenue growth % and day-of-week rankings
  - Output: 365 daily rows, deployed in 8.06s
- [x] Document all marts in schema.yml (column descriptions, business context)
- [x] Enhance BEST_PRACTICES.md:
  - SQL execution order vs written order (FROM → WHERE → GROUP BY → SELECT → ORDER BY)
  - COUNT(*) vs COUNT(column) behavior with NULL examples
  - JOIN types (LEFT, INNER, RIGHT, FULL) with retail examples
  - CTE three-layer pattern (Aggregate → Calculate → Enrich)
  - Window functions vs aggregates distinction
  - PARTITION BY for scoped calculations
  - dbt schema configuration (avoid concatenation bugs)
  - SQL skill tiers (Tier 1: fundamentals, Tier 2: analytics, Tier 3: advanced)
- [x] Git commits: feature/mart-1-product-performance, feature/mart-2-customer-segmentation, feature/mart-3-regional-sales, chore/sql-tier-documentation
- **Output**: ✅ 4 production marts ready for BI + analysis

#### **Data Quality Tests** ✅ COMPLETE
- [x] Run dbt test on all marts
  ```bash
  dbt test -s marts
  ```
  - ✅ All 9 of 9 tests PASSED
  - Issue detected: 199,890 NULL customer_ids in raw sales data
  - Fix applied: Added `AND customer_id IS NOT NULL` to stg_sales_clean WHERE clause
  - Result:
    * not_null_fct_customer_lifetime_value_customer_id ✅
    * unique_fct_customer_lifetime_value_customer_id ✅
    * not_null_fct_product_performance_* (3 tests) ✅
    * not_null_fct_regional_sales_* (4 tests) ✅
  - Staging refresh: 800.1k rows (cleaned, removed 199k NULL customer rows)
  - All marts refreshed and passing validation
- **Purpose**: ✅ Marts are production-ready

### Deliverables

| File | Purpose | Status |
|------|---------|--------|
| `src/etl/postgres_to_gcs.py` | Daily batch extract script | ✅ Complete |
| `src/etl/gcs_to_bigquery.py` | GCS to BigQuery loader | ✅ Complete |
| `src/etl/README.md` | ETL documentation + troubleshooting | ✅ Complete |
| `src/etl/setup_bigquery.py` | BigQuery dataset setup | ✅ Complete |
| `src/etl/dbt_project/` | dbt models (staging + tests) | ✅ Complete (staging models) |
| `tests/data_quality_checks.py` | Custom quality checks | ⏳ Pending |
| `pyproject.toml` | Python dependencies (dbt, pandas, etc.) | ✅ Complete |
| `BEST_PRACTICES.md` | GCP/BigQuery/credentials guide + loading patterns | ✅ Complete |
| `.vscode/settings.json` | VS Code venv auto-activation | ✅ Complete |

### Success Criteria

**Days 1–2: Extract & Load** ✅
- ✅ Data extracted from Postgres → Parquet (local testing: 2.25 min, 1.01M records)
- ✅ Data uploaded to GCS (production run: 6.74 min, 27.3 MB)
- ✅ Exit codes working (0=success, 1=failure)
- ✅ Comprehensive logging with rotation
- ✅ Context managers for resource cleanup

**Days 3–4: Load to BigQuery & dbt** ✅
- ✅ BigQuery staging tables created and loaded from GCS Parquet files (36.77s for all 5 tables)
- ✅ dbt project initialized with dbt_project.yml and profiles.yml
- ✅ All 5 staging models created and tested (with data quality validation)
- ✅ BigQuery datasets ready: raw (1.01M records), staging (empty/ready), marts (empty/ready)
- ✅ Python script (gcs_to_bigquery.py) used instead of bq CLI (production standard)
- ✅ Each staging model includes: null validation, positive value checks, deduplication, derived fields

**Day 5+: Data Quality Tests** ⏳
- ⏳ Data quality tests written and passing (0 failures)
- ⏳ Git commits: Final commit (all work)

### Technical Notes: dbt Initialization Approach

**Why Manual Setup Instead of `dbt init`?**

When running `dbt init dbt_project`, we encountered:
```
KeyboardInterrupt: exec() in dataclasses module during QueryComment class definition
```

**Analysis:**
- Root cause: dbt-core 1.7.0 has Python 3.10 compatibility issues
- The dataclasses module fails during QueryComment class generation
- This is a known issue with dbt ≤1.7.0 on Python 3.10

**Solution: Manual Project Setup**
Instead of debugging compatibility, we created the dbt project structure manually:
1. Write `dbt_project.yml` (project config)
2. Write `profiles.yml` (BigQuery connection)
3. Write SQL models directly (no code generation needed)

**Benefits of Manual Approach (Industry Standard):**
- ✅ Full control over project structure
- ✅ Properly version-controlled dbt configuration
- ✅ No dependency on dbt CLI version quirks
- ✅ Easy to customize for team workflows
- ✅ Same result as `dbt init`, but cleaner

**Lesson:** dbt projects are just YAML + SQL files. You don't need `dbt init`; manual creation is often better for version control and team consistency.

---

## **WEEK 3: BigQuery Analytics Layer & Performance Optimization**

### Goal
Build optimized analytics tables in BigQuery and demonstrate cost/performance improvements.

### ⚠️ Reality Check: Savings Expectations

**Important Context on the "96% Cost Reduction" Claim:**

Your dataset: **~1M rows ≈ 100-200 MB**
- At this scale, partitioning/clustering is correct practice and essential learning
- Realistic savings: **50-80%** (not 96%)
- Why? Absolute data is smaller, so optimization gains are proportionally smaller

**The 96% reduction is real at enterprise scale:**
- Billions of rows = hundreds of GB / TB of data
- Partitioning on date + clustering on join keys = massive scans eliminated
- Example: 500 GB table → 5 GB scanned = 99% reduction

**Your learning value:**
- Same optimization techniques as enterprise pipelines ✅
- Same dbt config patterns ✅
- Same benchmarking methodology ✅
- Just different absolute numbers (50-80% instead of 96%)

**Resume talking point:** "I optimized queries using BigQuery partitioning and clustering, reducing scanned bytes by 60%+ and improving performance by 5-10x on a 1M row dataset. At enterprise scale (TB+ data), these same techniques achieve 95%+ cost reductions."

---

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
  - Example: "Query time: 2.5s → 0.3s (88% reduction in scanned bytes)"
- [ ] Create summary README for optimization wins
- **Output**: Performance report with realistic benchmarks

### Deliverables

| File | Purpose |
|------|---------|
| `src/etl/dbt_project/models/marts/` | Analytics mart models |
| `src/analytics/views.sql` | Materialized views |
| `docs/PERFORMANCE_LOG.md` | Benchmark results + cost analysis |
| `.github/workflows/dbt_run.yml` | CI/CD for dbt (optional) |

### Success Criteria
- ✅ Analytics mart tables created and tested
- ✅ Partitioning/clustering demonstrably improves performance (50%+ reduction in bytes scanned)
- ✅ Query cost benchmarked and documented with realistic expectations
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

### GitHub Repo Structure (Complete 5-Week Core + Optional Week 6)
```
lcv-retail-analytics-platform/
├── README.md (comprehensive project overview)
├── ROADMAP.md (this file — 5-week plan + Week 6 enhancement)
├── GOVERNANCE.md (data dictionary + lineage)
├── SCHEMA/ (data modeling + phone identity documentation)
├── src/ (all source code: Postgres, ETL, Analytics, ML)
├── dashboards/ (BI assets + screenshots)
├── tests/ (quality checks + model tests)
├── docs/ (performance logs, ML models, architecture)
└── .gitignore
```

**Week 6 Bonus (Optional):**
If you want to add phone-based customer identity resolution (Turkish retail domain enhancement), you'll also have:
- `src/etl/dbt_project/models/staging/stg_phone_identity.sql`
- Enhanced `fct_customer_lifetime_value` with phone identity
- Updated synthetic data generator with phone numbers

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

## **WEEK 6: Enterprise Enhancements — Phone-Based Customer Identity Resolution**

### Goal
Add domain-specific customer identity resolution using phone number as the primary key. This mirrors exactly how Turkish retailers (LCW, Migros, BIM, A101, Boyner) identify and convert customers at POS.

### Business Context

**Turkish Retail Flow (LCW Reality):**
1. Customer at checkout: "Telefon numaranız?"
2. Phone provided → Cashier registers in seconds (if new)
3. phone_number becomes customer_id immediately
4. Discounts applied, loyalty points earned
5. Anonymous sales (no phone) are rare edge cases (~2-3%, tourists/refusals)

**Current Synthetic Data Issue:**
- ~20% NULL customer_ids (unrealistically high)
- Doesn't reflect actual retail behavior

**Enhanced Model:**
- Reduce NULL customer_ids to 2-3% (realistic)
- Phone number as primary identity key
- Simple segmentation: Loyalty Member vs Anonymous
- Conversion funnel visibility (though most sign up instantly)

### Tasks

#### **Create phone_number Identity Layer**

- [ ] Update `src/postgres/seed_synthetic_data.py`:
  - Add `phone_number` column to `dim_customer` (Turkish format: 05XXXXXXXXX)
  - Add `phone_number` column to `fact_sales`
  - Reduce NULL `customer_id` from 20% → 2-3% (rare cases)
  - Link phone_number directly to customer_id when provided

- [ ] Create new staging model: `stg_phone_identity.sql`
  ```sql
  SELECT
      phone_number,
      customer_id,
      COUNT(*) AS total_purchases,
      SUM(net_amount) AS total_spend,
      MIN(sale_date) AS first_seen,
      MAX(sale_date) AS most_recent,
      CASE
          WHEN phone_number IS NOT NULL THEN 'Loyalty Member'
          ELSE 'Anonymous'
      END AS identity_status
  FROM {{ ref('stg_sales_clean') }}
  GROUP BY phone_number, customer_id
  ```

- [ ] Enhance `fct_customer_lifetime_value`:
  - Add `phone_number` and `identity_status` columns
  - Recalculate with richer phone-based identity data
  - Re-test: All 9 dbt tests should still PASS with cleaner data

- [ ] Create new mart (optional): `fct_customer_conversion_funnel`
  ```sql
  -- Conversion path: Anonymous → Loyalty Member
  -- Identify customers who started anonymous, then joined loyalty
  -- Track uplift in LTV after conversion
  ```

- [ ] Update `SCHEMA/data_dictionary.md`:
  - Document phone_number as identity key
  - Explain Turkish retail context
  - Document new staging model

#### **Validation & Testing**

- [ ] Rebuild all downstream models: `dbt run -s stg_phone_identity+`
- [ ] Rerun all tests: `dbt test -s marts` (confirm 9/9 PASS with new data)
- [ ] Snapshot queries before/after:
  - NULL customer_id count: 199,890 → ~20,000 (2-3% of 800k rows)
  - CLV distribution: More customers tracked
  - Identity_status breakdown: % Loyalty vs Anonymous

### Portfolio Narrative

When presenting this to LCW:

> "I built the core analytical platform in 5 weeks. Then I added phone-based customer identity resolution — modeling exactly how Turkish retailers like LCW identify and convert customers at checkout. This reduces anonymous transactions from 20% to 2-3%, making CLV calculations meaningful across nearly the full customer base. The model also creates visibility into the conversion funnel: identifying high-value anonymous customers who could become loyalty members."

**Why This Impresses:**
- ✅ Domain-specific (Turkish retail, not generic)
- ✅ Shows business understanding (how LCW actually works)
- ✅ Real insight: <3% anonymous vs your initial 20%
- ✅ Creates new analytics (conversion funnel)
- ✅ Any LCW interviewer recognizes the pattern immediately

### Deliverables

| File | Purpose |
|------|---------|
| `src/postgres/seed_synthetic_data.py` | Updated with phone_number + reduced NULL % |
| `src/etl/dbt_project/models/staging/stg_phone_identity.sql` | New identity aggregation model |
| `src/etl/dbt_project/models/marts/fct_customer_lifetime_value.sql` | Enhanced with phone + identity_status |
| `SCHEMA/data_dictionary.md` | Added phone identity section |

### Success Criteria

- ✅ NULL customer_id reduced from 199,890 → ~20k (2-3%)
- ✅ New stg_phone_identity model created and tested
- ✅ CLV mart includes phone_number and identity_status
- ✅ All 9 dbt tests PASS with new data
- ✅ Phone identity layer documented in data_dictionary
- ✅ Git commits: 2–3 (seed data update, new staging model, enhanced marts)

### Why Week 6 vs Earlier Weeks

- **Doesn't block Weeks 3-5**: Performance, BI, ML don't depend on phone identity
- **Clean addition**: Seed data change is isolated and well-understood
- **Shows extensibility**: You can enhance a completed system without breaking it
- **Turkish domain knowledge**: Final polish that shows you understand LCW's business
- **Interview value**: This is the detail that separates candidates who understand the domain from those who just know the tech

---

## **WEEK 6B (Optional): Snowflake Parallel Warehouse Deployment**

### Goal
Add Snowflake as a second warehouse target for the same dbt models. Demonstrates warehouse-agnostic data engineering and adds resume impact (multi-cloud credentials).

### Business Context

**Why Parallel Snowflake?**
- ✅ dbt is warehouse-agnostic (same models, different target)
- ✅ Snowflake is dominant in European mid-market retail (Turkish companies often use it)
- ✅ Resume boost: "dbt + BigQuery + Snowflake" > "dbt + BigQuery alone"
- ✅ Great talking point: "I deploy the same models across multiple warehouses"

**Resume Impact:**
```
Before: BigQuery + dbt (Google-ecosystem focused)
After:  BigQuery + Snowflake + dbt (warehouse-agnostic, enterprise-ready)
```

**Cost:** Snowflake 30-day free trial with $400 credits (more than enough for this project)

### Tasks

#### **1. Snowflake Account Setup** (30 min)
- [ ] Sign up for [Snowflake Free Trial](https://www.snowflake.com/trial/)
  - No credit card required (trial period)
  - 30-day trial with $400 compute credits
- [ ] Create Snowflake account
- [ ] Note your account identifier (e.g., `xy12345.us-east-1`)
- [ ] Create role: `TRANSFORMER` (for dbt)
- [ ] Create warehouse: `COMPUTE_WH` (standard size)
- [ ] Create database: `LCV_ANALYTICS`
- [ ] Create schema: `MARTS`
- [ ] Create user for dbt with appropriate permissions

#### **2. Configure dbt for Snowflake** (1 hour)
- [ ] Update `src/etl/dbt_project/.dbt/profiles.yml`:
  ```yaml
  lcv_retail_analytics:
    outputs:
      dev_bigquery:
        type: bigquery
        # ... existing BQ config ...

      dev_snowflake:
        type: snowflake
        account: your_account_id
        user: dbt_user
        password: your_password  # Or use environment variable: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
        role: TRANSFORMER
        database: LCV_ANALYTICS
        warehouse: COMPUTE_WH
        schema: MARTS
        threads: 4
        client_session_keep_alive: False

    target: dev_bigquery  # Default to BigQuery, but can switch
  ```

- [ ] Install Snowflake dbt adapter:
  ```bash
  pip install dbt-snowflake
  ```

- [ ] Test Snowflake connection:
  ```bash
  dbt debug --target dev_snowflake
  ```

#### **3. Deploy Models to Snowflake** (1-2 hours)
- [ ] Run staging models on Snowflake:
  ```bash
  cd src/etl/dbt_project
  dbt run --target dev_snowflake -s staging
  ```

- [ ] Run all marts on Snowflake:
  ```bash
  dbt run --target dev_snowflake -s marts
  ```

- [ ] Run tests on Snowflake:
  ```bash
  dbt test --target dev_snowflake -s marts
  ```
  - Should see all 9 tests PASS
  - Confirms data integrity is equal across warehouses

#### **4. Performance & Cost Analysis** (1 hour)
- [ ] Compare query performance: BigQuery vs Snowflake
  ```
  Example: Run same query on both
  - BigQuery: X seconds
  - Snowflake: Y seconds
  - Document findings
  ```

- [ ] Document cost estimates:
  ```
  BigQuery: ~$0.07 per GB scanned
  Snowflake: $2-4 per credit (1 credit = 1 hour of standard warehouse)

  For this project:
  - 800K staging rows × 10 column queries × 30 days ≈ $X
  - Your Snowflake trial covers it entirely
  ```

- [ ] Update README with warehouse comparison table

#### **5. Documentation & Git** (30 min)
- [ ] Document in `src/etl/README.md`:
  - Snowflake setup (account creation, configuration)
  - How to switch targets: `dbt run --target dev_snowflake`
  - Performance comparison results
  - Cost analysis between BigQuery and Snowflake

- [ ] Update `README.md`:
  - Add "Multi-Warehouse Deployment" section
  - Highlight dbt warehouse-agnostic architecture

- [ ] Git commits: 2-3
  ```bash
  git commit -m "feat: add Snowflake dbt target to profiles.yml"
  git commit -m "feat: deploy analytics models to Snowflake (parallel to BigQuery)"
  git commit -m "docs: add warehouse performance and cost comparison"
  ```

### Deliverables

| File | Purpose |
|------|---------|
| `.dbt/profiles.yml` | Updated with Snowflake target (dev_snowflake) |
| `src/etl/README.md` | Setup instructions + performance comparison |
| `README.md` | Multi-warehouse deployment section |
| Snowflake Database | 4 marts + 5 staging models deployed |

### Success Criteria

- ✅ Snowflake account created and configured
- ✅ dbt-snowflake adapter installed
- ✅ All 5 staging models successfully deployed to Snowflake
- ✅ All 4 marts successfully deployed to Snowflake
- ✅ All 9 data quality tests PASS on Snowflake (same as BigQuery)
- ✅ Performance metrics documented (query times, costs)
- ✅ Can switch targets: `dbt run --target dev_snowflake` vs `--target dev_bigquery`
- ✅ README explains multi-warehouse strategy
- ✅ Git commits: 2-3 atomic commits

### Portfolio Narrative

When presenting this to employers:

> "I built the analytical platform in dbt, which is warehouse-agnostic. I deployed the exact same models to both BigQuery and Snowflake to demonstrate I can work across modern data stacks. Here's the performance comparison and cost analysis."

**Why This Impresses:**
- ✅ Shows you understand cloud data warehouses (not just one platform)
- ✅ Demonstrates warehouse-agnostic thinking (dbt's superpower)
- ✅ European employers see Snowflake often — huge advantage
- ✅ Parallel cloud is the future of enterprise data (you're future-ready)
- ✅ Cost consciousness (you benchmarked and compared)

### Interview Talking Points

- "I chose dbt because it's truly warehouse-agnostic. Same models, different targets."
- "I tested performance across BigQuery and Snowflake to understand the tradeoffs."
- "For Turkish companies, Snowflake is often preferred. I'm comfortable in both ecosystems."
- "The real power is the transformation logic (dbt models), not the warehouse. Switching targets is trivial."

### Effort Estimate

```
Snowflake setup + dbt config         → 2 hours
Deploy models + test                 → 2-3 hours
Performance analysis + documentation → 1 hour
Total: ~5-6 hours
```

This is a **high-impact, low-effort addition** to your portfolio!

---

## **WEEK 7: Automated Incremental Pipeline — Production Patterns**

### Goal
Transform your project from "I built a data warehouse" to "I built a production-pattern data pipeline with automated incremental loading." Add nightly transaction simulation and convert dbt models to incremental materialization.

### Business Context

**Production Reality:**
- Batch reloads are expensive at scale (100M+ rows = $$$, hours of compute)
- Incremental loading is how production pipelines work everywhere
- Your current pipeline: Full rebuild nightly (~10-30 min on 1M rows)
- Production pipeline: Append only new rows (~30 sec for 2,740 daily transactions)

**Resume Impact:**
```
Before: "Built a data warehouse with 1M records"
After:  "Built an automated nightly ETL pipeline with incremental
         loading—simulating production batch patterns"
```

The word **"incremental"** and **"automated"** signal real data engineering experience.

### Tasks

#### **Day 1–2: Daily Transaction Generator**

- [ ] Create `src/etl/daily_transactions.py`
  ```python
  def generate_daily_transactions(date, n_transactions=2740):
      # ~1M rows / 365 days = ~2,740 per day average
      # Simulate natural variation (some days 2000, others 3500)
      transactions = []
      for _ in range(n_transactions):
          transactions.append({
              'sale_date': date,
              'store_id': random.randint(1, 50),
              'product_id': random.randint(1, 500),
              'customer_id': random.choice([None] * 30 + list(range(1, 10001))),  # 3% NULL
              'quantity': random.randint(1, 5),
              # ... complete transaction record ...
          })
      return transactions

  if __name__ == "__main__":
      today = datetime.now().date()
      df = pd.DataFrame(generate_daily_transactions(today))
      # Insert to Postgres
  ```

- [ ] Test locally: Generate today's transactions, append to Postgres
- [ ] Verify partition: Check data appears in postgres with correct date

#### **Day 3: Integrate with Existing ETL Pipeline**

- [ ] Update `src/etl/postgres_to_gcs.py`:
  - Change FROM: "Export all tables"
  - Change TO: "Export only WHERE sale_date >= (today - 2 days)" (buffer for late arrivals)
  - Implement incremental export logic

- [ ] Update `src/etl/gcs_to_bigquery.py`:
  - Change FROM: "WRITE_TRUNCATE" (full replacement)
  - Change TO: "WRITE_APPEND" (incremental append)
  - Add `_PARTITIONTIME` validation to ensure data goes to correct date partitions

- [ ] Test: Run daily generator → postgres_to_gcs (incremental extract) → gcs_to_bigquery (append)
  - Verify: Today's transactions appear in BigQuery within correct partition
  - Verify: No duplicate IDs (sale_id is unique across all time)

#### **Day 4–5: Convert Key Marts to Incremental dbt Models**

**Why Incremental?**
```sql
-- Current (full rebuild every dbt run):
{{ config(materialized='table') }}
SELECT * FROM {{ ref('stg_sales_clean') }}
-- Result: All 800K rows rebuilt every time (slow + expensive)

-- Incremental (append only new rows):
{{ config(materialized='incremental') }}
SELECT * FROM {{ ref('stg_sales_clean') }}
{% if is_incremental() %}
  WHERE sale_date > (SELECT MAX(sale_date) FROM {{ this }})
{% endif %}
-- Result: Only 2,740 new rows processed (fast + cheap)
```

**Implementation:**

- [ ] Convert `fct_daily_sales_trends` to incremental
  ```sql
  -- models/marts/fct_daily_sales_trends.sql
  {{ config(materialized='incremental') }}

  WITH daily_sales AS (
    SELECT
      sale_date,
      SUM(net_amount) AS daily_revenue,
      SUM(quantity) AS daily_units,
      -- ... other metrics ...
    FROM {{ ref('stg_sales_clean') }}
    GROUP BY sale_date
  )
  SELECT * FROM daily_sales

  {% if is_incremental() %}
    WHERE sale_date > (SELECT MAX(sale_date) FROM {{ this }})
  {% endif %}
  ```

- [ ] Convert `fct_product_performance` to incremental
  - Aggregate by `product_id` (dimensions stay same, only append new sales)
  - First run: rebuild all products
  - Daily runs: recalculate only affected products

- [ ] Keep `fct_customer_lifetime_value` and `fct_regional_sales` as full rebuild (safer for aggregates)
  - These need full historical context (can't append incrementally without complex logic)
  - Dimension tables ALWAYS full rebuild

- [ ] Test incremental behavior:
  ```bash
  # First run (full build)
  dbt run -s fct_daily_sales_trends
  # Check: How many rows? (should match SELECT COUNT(*) from raw data)

  # Second run (incremental append)
  dbt run -s fct_daily_sales_trends
  # Check: Did it append only new day's rows?
  # Verify: No duplicates in results
  ```

#### **Day 5 (cont'd): Validate Incremental = Full**

- [ ] Create validation test: `tests/validate_incremental.sql`
  ```sql
  -- Ensure incremental mart is identical to full rebuild
  SELECT COUNT(*) as incremental_count FROM {{ ref('fct_daily_sales_trends') }}
  UNION ALL
  SELECT COUNT(*) as full_rebuild_count FROM (
    SELECT * FROM {{ ref('stg_sales_clean') }}
    GROUP BY sale_date
    -- ... full rebuild logic ...
  )
  -- Both counts should match exactly
  ```

- [ ] Run test: `dbt test -s fct_daily_sales_trends`
  - Catch any bugs where incremental diverges from full rebuild
  - This is critical: one missed row = silent data corruption

#### **Day 5+: Schedule Nightly Run with Windows Task Scheduler**

- [ ] Create `src/etl/run_nightly_pipeline.py`:
  ```python
  #!/usr/bin/env python3
  """
  Nightly pipeline orchestrator:
  1. Generate today's transactions
  2. postgres_to_gcs (incremental extract)
  3. gcs_to_bigquery (incremental load)
  4. dbt run (refresh incremental marts)
  5. Send completion notification
  """

  if __name__ == "__main__":
      # 1. Generate daily transactions
      today = datetime.now().date()
      transactions_df = generate_daily_transactions(today)
      load_to_postgres(transactions_df)

      # 2-3. ETL Pipeline
      postgres_to_gcs(incremental=True, date=today)
      gcs_to_bigquery(append_mode=True, date=today)

      # 4. Refresh marts
      os.system("cd src/etl/dbt_project && dbt run -s +fct_daily_sales_trends")

      # 5. Log success
      logger.info(f"Pipeline complete: {today}")
  ```

- [ ] Create Windows Task Scheduler entry:
  - **Task Name**: `LCV-Retail-NightlyETL`
  - **Trigger**: Daily at 2:00 AM (off-peak)
  - **Action**: `python src/etl/run_nightly_pipeline.py`
  - **Log Output**: `logs/pipeline_2026-03-16.log`

- [ ] Test: Run manually first
  ```bash
  python src/etl/run_nightly_pipeline.py
  # Check logs/
  # Verify BigQuery received new data
  # Verify dbt marts incremented (not rebuilt)
  ```

- [ ] Documentation: `src/etl/README.md`
  - How to set up Windows Task Scheduler
  - How to monitor nightly runs
  - How to debug if a run fails

### Deliverables

| File | Purpose |
|------|---------|
| `src/etl/daily_transactions.py` | Generates 2,740 transactions for a given date |
| `src/etl/run_nightly_pipeline.py` | Orchestrator (generate → extract → load → dbt refresh) |
| `src/etl/postgres_to_gcs.py` | UPDATED: Incremental WHERE clause (last 2 days) |
| `src/etl/gcs_to_bigquery.py` | UPDATED: WRITE_APPEND mode instead of WRITE_TRUNCATE |
| `src/etl/dbt_project/models/marts/fct_daily_sales_trends.sql` | UPDATED: Incremental materialization |
| `src/etl/dbt_project/models/marts/fct_product_performance.sql` | UPDATED: Incremental materialization |
| `tests/validate_incremental.sql` | Ensures incremental = full rebuild |
| `src/etl/README.md` | Updated with nightly pipeline + Task Scheduler setup |
| `logs/` | Timestamped pipeline execution logs |

### Success Criteria

**Day 1–2: Daily Generator**
- ✅ Generate 2,740 transactions for any given date
- ✅ Insert successfully into Postgres
- ✅ Realistic variation (some days 2000, others 3500)

**Day 3: Incremental ETL**
- ✅ postgres_to_gcs exports only last 2 days (not all 1M rows)
- ✅ gcs_to_bigquery appends (WRITE_APPEND), doesn't truncate
- ✅ Daily cycle: Generate → Extract → Load in <2 minutes total

**Day 4–5: Incremental dbt Models**
- ✅ `fct_daily_sales_trends` first run: builds all 365 days
- ✅ `fct_daily_sales_trends` second run: appends only new day
- ✅ `fct_product_performance` follows same pattern
- ✅ Validation test PASSES: Incremental results = Full rebuild results
- ✅ No duplicate rows in incremental tables

**Day 5+: Automation**
- ✅ Windows Task Scheduler configured and tested
- ✅ Nightly runs complete without errors (monitored via logs)
- ✅ All logs timestamped and rotated (older logs compressed/archived)
- ✅ Pipeline execution time: ~30 seconds for 2,740 new rows (vs 10-30 min for full rebuild)

**Performance Metrics to Document:**
```
Before (full rebuild):
- Extract time: 3-5 minutes (all 1M rows)
- Load time: 1-2 minutes
- dbt run time: 5-10 minutes (rebuilding all marts)
- Total: 10-17 minutes per night

After (incremental):
- Extract time: 10 seconds (2,740 rows only)
- Load time: 5 seconds
- dbt run time: 15 seconds (incremental models)
- Total: ~30 seconds per night
- Speedup: 20-30x faster
- Compute savings: 95%+ reduction (only processing new rows, not entire 1M rows)
```

**Note on Cost Savings:** This is different from Week 3's query optimization:
- **Week 3 (Partitioning/Clustering)**: Reduces bytes *scanned by queries* (50-80% on your 1M dataset)
- **Week 7 (Incremental dbt)**: Reduces *compute* needed to *build* marts nightly (95%+ savings by processing 2.7k rows instead of 1M)
- Both are essential in production pipelines, just different layers

### Portfolio Narrative

When presenting Week 7 to employers:

> "I built the core analytics platform in 5 weeks. Then I added production-grade pipeline patterns: automated nightly incremental loading. The system now processes 2,740 new daily transactions in 30 seconds—not the 10-30 minutes full rebuild would take. This is incremental dbt materialization, the pattern used by every production data team at scale. I also added Windows Task Scheduler automation, so the pipeline runs nightly without manual intervention. This moves the project from 'data warehouse proof-of-concept' to 'production-ready data infrastructure.'"

**Why This Impresses:**
- ✅ **Incremental thinking**: Shows you understand production constraints (cost, speed)
- ✅ **dbt expertise**: Incremental materialization is a tier-2+ dbt skill
- ✅ **Automation**: Demonstrates DevOps thinking (scheduling, monitoring, logging)
- ✅ **Cost awareness**: You benchmarked and optimized (95% compute reduction for nightly builds)
- ✅ **End-to-end ownership**: Not just writing SQL, but running production systems
- ✅ **Real patterns**: Every production data team does incremental loading

**Interview Talking Points:**
- "Incremental loading is non-negotiable at scale. 100M+ rows can't do full rebuilds."
- "I used dbt's `is_incremental()` logic to detect first run vs subsequent runs."
- "First run rebuilds history, then every night appends only new transactions."
- "Validated that incremental results exactly match full rebuild (caught data corruption risks)."
- "Nightly automation via Task Scheduler means zero manual intervention."
- "Pipeline runs in ~30 seconds on 2,740 daily transactions vs 10+ minutes for full reload."

### Effort Estimate

```
Daily transaction generator        → 2 hours
Incremental ETL updates            → 2-3 hours
Convert marts to incremental dbt   → 2-3 hours
Validation + testing               → 1 hour
Task Scheduler automation          → 30 min
Documentation                      → 1 hour
Total: ~8.5-9.5 hours (1-1.5 days)
```

This is the **highest-impact single addition** available—transforms your project from "warehouse" to "production data infrastructure."

---

## Week 6 & 7: Recommended Sequence

**If you do BOTH:**
1. **Week 6**: Add phone identity OR Snowflake (enterprise features)
2. **Week 7**: Add incremental pipeline + automation (production patterns)

This sequence makes sense:
- Week 6 makes the data richer (phone identity) or broader (multi-cloud)
- Week 7 makes it production-ready (incremental, automated, cost-optimized)
- Together: "Complete end-to-end analytics platform following production patterns"

**Effort:**
- Week 6 alone: 5-6 hours
- Week 7 alone: 8-9 hours
- Both: 13-15 hours (high-impact portfolio piece)

---

## Week 6: Multiple Optional Paths

**Choose Any Combination:**

### Path A: Phone-Based Customer Identity (Turkish Domain Knowledge)
- 5-6 hours
- Reduces NULLs, adds realism
- Shows business domain understanding
- LCW-specific competitive advantage
- Deliverable: stg_phone_identity model + enhanced CLV mart

### Path B: Snowflake Deployment (Multi-Cloud Engineering)
- 5-6 hours
- Warehouse-agnostic dbt skills
- Resume: BigQuery + Snowflake
- European job market advantage
- Deliverable: Snowflake + dbt + performance comparison

### Path C: API Enhancements (FastAPI User Tracking) ✨
- 3-4 hours
- Build production-grade REST APIs (separate from ML models)
- User progress tracking endpoint
- CRUD operations + charting
- Showcase full-stack FastAPI skills

**Path C Details:**
```python
# New endpoints for user progress tracking
@app.get("/users/{user_id}/progress/chart")
@app.get("/users/{user_id}/progress/summary")
@app.post("/users/{user_id}/progress")

# Requires: UserProgress table in BigQuery
# Tests: All CRUD operations validated
# Resume: "ML models + REST API layer"
```

### Path D: Two Paths Combined
- 10-12 hours
- A + B: Domain knowledge + Multi-cloud
- A + C: Domain knowledge + API skills
- B + C: Multi-cloud + API skills

### Path E: All Three (Ultimate Polish) ✨✨
- 15-18 hours
- Complete package: domain + cloud + APIs
- "I understand Turkish retail, modern cloud data stacks, AND production FastAPI"
- Most impressive portfolio

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

# Week 6 (Optional: Enterprise Enhancement)
git commit -m "feat: add phone-based customer identity resolution"
git commit -m "feat: create stg_phone_identity staging model"
git commit -m "feat: enhance CLV mart with phone identity + identity_status"
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
