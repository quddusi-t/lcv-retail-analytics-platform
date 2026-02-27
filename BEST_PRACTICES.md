# 🎯 Developer Habits & Best Practices

**Universal roadmap for professional software development.**
A checklist to prevent common mistakes, maintain consistency, and deliver production-quality code.

---

## 📋 Pre-Project Initialization

### Environment Management
- [x] **Create `.env` file immediately** — Store all secrets, API keys, database credentials, tokens
  - [x] Never commit `.env` to git (excluded in `.gitignore`)
  - [x] Add `.env` to `.gitignore` (checked on line 2)
  - [x] Document required env vars in `.env.template` (includes PostgreSQL, GCP, API, dbt config)
  - **Next step**: Copy `.env.template` to `.env` and fill in actual values

- [x] **Validate required environment variables — Fail Fast**
  ```python
  from dotenv import load_dotenv
  import os

  load_dotenv()

  # Validate required env vars immediately (prevents silent misconfigurations)
  required_vars = ["POSTGRES_HOST", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"]
  missing_vars = [var for var in required_vars if not os.getenv(var)]
  if missing_vars:
      raise RuntimeError(
          f"Missing required environment variables: {', '.join(missing_vars)}. "
          f"Please set them in .env or as system environment variables."
      )
  ```
  - **Why?** Prevents runtime failures after hours of processing (fail at startup instead)
  - **Example error**: `RuntimeError: Missing required environment variables: POSTGRES_HOST. Please set them in .env or as system environment variables.`
  - **Benefit**: Immediate feedback, saves time debugging

- [x] **Create `.gitignore` before first commit**
  - [x] Standard ignores: `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `*.pyc`, `*.egg-info/`
  - [x] IDE ignores: `.vscode/`, `.idea/`, `.DS_Store`, `*.swp`
  - [x] Local env: `.env`, `.env.local`, `config.local.yml`
  - [x] Build artifacts: `dist/`, `build/`, `.coverage/`

### Virtual Environments
- [x] **Isolate dependencies** — Use venv/virtualenv/conda for every project
  - [x] `.venv/` created and activated
  - [x] Never use system Python
  - [x] Document setup in README: `python -m venv venv` or `conda create -n project_name`
- [x] **Pin dependency versions** — Create `requirements.txt` or `pyproject.toml`
  - [x] `pyproject.toml` configured with uv package manager
  - [x] Document major versions with comments
  - Note: Used `uv` (faster, modern alternative to pip)

### Git Configuration
- [x] **Initialize git repo before writing code**
  - [x] Git repo initialized with atomic commit history
  - [x] Pre-commit hooks configured (black, ruff, trailing-whitespace fixes)
- [x] **Create `.gitattributes`** — Covered in `.gitignore`
  - Consistent line endings enforced by pre-commit hooks

---

## 💾 Atomic Commits (Most Critical)

### Commit Philosophy
**One logical change = One commit. Never mix multiple features/fixes in a single commit.**

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style (formatting, semicolons, etc.)
- `refactor:` Code refactoring (no feature change)
- `perf:` Performance improvements
- `test:` Add or update tests
- `chore:` Build, dependency updates, tooling
- `ci:` CI/CD configuration

### Examples of Good Atomic Commits

✅ **GOOD:**
```bash
git commit -m "feat: add RFM segmentation SQL query"
git commit -m "test: add unit tests for RFM calculation"
git commit -m "docs: document RFM business logic in data dictionary"
git commit -m "refactor: optimize RFM query with indexes"
```

❌ **BAD:**
```bash
git commit -m "lots of changes"
git commit -m "add RFM, fix bugs, update docs, and optimize queries"
git commit -m "wip"
```

### Before Every Commit
- [ ] **Review what you're committing** — `git diff` before staging
- [ ] **Test the code** — Run tests/linter/type checker locally
- [ ] **Write a meaningful message** — Explain WHY, not WHAT
- [ ] **One feature per commit** — Don't mix concerns

### Commit Workflow
```bash
# 1. Check what changed
git status
git diff

# 2. Stage only related changes
git add path/to/related/files
git add -p  # Interactive staging (stage chunks, not whole files)

# 3. Commit with clear message
git commit -m "feat: implement user authentication module"

