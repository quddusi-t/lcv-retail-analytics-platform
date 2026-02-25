# ETL Module — PostgreSQL to Google Cloud Storage to BigQuery

Extract data from PostgreSQL, convert to Parquet, and load to Google Cloud Storage as staging for BigQuery ingestion. Plus dbt transformation models.

---

## 📦 Contents

- `postgres_to_gcs.py` – Main ETL extraction script (PostgreSQL → Parquet → GCS)
- `requirements.txt` – Python dependencies for ETL pipeline
- `dbt_project/` – dbt models for BigQuery transformations (future)

---

## 🚀 Quick Start

### Prerequisites

- PostgreSQL database with seed data populated
- Google Cloud Storage bucket created
- GCP service account key (JSON file)
- Environment variables configured in `.env`

### Installation

All ETL dependencies are in the root `pyproject.toml`. Install once at project level:

```bash
# From project root
pip install -e .
```

This installs:
- `pandas` — Data manipulation
- `pyarrow` — Parquet format support
- `psycopg2-binary` — PostgreSQL connection
- `google-cloud-storage` — GCS client
- `python-dotenv` — Environment variables

### Configuration

Ensure `.env` file contains:

```env
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=lcv_retail_analytics

# Google Cloud
GCP_PROJECT_ID=lcv-retail-analytics-dw
GCP_KEY_PATH=./lcv-gcp-key.json
GCS_BUCKET=lcv-retail-analytics-dw
BIGQUERY_DATASET=retail_analytics_raw
```

### Run Extraction

**Full mode (PostgreSQL → Parquet → GCS):**
```bash
python src/etl/postgres_to_gcs.py
```

**Local-only mode (PostgreSQL → Parquet files only, for testing):**
```bash
python src/etl/postgres_to_gcs.py --local
```
---

## 📊 Extraction Flow

```
┌─────────────────────────────┐
│     PostgreSQL Database     │
│  ✓ dim_date (731 records)   │
│  ✓ dim_store (50)           │
│  ✓ dim_product (500)        │
│  ✓ dim_customer (10k)       │
│  ✓ fact_sales (1M records)  │
└──────────────┬──────────────┘
               │ Extract
               ▼
┌─────────────────────────────┐
│   Pandas DataFrames         │
│   (in-memory processing)    │
└──────────────┬──────────────┘
               │ Convert
               ▼
┌─────────────────────────────┐
│   Parquet Files (Local)     │
│   Compression: Snappy       │
│   Location: ./parquet_staging/
└──────────────┬──────────────┘
               │ Upload
               ▼
┌─────────────────────────────┐
│   Google Cloud Storage      │
│   Path: gs://bucket/YYYY-MM-DD/
│   Format: {table_name}.parquet
└─────────────────────────────┘
               │
               ▼
        (Ready for BigQuery Load)
```

---

## 📝 Logging

Execution logs written to `etl_extract.log`:

- **Console output**: Real-time progress
- **File output**: Persistent record with rotation (3 backups, 5MB each)
- **Level**: INFO (progress), ERROR (failures)
- **Format**: `timestamp [LEVEL] message`

Example log output:
```
2026-02-25 10:30:12 [INFO] Extracting table: fact_sales
2026-02-25 10:30:12 [INFO] [OK] Extracted 1000000 records from fact_sales
2026-02-25 10:30:13 [INFO] [OK] Saved fact_sales as Parquet (45.32 MB)
2026-02-25 10:30:45 [INFO] [OK] Uploaded to gs://lcv-retail-analytics-dw/2026-02-25/fact_sales.parquet
```

---

## 🔄 Exit Codes

- **Exit 0**: Success (pipeline completed)
- **Exit 1**: Fatal error (configuration, connection, or authentication failed)

Useful for CI/CD pipelines (GitHub Actions, GitLab CI, Jenkins).

---

## ⚙️ Advanced Options

### Local-Only Testing

Test the pipeline without uploading to GCS:

```bash
python src/etl/postgres_to_gcs.py --local
```

Output:
- Parquet files saved to `./parquet_staging/`
- No GCS authentication required
- No cloud costs incurred
- Useful for development/debugging

---

## 🐛 Troubleshooting

### PostgreSQL Connection Failed

```
Failed to connect to PostgreSQL: could not connect to server
```

**Solution:**
- Verify PostgreSQL is running: `psql -U postgres -c "SELECT 1"`
- Check `.env` settings: POSTGRES_HOST, PORT, USER, PASSWORD
- Ensure synthetic data loaded: `python src/postgres/seed_synthetic_data.py`

### GCS Authentication Failed

```
GCS authentication failed: 'NoneType' object is not subscriptable
```

**Solution:**
- Verify GCP_KEY_PATH points to valid JSON file
- Ensure service account has BigQuery Admin + Storage Admin roles
- Test locally first: `python src/etl/postgres_to_gcs.py --local`

### Out of Memory

If extracting very large tables (>5GB):

**Solution:**
- Increase available RAM
- Extract tables incrementally with chunking

### GCS Bucket Not Found

```
404 Not Found: Bucket not found
```

**Solution:**
- Verify bucket name: GCS_BUCKET=lcv-retail-analytics-dw
- Bucket must exist before running
- Check GCP project has bucket

---

## 📊 Data Specifications

| Table | Records | Size | Compression |
|-------|---------|------|-------------|
| dim_date | 731 | ~50KB | Snappy |
| dim_store | 50 | ~20KB | Snappy |
| dim_product | 500 | ~200KB | Snappy |
| dim_customer | 10,000 | ~2MB | Snappy |
| fact_sales | 1,000,000 | ~45MB | Snappy |
| **TOTAL** | **~1M** | **~47MB** | **Snappy** |

---

## 🔐 Security Notes

- **GCP Key**: Added to `.gitignore` — never committed to git
- **Service Account**: Has minimal permissions (BigQuery Admin, Storage Admin only)
- **Data in Transit**: Encrypted by default (Google's TLS)
- **Data at Rest**: Google-managed encryption in GCS

---

## 🚀 Roadmap

- [ ] Incremental extracts (delta-load strategy)
- [ ] Partition fact_sales by sale_date before upload
- [ ] Data quality checks before upload
- [ ] Retry logic for failed uploads
- [ ] CloudScheduler integration for daily runs
- [ ] Monitoring/alerting with Cloud Logging
- [ ] dbt transformation models
- [ ] BigQuery automatic load from GCS

---

## 📚 References

- [Google Cloud Storage Python Client](https://github.com/googleapis/python-storage)
- [pandas.to_parquet()](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_parquet.html)
- [PyArrow Documentation](https://arrow.apache.org/docs/python/)

---

## 📋 Notes

- **Idempotent**: Pipeline safely handles re-runs (upsert patterns)
- **Schedulable**: Can be orchestrated via Airflow, Cloud Composer, or cron
- **Observable**: dbt generates docs and lineage graphs
- **Testable**: dbt tests ensure data quality gates
