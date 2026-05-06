# LCV Retail Analytics Platform

End-to-end data engineering and ML platform simulating LC Waikiki's retail data infrastructure. PostgreSQL OLTP source → GCS Parquet staging → BigQuery warehouse → dbt transformations → churn prediction API and Looker Studio dashboards.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   PostgreSQL (Source)                        │
│  fact_sales  |  dim_product  |  dim_store  |  dim_customer   │
│  dim_date                                                    │
└────────────────────┬─────────────────────────────────────────┘
                     │  postgres_to_gcs.py  (40s, 27 MB)
                     ▼
┌──────────────────────────────────────────────────────────────┐
│            Google Cloud Storage (Parquet, date-partitioned)  │
│            gs://bucket/YYYY-MM-DD/*.parquet                  │
└────────────────────┬─────────────────────────────────────────┘
                     │  gcs_to_bigquery.py  (24s)
                     ▼
┌──────────────────────────────────────────────────────────────┐
│                 BigQuery — retail_analytics_raw              │
│  fact_sales (partitioned DAY/sale_date) + 4 dim tables       │
└────────────────────┬─────────────────────────────────────────┘
                     │  dbt run  (11 models, 9 tests)
                     ▼
┌────────────────────────────────────────────────────────────────────────────────┐
│  Staging (views)                  │  Marts (tables, partitioned + clustered)  │
│  stg_sales_clean                  │  fct_daily_sales_trends                   │
│  stg_customer_clean               │  fct_store_performance                    │
│  stg_product_clean                │  fct_product_performance                  │
│  stg_store_clean                  │  fct_regional_sales                       │
│  stg_date_clean                   │  fct_customer_lifetime_value              │
│                                   │  fct_customer_churn_features              │
└────────────────────┬──────────────────────────────────────────────────────────┘
                     │
          ┌──────────┼──────────────┐
          ▼          ▼              ▼
   Looker Studio  FastAPI ML API  SQL analytics
   5 dashboards   /predict/churn  src/analytics/
```

---

## What Was Built

### Synthetic Dataset

- **1,000,000** sales transactions across **24 months** (2023-11-01 to 2025-10-31)
- **50** stores, **500** products (textiles, accessories, footwear), **10,000** customers
- **25.48% churn rate** — cadence-relative definition: silent for `> MAX(90d, 1.5 × avg inter-purchase gap)`
- Seeded with realistic behavioral cohorts: churned customers have 10% return rate vs 4% active; loyalty member distribution maintained per cohort

### ETL Pipeline

| Stage | Script | Time | Volume |
|---|---|---|---|
| PostgreSQL → GCS | `postgres_to_gcs.py` | ~40s | 27 MB Parquet |
| GCS → BigQuery | `gcs_to_bigquery.py` | ~24s | 1M rows |

- Extracts all 5 tables (1 fact, 4 dims) as Parquet to `gs://bucket/YYYY-MM-DD/`
- Loads to BigQuery raw layer; `fact_sales` loaded with `TimePartitioning(DAY, sale_date)`
- `--local` flag for development without GCS

### BigQuery Partitioning

Benchmarked April 27, 2026 on the 730-day dataset:

| | Bytes scanned |
|---|---|
| Unpartitioned + date filter | 15.26 MB |
| Partitioned + date filter (`>= 2025-10-01`) | 529 KB |
| **Reduction** | **96.6%** |

Partitioning set at load time in `gcs_to_bigquery.py` — applied to `fact_sales` only. Staging views inherit pruning automatically from the partitioned source.

### dbt Transformations

11 models, 9/9 tests passing.

**Staging** (5 views — `retail_analytics_staging`):

| Model | What it does |
|---|---|
| `stg_sales_clean` | Deduplication, null filtering, return flag, net_amount calculation |
| `stg_customer_clean` | Customer master with loyalty status |
| `stg_product_clean` | Product master with category and list price |
| `stg_store_clean` | Store master with regional hierarchy |
| `stg_date_clean` | Date dimension with calendar attributes |

**Marts** (6 tables — `retail_analytics_marts`, partitioned + clustered):

| Model | Grain | Key metrics |
|---|---|---|
| `fct_daily_sales_trends` | 1 row/day | Daily revenue, 7/30-day moving averages, DoW ranking |
| `fct_store_performance` | 1 row/store | Revenue, profit, transaction count, rank within region |
| `fct_product_performance` | 1 row/product | Revenue, units sold, profit by category |
| `fct_regional_sales` | store × category × month | Regional revenue, margin, performance quartiles |
| `fct_customer_lifetime_value` | 1 row/customer | LTV, RFM segments, VIP/At Risk classification |
| `fct_customer_churn_features` | 1 row/customer as of 2025-10-31 | Behavioral features + `is_churned` label for ML |

### Churn Prediction ML

Trained on `fct_customer_churn_features` — 8,000 train / 2,000 test (stratified split).

**Feature leakage audit**: 6 features excluded (`days_since_last_purchase`, `purchases_l30/60/90d`, `spend_l90d`, `spend_trend_ratio`) — all directly encode the churn label by construction. A temporal split audit confirms they produce ~100% / ~0% churn in train/test cohorts.

**5 clean features used**: `spend_prev_90d`, `return_rate`, `avg_days_between_purchases`, `purchase_count`, `loyalty_member`

| Model | AUC-ROC | Accuracy |
|---|---|---|
| DummyClassifier (baseline) | 0.496 | — |
| Logistic Regression | 0.9995 | 99.25% |
| Random Forest | 0.9990 | — |
| **AUC lift over baseline** | **+0.504** | |