# 4. Verify before push
git log --oneline -3
git push origin feature-branch
```

---

## 🏗️ Code Organization

### Directory Structure
- [ ] **Keep source code organized by layer/domain**
  ```
  src/
  ├── analytics/    (business logic, queries)
  ├── etl/         (data pipelines)
  ├── ml/          (model training, inference)
  ├── postgres/    (database setup, migrations)
  └── utils/       (shared utilities)
  ```

- [ ] **Separate concerns**
  - Data models in one place
  - Business logic in another
  - API endpoints separate from core logic
  - Always follow monorepo or multi-repo strategy consistently

### File Naming
- [ ] **Use descriptive, snake_case names** (Python) or camelCase (JS)
  - Good: `seed_synthetic_data.py`, `rfm_segmentation.sql`
  - Bad: `data.py`, `query.sql`, `script1.py`

- [ ] **Group related files**
  - All models together: `models/`, `models/staging/`, `models/marts/`
  - All tests together: `tests/unit/`, `tests/integration/`
  - All configs together: `config/`, `config/dev.yml`, `config/prod.yml`

---

## ✍️ Documentation (As You Go)

### README
- [ ] **Write README first** — Describes what, why, how
  - Project goal
  - Quick start (4 steps max)
  - Architecture overview
  - Development setup
  - Configuration instructions
  - Example usage

### Inline Comments
- [ ] **Comment WHY, not WHAT**
  - BAD: `x = x + 1  # increment x`
  - GOOD: `x = x + 1  # offset by 1 to match 1-indexed schema`

- [ ] **Use docstrings for functions/classes**
  ```python
  def calculate_rfm_score(customer_id: int, lookback_days: int = 90) -> dict:
      """
      Calculate RFM (Recency, Frequency, Monetary) score for a customer.

      Args:
          customer_id: Unique customer identifier
          lookback_days: Historical window in days (default 90)

      Returns:
          dict with keys 'recency', 'frequency', 'monetary', 'score'

      Raises:
          ValueError: If customer_id not found in database
      """
  ```

### Data Dictionary
- [ ] **Document every table, column, and transformation**
  - Table name, purpose, grain
  - Column name, data type, business meaning, nullable?
  - Example: "customer_id: INT, unique identifier for customer, NOT NULL"

### Architecture Diagram
- [ ] **Include data flow diagram**
  - Sources → ETL → Warehouse → BI/ML
  - Use tools: Mermaid, Lucidchart, Draw.io
  - Update when architecture changes

### Changelog
- [ ] **Keep `CHANGELOG.md` or `HISTORY.md`**
  - What changed, when, why
  - Format: date, version, breaking changes highlighted
  - Example: "v1.2.0 — 2026-02-19 — Added RFM segmentation, deprecated batch_size parameter"

---

## 🧪 Testing & Quality

### Write Tests
- [ ] **Test-driven development (TDD) or write tests alongside code**
  - Unit tests: Test individual functions
  - Integration tests: Test features end-to-end
  - Data tests: Validate data quality (dbt tests, SQL checks)

- [ ] **Organize tests to mirror source structure**
  ```
  tests/
  ├── unit/
  │   ├── test_rfm_calculation.py
  │   └── test_churn_model.py
  ├── integration/
  │   └── test_etl_pipeline.py
  └── data/
      └── test_quality_checks.sql
  ```

### Code Quality
- [ ] **Use linters and formatters**
  - Python: `black`, `ruff`, `pylint`
  - SQL: `sqlfluff`
  - Use pre-commit hooks to auto-check

- [ ] **Type hints (Python)**
  ```python
  def load_data(path: str, limit: int = None) -> pd.DataFrame:
      ...
  ```

- [ ] **Configure pre-commit hooks**
  ```bash
  # .pre-commit-config.yaml
  repos:
    - repo: https://github.com/psf/black
      rev: 23.1.0
      hooks:
        - id: black
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.1.0
      hooks:
        - id: ruff
  ```

### Run Tests Before Committing
```bash
pytest tests/
python -m black --check src/
python -m ruff check src/
```

---

## 🔐 Secrets & Configuration

### Environment Variables
- [ ] **Use `.env` for local development**
  ```bash
  DATABASE_URL=postgresql://user:password@localhost/dbname
  GCP_PROJECT_ID=my-gcp-project
  API_KEY=sk-abc123xyz
  ENVIRONMENT=development
  ```

- [ ] **Create `.env.example` or `ENV_TEMPLATE.md`**
  ```bash
  # .env.example
  DATABASE_URL=postgresql://user:password@host/dbname
  GCP_PROJECT_ID=your-gcp-project-id
  API_KEY=your-api-key
  ```

- [ ] **Never hardcode secrets**
  - Load from environment: `os.getenv("DATABASE_URL")`
  - Use config management tools for production

### CI/CD Secrets
- [ ] **Use GitHub Secrets, GitLab CI Variables, or platform equivalents**
  - Store in secure vault
  - Rotate regularly
  - Document what each secret is used for

