# ETL Module

This module handles the Extract–Load pipeline that moves data from PostgreSQL → GCS → BigQuery, plus dbt transformation models.

---

## 📦 Contents

- `run_pipeline.py` – Main orchestration script for the EL pipeline
- `dbt_project.yml` – dbt project configuration and models
- Core EL logic and BigQuery integration

---

## 🚀 Quick Start

### Prerequisites

- PostgreSQL source database (see [postgres/](../postgres/README.md))
- Google Cloud Project with:
  - BigQuery dataset created
  - Service account with BigQuery permissions
  - GCS bucket for staging (optional)
- Python dependencies: `psycopg2`, `google-cloud-bigquery`, `dbt-bigquery`, `python-dotenv`

### Configuration

Create or update `.env` in project root:

```env
# PostgreSQL (Source)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=lcv_retail_db

# Google Cloud (Destination)
GOOGLE_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
GCP_BIGQUERY_DATASET=retail_analytics
```

### Run ETL Pipeline

```bash
python src/etl/run_pipeline.py
```

This will:
1. Extract data from PostgreSQL
2. Load to BigQuery (creating tables if needed)
3. Run dbt models for transformation
4. Generate data quality checks
5. Log execution metrics

---

## 🔄 Pipeline Stages

### Stage 1: Extract (PostgreSQL)

Reads data from PostgreSQL source:
- `dim_date`, `dim_store`, `dim_product`, `dim_customer`
- `fact_sales`

### Stage 2: Load (BigQuery)

Writes to BigQuery staging datasets:
- Raw layer (`raw_*` tables)
- Maintains consistency with source schema

### Stage 3: Transform (dbt)

Applies transformation models:
- Data cleaning and validation
- Slowly Changing Dimension (SCD) handling for customers/products
- Fact table aggregations

### Stage 4: Publish (Analytics)

Final analytics-ready tables for dashboards and ML models

---

## 📊 Data Lineage

```
PostgreSQL (OLTP)
      ↓
   Extract
      ↓
BigQuery Raw Layer
      ↓
   dbt Models
      ↓
BigQuery Analytics Layer
      ↓
Dashboards / ML / Reporting
```

---

## ⚙️ Configuration

### dbt Profiles

dbt configuration is stored in `~/.dbt/profiles.yml` (or set `DBT_PROFILES_DIR`):

```yaml
lcv_retail_analytics:
  outputs:
    dev:
      type: bigquery
      project: your-gcp-project-id
      dataset: retail_analytics_dev
      method: service-account
      keyfile: path/to/service-account-key.json
    prod:
      type: bigquery
      project: your-gcp-project-id
      dataset: retail_analytics
      method: service-account
      keyfile: path/to/service-account-key.json
  target: dev
```

### Environment-Specific Runs

```bash
# Run dbt with dev profile
dbt run --profiles-dir ~/.dbt --target dev

# Run dbt with prod profile
dbt run --profiles-dir ~/.dbt --target prod
```

---

## 📝 dbt Commands

Common dbt operations:

```bash
# Install dependencies
dbt deps

# Run all models
dbt run

# Run specific model
dbt run --select model_name

# Generate docs
dbt docs generate

# Run tests
dbt test

# Dry run (validate without executing)
dbt run --dry-run
```

---

## 🔍 Monitoring

### Pipeline Logs

Execution logs from `run_pipeline.py`:
- Data extraction counts
- Load success/failure rates
- dbt model execution times
- Data quality test results

### BigQuery Monitoring

Check BigQuery job history in Google Cloud Console:
- Query execution times
- Data volume loaded
- Cost estimation

---

## 🐛 Troubleshooting

### Authentication Error

```
google.auth.exceptions.DefaultCredentialsError
```

- Verify `GOOGLE_APPLICATION_CREDENTIALS` points to valid service account JSON
- Check service account has BigQuery permissions
- Run: `gcloud auth application-default login`

### BigQuery Dataset Not Found

```
NotFound: 404 Dataset your_project:retail_analytics not found
```

- Create dataset in BigQuery console or via:
  ```bash
  bq mk --dataset your_project:retail_analytics
  ```

### dbt Model Failures

- Run `dbt debug` to check database connections
- Check model SQL syntax: `dbt parse`
- View logs in `logs/dbt.log`

---

## 📁 Project Structure

```
etl/
├── run_pipeline.py          # Main orchestration
├── dbt_project.yml          # dbt config
├── models/
│   ├── staging/             # Raw → Cleaned
│   ├── intermediate/        # Cleaned → Business logic
│   └── marts/               # Final analytics tables
├── tests/                   # Data quality tests
├── macros/                  # Reusable SQL functions
└── seeds/                   # Static reference data (CSVs)
```

---

## 📋 Notes

- **Idempotent**: Pipeline safely handles re-runs (upsert patterns)
- **Schedulable**: Can be orchestrated via Airflow, Cloud Composer, or cron
- **Observable**: dbt generates docs and lineage graphs
- **Testable**: dbt tests ensure data quality gates
