# PostgreSQL Module

This module handles database schema setup and synthetic data generation for the LCV Retail Analytics Platform.

---

## 📦 Contents

- `seed_synthetic_data.py` – Main script to generate and populate realistic retail data
- Database schema (SQL files through `seed_data.log` execution)

---

## 🚀 Quick Start

### Prerequisites

- PostgreSQL 12+ running and accessible
- Environment variables configured (see Configuration)
- Python dependencies installed (`psycopg2`, `python-dotenv`, `numpy`)

### Configuration

Create a `.env` file in the project root with:

```env
# Database (Required)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=lcv_retail_db

# Data Generation (Optional - defaults provided)
NUM_STORES=50
NUM_PRODUCTS=500
NUM_CUSTOMERS=10000
NUM_SALES=1000000
DATE_RANGE_DAYS=730
RANDOM_SEED=42
```

### Run Synthetic Data Generation

**Production scale** (50 stores, 10K customers, 1M sales):
```bash
python src/postgres/seed_synthetic_data.py
```

**Medium test** (25 stores, 5K customers, 50K sales, ~2-3 minutes):
```powershell
$env:NUM_STORES=25; $env:NUM_PRODUCTS=250; $env:NUM_CUSTOMERS=5000; $env:NUM_SALES=50000; python src/postgres/seed_synthetic_data.py
```

**Small test** (5 stores, 500 customers, 100 sales, ~10 seconds):
```powershell
$env:NUM_STORES=5; $env:NUM_PRODUCTS=50; $env:NUM_CUSTOMERS=500; $env:NUM_SALES=100; python src/postgres/seed_synthetic_data.py
```

This will:
1. **Validate schema** — Check tables exist before data insertion (fail fast)
2. **Connect to PostgreSQL** — Establish database connection
3. **Clear existing data** — Truncate dimension and fact tables
4. **Generate dimensions** — Date, store, product, customer
5. **Generate fact sales** — ~1M transactions in batches (batching prevents memory overflow)
6. **Create indexes** — For query optimization
7. **Track performance** — Log elapsed time (seconds and minutes)
8. **Exit gracefully** — Exit codes 0 (success) or 1 (fatal error) for CI/CD integration

---

## 📊 Generated Schema

### Dimension Tables

- **dim_date**: Calendar dimension (2-year range)
- **dim_store**: Store locations and metadata (50 stores, 5 regions)
- **dim_product**: Product catalog (500 items, 3 categories)
- **dim_customer**: Customer profiles (10K customers, loyalty tracking)

### Fact Tables

- **fact_sales**: ~1M transactions with quantity, pricing, discounts, margins, returns

---

## 🔍 Logging & Exit Codes

### Log Output
Execution logs are written to `seed_data.log`:

- **Console output**: Real-time progress
- **File output**: Persistent record with rotation (3 backups, 5MB each)
- **Level**: INFO (progress), ERROR (failures)
- **Format**: `timestamp [LEVEL] message`

Example log output:
```
2026-02-24 05:45:30 [INFO] Step 1/8: Validating target schema...
2026-02-24 05:45:33 [INFO] [OK] All required tables exist
2026-02-24 05:45:34 [INFO] Step 2/8: Clearing existing data...
2026-02-24 05:45:34 [INFO] [OK] Cleared existing data from all tables
2026-02-24 05:45:35 [INFO] Step 3/8: Generating date dimension...
2026-02-24 05:45:35 [INFO] Generating 731 date dimension records...
2026-02-24 05:45:35 [INFO] [OK] Inserted 731 date records
...
2026-02-24 05:48:03 [INFO] [OK] SYNTHETIC DATA GENERATION COMPLETED SUCCESSFULLY!
2026-02-24 05:48:03 [INFO] Pipeline completed successfully in 152.21 seconds (2.54 minutes)
```

### Exit Codes
- **Exit 0**: Success (allows CI/CD pipelines to proceed)
- **Exit 1**: Fatal error (CI/CD fails the build for debugging)

Useful for GitHub Actions, GitLab CI, Jenkins automation.

---

## ⚙️ Customization

### Adjust Dataset Sizes

Modify `.env` to scale data generation:

```env
NUM_STORES=100        # Default: 50
NUM_PRODUCTS=1000     # Default: 500
NUM_CUSTOMERS=50000   # Default: 10000
NUM_SALES=5000000     # Default: 1000000
```

### Change Random Seed

Set `RANDOM_SEED` to regenerate with different values (for testing):

```env
RANDOM_SEED=99  # Default: 42
```

---

## 🐛 Troubleshooting

### Connection Failed

```
psycopg2.OperationalError: could not connect to server
```

- Verify PostgreSQL is running
- Check `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD` in `.env`
- Verify database exists or permissions allow creation

### Table Already Exists

The script uses `TRUNCATE CASCADE` to clear tables. If schema doesn't exist:

- Ensure your PostgreSQL user has privileges to create tables
- Check that the database was properly initialized with schema

### Out of Memory

If generating very large datasets (~10M+ sales):

- Increase `DATE_RANGE_DAYS` to spread sales over longer period
- Check machine RAM availability
- Consider running in smaller batches

---

## 📝 Notes

- **Idempotent**: Script safely clears and regenerates data each run
- **Reproducible**: `RANDOM_SEED` ensures consistent results for testing
- **Auditable**: Full execution log with counts and timestamps
- **Optimized**: Batch inserts (10K records) for performance