### Domain Constants & Business Rules
- [ ] **Separate domain constants from configuration**
  ```python
  # ✅ GOOD: Keep small, stable constants in code
  REGIONS = ["North", "South", "East", "West"]
  PRODUCT_CATEGORIES = {"Textile": [...], "Accessories": [...]}

  # ✅ Configurable params from environment
  NUM_STORES = int(os.getenv("NUM_STORES", 50))
  NUM_PRODUCTS = int(os.getenv("NUM_PRODUCTS", 500))
  ```

- [ ] **Move to external config (YAML/JSON) when:**
  - Business rules change frequently (no code deploy needed)
  - Supporting multiple environments with different constants
  - Number of constants grows significantly (50+ items)
  - International expansion requires regional customization

- [ ] **Current approach is pragmatic for MVP:**
  - Code constants work fine for stable, small datasets
  - Easy to version control and review
  - Upgrade to external config in Week 3-4 if needed

---

## 📦 Dependency Management

### Track Dependencies
- [ ] **Maintain single source of truth for dependencies**
  - `requirements.txt` (Python)
  - `pyproject.toml` + `poetry.lock` (Python with Poetry)
  - `package.json` + `package-lock.json` (Node.js)
  - `Gemfile` + `Gemfile.lock` (Ruby)

- [ ] **Document why each dependency exists**
  ```python
  # requirements.txt
  pandas==1.5.3        # Data manipulation
  apache-airflow==2.5.0  # Workflow orchestration
  pytest==7.2.1        # Testing framework
  ```

### Update Dependencies Safely
- [ ] **Check for breaking changes before updating**
  ```bash
  pip list --outdated
  pip install --upgrade package_name --dry-run
  ```

- [ ] **Test after updating dependencies**
  - Run full test suite
  - Check for compatibility issues

---

## 🚀 Deployment & DevOps

### Docker (if applicable)
- [ ] **Use `.dockerignore`** — Similar to `.gitignore`
  ```
  .git
  .gitignore
  .env
  __pycache__
  venv/
  .pytest_cache/
  *.pyc
  ```

- [ ] **Dockerfile best practices**
  - Use specific base image tags (not `latest`)
  - Pin RUN command package versions
  - Multi-stage builds for smaller images
  - `FROM python:3.11-slim` not `FROM python:latest`

### CI/CD Pipeline
- [ ] **Automate tests on every push**
  - GitHub Actions, GitLab CI, Jenkins, etc.
  - Run: tests, linting, type checking, security scans

- [ ] **Automate deployments**
  - Dev: Auto-deploy on main
  - Staging: Manual or schedule-based
  - Production: Manual approval required

### Monitoring & Logging
- [x] **Add structured logging with rotation**
  ```python
  import logging
  from logging.handlers import RotatingFileHandler

  logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s [%(levelname)s] %(message)s",
      handlers=[
          logging.StreamHandler(),  # console output
          RotatingFileHandler(
              "app.log", maxBytes=5_000_000, backupCount=3
          )  # 5MB files, keep 3 backups
      ],
  )
  logger = logging.getLogger(__name__)
  logger.info(f"Processing customer {customer_id}")
  logger.error(f"Failed to load data: {error}")
  ```
  - **Why rotating?** Prevents unbounded log file growth; keeps last 3 rotations (15MB max)
  - **Console + File**: Immediate visibility during dev, permanent record for debugging

- [x] **Suppress noisy third-party logs**
  ```python
  # Reduce verbosity from chatty libraries (psycopg2, urllib3, etc.)
  logging.getLogger("psycopg2").setLevel(logging.WARNING)
  logging.getLogger("urllib3").setLevel(logging.WARNING)
  ```
  - **Why?** Database drivers log internal protocol; clutters your application logs
  - **Result**: Only see YOUR events, not driver noise

- [ ] **Avoid emojis in log messages and scripts**
  - ❌ BAD: `logger.info("✅ Data loaded successfully")`
  - ✅ GOOD: `logger.info("[OK] Data loaded successfully")`
  - **Reason**: Emojis cause encoding issues on Windows terminals (charmap codec errors), CI/CD systems, and log aggregation pipelines that expect ASCII-only output. Use `[OK]`, `[ERROR]`, `[WARNING]` instead.

- [ ] **Plan for observability at scale** (future enhancement)
  - Current: Text logs to file ✅
  - Next: Structured JSON logging when adding ELK/Datadog (Week 3+)
  - **Why JSON?** Machine-parseable for log aggregation platforms; enables metrics extraction, anomaly detection, automated alerting
  - Tools: `python-json-logger`, Datadog Agent, ELK Stack, Splunk

- [ ] **Monitor in production**
  - Track errors, latency, resource usage
  - Set up alerts for failures
  - Log to centralized system (Datadog/ELK) for multi-service visibility

---

## 🔄 Code Review

### Before Merging
- [ ] **Create pull request (PR) with clear description**
  - What changed and why
  - Link to related issues
  - Screenshots (if UI)
  - Testing instructions

