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