Artifacts saved to `src/ml/models/` (gitignored): `churn_model.pkl`, `churn_scaler.pkl`, `churn_metadata.json`, `confusion_matrix.png`.

### ML API

```
uvicorn src.ml.api:app --reload --host 0.0.0.0 --port 8000
```

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Liveness check + model load status |
| `/api/models` | GET | Model metadata, AUC, feature list, risk thresholds |
| `/api/predict/churn` | POST | Single customer churn score + risk tier |
| `/api/predict/churn/batch` | POST | Batch predictions |

Risk tiers: `low` (< 0.30) / `medium` (0.30–0.60) / `high` (≥ 0.60). Swagger UI at `/docs`.

### Looker Studio Dashboards

5 dashboards at [datastudio.google.com/s/j2Q-vBZT3Gc](https://datastudio.google.com/s/j2Q-vBZT3Gc):

- Sales Performance (revenue trends, YoY)
- Store Performance (regional rankings)
- Product Performance (category breakdown)
- Customer Lifetime Value (RFM segments)
- Daily Sales Trends (moving averages, DoW patterns)

---

## Project Structure

```
lcv-retail-analytics-platform/
├── pyproject.toml                      # uv-managed dependencies
├── uv.lock                             # Locked dependency graph
├── SCHEMA/
│   ├── star_schema.sql                 # PostgreSQL DDL
│   └── data_dictionary.md              # Column definitions and business rules
├── src/
│   ├── postgres/
│   │   └── seed_synthetic_data.py      # Generate 1M synthetic transactions
│   ├── etl/
│   │   ├── postgres_to_gcs.py          # Extract PostgreSQL → GCS Parquet
│   │   ├── gcs_to_bigquery.py          # Load GCS → BigQuery (partitioned)
│   │   ├── setup_bigquery.py           # Create datasets
│   │   └── dbt_project/
│   │       └── models/
│   │           ├── staging/            # 5 views (stg_*)
│   │           └── marts/              # 6 tables (fct_*)
│   ├── analytics/
│   │   └── queries.sql                 # YoY, RFM, churn risk SQL views
│   └── ml/
│       ├── train_churn.py              # Train LR + RF, leakage audit, save artifacts
│       ├── churn_model.py              # Inference class + Pydantic schemas
│       ├── api.py                      # FastAPI app
│       └── models/                     # Gitignored — regenerated by train_churn.py
└── docs/
    ├── GOVERNANCE.md                   # Data quality checks and lineage
    ├── BEST_PRACTICES.md               # SQL optimization patterns
    ├── PERFORMANCE_LOG.md              # BigQuery benchmark results
    └── CHANGELOG.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Source database | PostgreSQL 15 |
| Orchestration | Python (custom ETL scripts) |
| Storage | Google Cloud Storage (Parquet) |
| Warehouse | BigQuery (partitioned + clustered) |
| Transformations | dbt Core 1.11 + dbt-bigquery |
| ML | scikit-learn (LogisticRegression, RandomForestClassifier) |
| ML API | FastAPI + uvicorn, Pydantic v2 |
| Visualization | Looker Studio |
| Dependency management | uv + pyproject.toml |
| Code quality | black, ruff, mypy, pre-commit |

---

## Running the Pipeline

```bash
# Dependencies
uv sync --dev

# 1. Seed PostgreSQL
python src/postgres/seed_synthetic_data.py

# 2. Extract to GCS (--local for testing without GCS)
python src/etl/postgres_to_gcs.py --local

# 3. Load to BigQuery
python src/etl/gcs_to_bigquery.py

# 4. Run dbt
cd src/etl/dbt_project
dbt run
dbt test

# 5. Train churn model
python src/ml/train_churn.py

# 6. Start ML API
uvicorn src.ml.api:app --reload --host 0.0.0.0 --port 8000
```

Required environment variables: see `.env.template`.

---

## Known Limitations

**Synthetic data distributions**: All stores and product categories show similar revenue and ~45% margin. The seeder uses uniform distributions — no store-tier weighting, no seasonality curve. Real retail data shows 20–30% margin variance by store tier and significant seasonal spikes that uniform seeding doesn't replicate.

**AUC 0.9995 reflects synthetic separability**: The behavioral cohorts were explicitly constructed with distinct churn patterns (10% vs 4% return rate, spend windows set to create clean temporal boundaries). This makes the classes cleanly separable in feature space. Production churn models on real customer data typically achieve AUC 0.70–0.85. The leakage audit and DummyClassifier baseline (+0.504 lift) are included precisely to document that the signal is genuine but synthetic-data-inflated.

**`fct_store_performance` is lifetime-to-date only**: This mart aggregates all transactions with no date dimension — it can't be sliced by period. `fct_regional_sales` supports time-series analysis via `year_month`; `fct_store_performance` does not. Period-over-period store comparisons require either promoting this mart to the `fct_regional_sales` grain or adding a `sale_month` grouping key.

---

## Documentation

- [SCHEMA/data_dictionary.md](SCHEMA/data_dictionary.md) — column definitions, business rules, data lineage
- [docs/GOVERNANCE.md](docs/GOVERNANCE.md) — data quality checks, SLA expectations
- [docs/PERFORMANCE_LOG.md](docs/PERFORMANCE_LOG.md) — BigQuery partition benchmark results
- [docs/BEST_PRACTICES.md](docs/BEST_PRACTICES.md) — SQL optimization patterns

---

MIT License