- [ ] **Request code review** — Never merge your own code
  - At least 1 other person reviews
  - Address all comments before merging

- [ ] **Ensure CI passes**
  - All tests pass
  - No linting errors
  - No security warnings

- [ ] **Squash or rebase** (optional)
  - Keep history clean: `git rebase -i origin/main`
  - Avoid "fix typo" commits in final history

---

## 🗂️ Project-Specific Habits

### Data Projects (SQL, dbt, Analytics)
- [ ] **Version control for SQL**
  - Store all DDL statements in `.sql` files
  - Version your data migrations
  - Use dbt for transformation logic

- [ ] **Test data quality**
  - Unit tests for transformations
  - Data profiling tests (nulls, duplicates, ranges)
  - Validation queries

- [ ] **Document data lineage**
  - Source → raw → staging → marts
  - Add comments in dbt models
  - Link to business glossary

### ML/AI Projects
- [ ] **Track training data versions**
  - Which dataset was used for training?
  - Random seed for reproducibility
  - Data splits documented

- [ ] **Version models**
  - Store models with metadata (date, performance, hyperparams)
  - Use MLflow, DVC, or similar

- [ ] **Document model assumptions**
  - Features used
  - Training period
  - Performance metrics
  - Known limitations

### Python Projects
- [x] **Use type hints everywhere**
  ```python
  from typing import Optional, List
  def process(data: List[dict], limit: Optional[int] = None) -> dict:
      ...
  ```

- [x] **Use context managers for resource management**
  ```python
  # ❌ BAD: Manual resource handling
  connection = create_connection()
  try:
      do_work(connection)
  finally:
      connection.close()

  # ✅ GOOD: Context manager ensures cleanup even on exceptions
  with create_connection() as connection:
      do_work(connection)

  # Implement context managers in classes:
  class DatabaseGenerator:
      def __enter__(self):
          self.connect()
          return self

      def __exit__(self, exc_type, exc_val, exc_tb):
          self.disconnect()
          return False  # Don't suppress exceptions
  ```
  - **Benefit**: Guarantees resource cleanup (files, DB connections, locks, etc.)
  - **Example**: `with SyntheticDataGenerator(db_config) as gen: gen.generate_all()`

- [x] **Use custom exceptions for domain errors**
  ```python
  class DataGenerationError(Exception):
      """Raised when synthetic data generation fails."""
      pass

  # Usage:
  try:
      generate_data()
  except DataGenerationError as e:
      logger.error(f"Data generation failed: {e}")
      raise
  ```
  - **Benefit**: Clearer error handling upstream; domains errors distinct from system errors

- [ ] **Use dataclasses or Pydantic for data models**
  ```python
  from dataclasses import dataclass

  @dataclass
  class Customer:
      customer_id: int
      name: str
      email: str
  ```

---

## 📋 Project Launch Checklist

Before pushing to production or sharing publicly:

- [ ] All tests pass locally and in CI
- [ ] Code reviewed by at least one peer
- [ ] No hardcoded secrets
- [ ] `.env.example` exists with template
- [ ] `.gitignore` excludes all sensitive files
- [ ] README is complete and accurate
- [ ] CHANGELOG updated
- [ ] Docstrings added to all functions
- [ ] Architecture diagram up-to-date
- [ ] Performance benchmarked (if applicable)
- [ ] Error handling implemented (no bare `except:`)
- [ ] Logging added (at DEBUG, INFO, ERROR levels)
- [ ] Dependencies documented in requirements file
- [ ] Commit history is clean (meaningful messages, atomic commits)
- [ ] Database migrations tested (if applicable)
- [ ] No TODO comments left in code (or tracked in issues)

---

## 🎓 Principles to Live By

| Principle | Meaning |
|-----------|---------|
| **DRY** | Don't Repeat Yourself — Extract reusable functions |
| **KISS** | Keep It Simple, Stupid — Avoid over-engineering |
| **SOLID** | Single Responsibility, Open/Closed, Liskov, Interface, Dependency — Design patterns |
| **YAGNI** | You Aren't Gonna Need It — Don't add features you don't need yet |
| **SoC** | Separation of Concerns — Different layers do different things |
| **Atomic** | Each commit is a complete, working change |
| **Explicit** | Clear > clever; readable code > compact code |

---

## 🚀 MVP (Minimum Viable Product) Philosophy

**Definition:** Release the smallest feature set that solves the core problem and creates value immediately.

**Core Principles:**
- ✅ Works end-to-end (even if not optimized)
- ✅ Solves the real problem
- ✅ Measurable success criteria
- ✅ Fast feedback loop
- ❌ Don't over-engineer "just in case"

