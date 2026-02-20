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

```bash
python src/postgres/seed_synthetic_data.py
```

This will:
1. Connect to PostgreSQL
2. Clear existing dimension and fact tables
3. Generate and insert dimension tables (date, store, product, customer)
4. Generate and insert ~1M sales fact records in batches
5. Create indexes for query optimization
6. Write execution log to `seed_data.log`

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

## 🔍 Logging

Execution logs are written to `seed_data.log`:

- **Console output**: Real-time progress
- **File output**: Persistent record with rotation (3 backups, 5MB each)
- **Level**: INFO (progress), ERROR (failures)
- **Format**: `timestamp [LEVEL] message`

Example log output:
```
2026-02-20 10:30:12 [INFO] Step 1/7: Clearing existing data...
2026-02-20 10:30:12 [INFO] ✅ Cleared existing data from all tables
2026-02-20 10:30:13 [INFO] Step 2/7: Generating date dimension...
2026-02-20 10:30:13 [INFO] Generating 731 date dimension records...
2026-02-20 10:30:13 [INFO] ✅ Inserted 731 date records
```

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