**In Data Engineering Context:**
```
MVP: Generate 1M transactions + load to PostgreSQL with basic quality checks
❌ NOT MVP: Real-time pipelines, distributed processing, Kubernetes, etc.
```

**When to Optimize Beyond MVP:**
- **Measure first**: Identify the actual bottleneck (don't guess)
- **Prove problem**: Show that current approach is too slow/expensive
- **Simple → complex**: executemany() → batch loading → COPY FROM → streaming

---

## 🗄️ Database Operations: Scale-Appropriate Approaches

### **Data Loading: Three Tiers**

| Approach | Records | Speed | When to Use | Complexity |
|----------|---------|-------|-------------|------------|
| **executemany()** | < 1M | ~10k rows/sec | MVP, development, error handling needed | ⭐ |
| **Batch + COPY** | 1M-100M | ~100k rows/sec | Production data loads, ETL pipelines | ⭐⭐ |
| **Streaming (Kafka)** | 100M+ | Continuous | Real-time ingestion, 24/7 pipelines | ⭐⭐⭐ |

### **Analogy: Moving Boxes**

```
executemany():  🚶 Walk through door one box at a time (show ticket each time)
COPY FROM:      🚚 Back truck to dock, dump all boxes at once
Kafka Stream:   🏗️  Conveyor belt (boxes arrive continuously)
```

### **COPY FROM vs executemany()** (PostgreSQL Example)

```python
# ❌ Current: Individual INSERT statements (MVP appropriate)
insert_query = "INSERT INTO sales (...) VALUES (%s, %s, ...)"
cursor.executemany(insert_query, records_list)  # Each row: parse → bind → execute
# Speed: ~30-50 sec for 1M records

# ✅ Future: PostgreSQL bulk load (when scaling)
import io
csv_buffer = io.StringIO()
for record in records:
    csv_buffer.write(f"{record[0]},{record[1]},...\n")
csv_buffer.seek(0)
cursor.copy_from(csv_buffer, 'sales', columns=['col1', 'col2', ...])
# Speed: ~3-5 sec for 1M records (10x faster!)
```

**Why COPY is faster:**
- Skips SQL parsing overhead
- Direct data format (binary or CSV)
- Single index update pass
- Optimized for sequential writes

**When to upgrade from executemany to COPY:**
- Volume > 5M records
- Measured latency > acceptable threshold
- Cost/time clearly justifies refactoring

---

## ☁️ Cloud Infrastructure & Credentials (GCP, BigQuery, GCS)

### Service Account & Authentication Setup

- [x] **Create GCP Service Account (never use personal account)**
  ```
  GCP Console → Service Accounts → Create Service Account
  - Name: etl-pipeline (descriptive, lowercase)
  - Grant roles: BigQuery Admin, Storage Admin
  - Create JSON key file (download & store securely)
  ```
  - **Why separate account?** Audit trail, revoke access without touching personal account, CI/CD-safe
  - **Key file location:** Store in project root: `./gcp-key.json` (add to `.gitignore`)
  - **Never commit key files** — They're authentication tokens equivalent to passwords

- [x] **Store GCP credentials in `.env`**
  ```bash
  # .env (never commit this)
  GCP_PROJECT_ID=lcv-retail-analytics-dw
  GCP_KEY_PATH=./lcv-gcp-key.json
  GCS_BUCKET=lcv-retail-analytics-dw
  BIGQUERY_DATASET=retail_analytics_raw
  ```

  ```bash
  # .env.template (safe to commit, shows structure)
  GCP_PROJECT_ID=your-project-id
  GCP_KEY_PATH=path/to/service-account-key.json
  GCS_BUCKET=your-bucket-name
  BIGQUERY_DATASET=your_dataset_name
  ```

- [x] **Authenticate in Python with service account**
  ```python
  from google.oauth2 import service_account
  from google.cloud import storage
  import os
  from dotenv import load_dotenv

  load_dotenv()

  # Load service account key
  key_path = os.getenv("GCP_KEY_PATH")
  credentials = service_account.Credentials.from_service_account_file(
      key_path,
      scopes=["https://www.googleapis.com/auth/cloud-platform"]
  )

  # Initialize GCS client
  storage_client = storage.Client(credentials=credentials)
  bucket = storage_client.bucket(os.getenv("GCS_BUCKET"))
  ```

### Google Cloud Storage (GCS) Best Practices

- [x] **Organize with date-partitioned folders**
  ```
  gs://bucket-name/
  ├── 2026-02-25/
  │   ├── dim_date.parquet
  │   ├── dim_store.parquet
  │   └── fact_sales.parquet
  ├── 2026-02-26/
  │   ├── dim_date.parquet
  │   ├── dim_store.parquet
  │   └── fact_sales.parquet
  ```
  - **Why?** YYYY-MM-DD format makes archival, versioning, and troubleshooting easy
  - Enables BigQuery partition pruning (scan only needed dates)
  - Simple data lineage: "which files loaded yesterday?"

- [x] **Use Parquet format with Snappy compression**
  ```python
  df.to_parquet(
      path,
      engine="pyarrow",
      compression="snappy",  # Best compression/speed tradeoff
      coerce_timestamps="us"  # Ensure timestamp compatibility
  )
  ```
  - **Parquet benefits:** Columnar (scan only needed cols), 60-80% compression, schema enforcement
  - **Snappy tradeoff:** ~1.5-2x faster than gzip, ~10-15% larger; good for ETL pipelines
  - **Use gzip instead if:** Storage cost >> compute cost (archive data)

- [x] **Validate file uploads**
  ```python
  blob = bucket.blob(f"{date}/table.parquet")
  blob.upload_from_filename(local_path)

  # Verify: compare file sizes
  local_size = os.path.getsize(local_path)
  gcs_size = blob.size
  assert local_size == gcs_size, f"Upload mismatch: {local_size} != {gcs_size}"
  ```

### BigQuery Best Practices

- [x] **Create datasets with appropriate locations**
  ```python
  from google.cloud import bigquery

  client = bigquery.Client(credentials=credentials)
  dataset_id = os.getenv("BIGQUERY_DATASET")
  dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
  dataset.location = "US"  # Multi-region for availability
  dataset = client.create_dataset(dataset, exists_ok=True)
  ```
  - **Location:** "US" (multi-region) for high availability, "us-east1" if cost is critical
  - **Separate datasets:** `raw` (GCS import), `staging` (dbt), `marts` (analytics)

- [x] **Use External Tables for Parquet in GCS (cheap exploration)**
  ```sql
  CREATE OR REPLACE EXTERNAL TABLE raw.fact_sales
  OPTIONS (
    format = 'PARQUET',
    uris = ['gs://bucket-name/2026-02-26/*.parquet'],
    hive_partition_uri_prefix = 'gs://bucket-name/',
    require_partition_filter = false
  );
  ```
  - **External table scanning:** $7.25/TB (same as regular query)
  - **Native table copy:** $0.023/GB first 100GB/month (cheaper for frequent access)
  - **Strategy:** Explore with external → copy to native when stable

- [x] **Load GCS Parquet into native BigQuery table**
  ```sql
  CREATE OR REPLACE TABLE raw.fact_sales AS
  SELECT * FROM `project.raw.fact_sales_external`;
  ```
  - Copies data into BigQuery's columnar storage
  - Enables clustering, partitioning, incremental loads
  - ~3-5x faster than external tables for repeated queries

- [x] **Always partition & cluster large tables**
  ```sql
  CREATE OR REPLACE TABLE marts.fact_sales (
    sale_id INT64,
    sale_date DATE,
    store_id INT64,
    amount NUMERIC(10, 2)
  )
  PARTITION BY sale_date
  CLUSTER BY store_id
  AS SELECT * FROM raw.fact_sales;
  ```
  - **Partitioning:** Prune entire date ranges (10-100x scan reduction)
  - **Clustering:** Sort within partitions (column filtering speedup)
  - **Cost impact:** Can reduce query costs 50-80% on large tables

### Secrets & Credentials Patterns

- [x] **NEVER hardcode secrets**
  ```python
  # ❌ BAD
  key_path = "/absolute/path/to/key.json"
  password = "super_secret_123"

  # ✅ GOOD
  key_path = os.getenv("GCP_KEY_PATH")
  password = os.getenv("POSTGRES_PASSWORD")
  ```

- [x] **Rotate credentials periodically**
  - Service account keys: 90-day rotation (automatic alerts in GCP)
  - Database passwords: Every 6 months minimum
  - Check git history: `git log -p | grep -i "password\|key\|secret"` (should be empty)

- [x] **Use `.env` template pattern**
  ```bash
  # .env.template (commit this)
  POSTGRES_HOST=localhost
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=your_password_here
  GCP_KEY_PATH=./path/to/key.json

  # .env (never commit)
  POSTGRES_HOST=localhost
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=malezya2652%&
  GCP_KEY_PATH=./lcv-gcp-key.json
  ```

- [x] **Validate credentials at startup (Fail-Fast)**
  ```python
  def validate_gcp_credentials():
      """Validate GCP service account key exists and is readable"""
      key_path = os.getenv("GCP_KEY_PATH")
      if not os.path.exists(key_path):
          raise FileNotFoundError(f"GCP key not found: {key_path}")
      try:
          from google.oauth2 import service_account
          service_account.Credentials.from_service_account_file(key_path)
      except Exception as e:
          raise ValueError(f"Invalid GCP key: {e}")
      logger.info(f"✓ GCP credentials validated: {key_path}")

  # Call at application startup
  validate_gcp_credentials()
  ```

---

## 🔄 ETL Pipeline Patterns (Extract, Transform, Load)

- [x] **Use context managers for resource cleanup**
  ```python
  class DataExtractor:
      def __init__(self, db_config, gcs_credentials):
          self.db_config = db_config
          self.gcs_credentials = gcs_credentials
          self.db_conn = None
          self.gcs_client = None

      def __enter__(self):
          self.db_conn = create_connection(self.db_config)
          self.gcs_client = storage.Client(credentials=self.gcs_credentials)
          return self

      def __exit__(self, exc_type, exc_val, exc_tb):
          """Cleanup: close connections regardless of success/failure"""
          if self.db_conn:
              self.db_conn.close()
          return False  # Don't suppress exceptions

  # Usage
  with DataExtractor(config, creds) as extractor:
      data = extractor.extract_table("sales")
  ```
  - **Why?** Guarantees cleanup even if exception occurs (prevents resource leaks)

- [x] **Implement idempotent pipelines**
  ```python
  # ✅ If pipeline crashes halfway, re-run produces same result
  # Upload with date-based path (skip if file exists)
  gcs_path = f"gs://bucket/{YYYY-MM-DD}/table.parquet"
  if not blob_exists(gcs_path):
      upload_to_gcs(data, gcs_path)
  else:
      logger.info(f"Skipping {gcs_path} (already uploaded)")
  ```

- [x] **Add timestamps & exit codes for monitoring**
  ```python
  import sys
  from datetime import datetime

  def main():
      start_time = datetime.now()
      try:
          logger.info("Pipeline started")
          extract_and_load_data()
          elapsed = (datetime.now() - start_time).total_seconds()
          logger.info(f"✓ Pipeline completed in {elapsed:.2f} seconds")
          sys.exit(0)  # Success
      except Exception as e:
          logger.error(f"✗ Pipeline failed: {e}", exc_info=True)
          sys.exit(1)  # Failure
  ```
  - **Exit codes:** 0 = success, 1 = fatal error (CI/CD can detect failures)
  - **Elapsed time:** Monitor performance trends

- [x] **Log extraction metadata**
  ```python
  logger.info(f"[OK] Extracted {record_count} records from {table_name}")
  logger.info(f"[OK] Saved {table_name}.parquet ({file_size_mb:.2f} MB)")
  logger.info(f"[OK] Uploaded to gs://{bucket}/{date}/{table_name}.parquet")
  ```
  - **Why?** Audit trail, debugging, monitoring pipeline health

---

## 📊 BigQuery Loading Patterns (GCS → BigQuery)

### Comparing Three Approaches

When loading Parquet files from GCS into BigQuery, you have three options. Here's the comparison:

| Approach | Method | Pros | Cons | Best For |
|----------|--------|------|------|----------|
| **Python Script** | `bigquery.Client.load_table_from_uri()` | ✅ Automated, version controlled, error handling, extensible, schedulable | Requires library | **Production pipelines** |
| **bq CLI** | `bq load --source_format=PARQUET` | ✅ Simple one-liners, easy testing | ❌ Manual per-table, no version control, hard to scale | Ad-hoc exploration |
| **External Tables** | `CREATE EXTERNAL TABLE ... OPTIONS(format='PARQUET')` | ✅ Fast preview, minimal setup | ❌ Slow queries, repeated GCS scans, not production-ready | Quick data exploration |

**Winner: Python Script** 🏆

### Implementation: Python Script (Recommended)

**Why Python = Production Standard:**
```
1. Extract (Python) → GCS Parquet files
2. Load (Python) → BigQuery native tables ← YOU ARE HERE
3. Transform (dbt) → Staging/mart models
4. Schedule → Airflow/Cloud Scheduler runs all three daily
```

- ✅ **Automated** — Single command loads all tables
- ✅ **Version controlled** — Code in git, reproducible
- ✅ **Error handling** — Fail-fast, comprehensive logging
- ✅ **Orchestration-ready** — Easy to schedule with Airflow, Cloud Scheduler, cron
- ✅ **Scalable** — Same pattern works for 5 tables or 500
- ✅ **Maintainable** — Team can understand & modify code

```python
# Example: Load all Parquet files from GCS to BigQuery
from google.cloud import bigquery
from google.oauth2 import service_account

class GCSToBigQueryLoader:
    def __init__(self, project_id, key_path, bucket, dataset):
        credentials = service_account.Credentials.from_service_account_file(key_path)
        self.bq_client = bigquery.Client(project=project_id, credentials=credentials)
        self.project_id = project_id
        self.dataset = dataset
        self.bucket = bucket

    def load_parquet_to_bigquery(self, gcs_uri: str, table_name: str) -> None:
        """Load single Parquet file from GCS to BigQuery native table."""
        table_id = f"{self.project_id}.{self.dataset}.{table_name}"

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            autodetect=True,  # Auto-infer schema from Parquet
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrite
        )

        load_job = self.bq_client.load_table_from_uri(
            gcs_uri, table_id, job_config=job_config
        )
        load_job.result()  # Wait for completion

        table = self.bq_client.get_table(table_id)
        logger.info(f"[OK] Loaded {table.num_rows} rows into {table_id}")

    def load_all_tables(self, date: str) -> None:
        """Load all Parquet files from a date into BigQuery."""
        files = self.list_parquet_files(date)  # e.g., ["dim_store.parquet", ...]

        for file_name in files:
            table_name = file_name.replace(".parquet", "")
            gcs_uri = f"gs://{self.bucket}/{date}/{file_name}"
            self.load_parquet_to_bigquery(gcs_uri, table_name)

# Usage
with GCSToBigQueryLoader(project_id, key_path, bucket, dataset) as loader:
    loader.load_all_tables("2026-02-27")  # Loads all tables with one call
```

**Key features:**
- ✅ Schema auto-detection from Parquet
- ✅ `WRITE_TRUNCATE` mode (idempotent: safe to re-run)
- ✅ Error handling + logging
- ✅ Works with context managers (automatic cleanup)

### When to Use Each Approach

**Use Python Script if:**
- ✅ You have 2+ tables to load
- ✅ You want automated, schedulable pipelines
- ✅ You need error handling and logging
- ✅ You value version control & team reproducibility

**Use bq CLI if:**
- ✅ One-off load (manual, ad-hoc)
- ✅ Testing a single table
- ✅ You prefer shell scripts

**Use External Tables if:**
- ✅ You want to explore data before copying
- ✅ Cost is not a concern (repeated GCS scans)
- ✅ Data changes frequently and you don't want to copy

### BigQuery Load Configuration Best Practices

```python
job_config = bigquery.LoadJobConfig(
    # Schema handling
    source_format=bigquery.SourceFormat.PARQUET,
    autodetect=True,  # Let BigQuery infer schema from file
    # OR specify schema explicitly for stricter validation

    # Data deduplication
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    # Options: WRITE_TRUNCATE (overwrite), WRITE_APPEND (insert), WRITE_EMPTY (fail if exists)

    # Timestamps
    time_partitioning=bigquery.TimePartitioning(type_="DAY", field="date_column"),
    # Optional: partition large tables by date for faster queries

    # Clustering for performance
    clustering_fields=["store_id", "product_id"],
    # Optional: co-locate related rows for query speedup
)

load_job = self.bq_client.load_table_from_uri(gcs_uri, table_id, job_config=job_config)
load_job.result()  # Wait for completion with .result()
```

**Common configurations:**
- `autodetect=True` — Let BigQuery infer schema (fast setup, less validation)
- `autodetect=False` + explicit schema — Strict validation (catches schema issues early)
- `WRITE_TRUNCATE` — Idempotent (safe for nightly re-runs)
- `time_partitioning` — For large tables (fact tables with dates)
- `clustering_fields` — Co-locate rows for query performance

---

## 🧠 Mental Checklist Before Pushing

```
Before each git push, ask yourself:

1. ✅ Did I test this locally?
2. ✅ Did I write/update tests?
3. ✅ Did I run linter/formatter?
4. ✅ Did I add comments where needed?
5. ✅ Did I check .gitignore? (no .env, no venv/)
6. ✅ Is my commit message clear and atomic?
7. ✅ Did I remove debugging code? (print, console.log, etc.)
8. ✅ Did I update documentation?
9. ✅ Is there any hardcoded data/secrets?
10. ✅ Would my team understand this in 6 months?
```

---

## 📚 References & Tools

- **Git**: [Git Book](https://git-scm.com/book/en/v2)
- **Conventional Commits**: [conventionalcommits.org](https://www.conventionalcommits.org/)
- **Python Style**: [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- **Pre-commit**: [pre-commit.com](https://pre-commit.com/)
- **dbt Best Practices**: [dbt Docs](https://docs.getdbt.com/)
- **Data Quality**: [Great Expectations](https://greatexpectations.io/)
- **SQL Linting**: [SQLFluff](https://www.sqlfluff.com/)

---

**Last Updated**: February 27, 2026
**Purpose**: Universal roadmap for professional development practices
**Latest Additions**: GCP/BigQuery setup, credentials management, ETL pipeline patterns, BigQuery loading patterns (Python vs CLI vs External Tables)
