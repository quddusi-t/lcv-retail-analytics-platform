# DBT Project: LCV Retail Analytics

Transform raw BigQuery data into clean, business-ready analytics tables.

## Project Structure

```
dbt_project/
├── dbt_project.yml          # Project configuration
├── models/
│   └── staging/         # Staging layer (raw → clean)
│       ├── stg_date_clean.sql          # Date dimension
│       ├── stg_store_clean.sql         # Store dimension
│       ├── stg_product_clean.sql       # Product dimension
│       ├── stg_customer_clean.sql      # Customer dimension
│       └── stg_sales_clean.sql         # Sales fact table
├── tests/               # dbt tests (data quality)
├── macros/              # dbt macros (reusable SQL)
└── analysis/            # Ad-hoc SQL analysis
```

## Models

### Staging Layer (stg_*_clean.sql)

Cleaning and validation of raw tables from `retail_analytics_raw` dataset:

1. **stg_date_clean** (731 rows)
   - Ensures date continuity
   - Adds fiscal year calculations
   - Validates no null dates

2. **stg_store_clean** (50 rows)
   - Standardizes text fields (UPPER)
   - Validates required fields
   - Preserves region hierarchy

3. **stg_product_clean** (498 rows)
   - Ensuresunit and cost prices > 0
   - Handles null brands
   - Validates category/subcategory

4. **stg_customer_clean** (10,000 rows)
   - Deduplicates by latest update
   - Ensures lifetime_value >= 0
   - Validates email addresses

5. **stg_sales_clean** (1,000,000 rows)
   - Validates quantity, prices > 0
   - Calculates derived fields (profit, discount amount)
   - Deduplicates using ROW_NUMBER
   - Materialized as TABLE for performance

## Configuration

### profiles.yml

Located at `~/.dbt/profiles.yml`. Connects dbt to BigQuery:

- **dev target:** Uses `retail_analytics_staging` dataset
- **prod target:** Uses `retail_analytics_marts` dataset

Both read from `retail_analytics_raw` raw tables.

### Environment Variables

```bash
export DBT_GCP_KEY_PATH=./lcv-gcp-key.json
```

Or update `~/.dbt/profiles.yml` with your key path.

## Usage

### Development (Staging Dataset)

```bash
# Run all models in dev environment
dbt run

# Run only staging models
dbt run --select stg_*

# Run with dry-run (SQL preview)
dbt run --dry-run

# Run and test
dbt run && dbt test
```

### Production (Marts Dataset)

```bash
# Switch to prod target
dbt run --target prod

# Full refresh (recreate tables)
dbt run --target prod --full-refresh
```

### Dbt CLI Commands

```bash
# Test data quality
dbt test

# Generate documentation
dbt docs generate

# Debug configuration
dbt debug

# Fresh cleanup
dbt clean
```

## Data Quality

Staging models include built-in validation:

- **Null checks** — Required fields cannot be null
- **Value range checks** — Prices/quantities must be positive
- **Deduplication** — Keep only latest version (ROW_NUMBER)
- **Type coercion** — Handle inconsistent data types

## Performance Notes

- **stg_date_clean:** VIEW (small dimension, fast access)
- **stg_store_clean:** VIEW (small dimension)
- **stg_product_clean:** VIEW (medium dimension)
- **stg_customer_clean:** VIEW (medium dimension)
- **stg_sales_clean:** TABLE (1M rows, materialized for query speed)

Each model is incrementally built on raw tables.

## Next Steps

1. ✅ Initialize dbt project
2. ✅ Create staging models
3. ⏳ Add dbt tests (assertions on data)
4. ⏳ Create mart models (analytics layer)
5. ⏳ Generate documentation

## References

- [dbt Docs](https://docs.getdbt.com/)
- [dbt Best Practices](https://docs.getdbt.com/guides/best-practices)
- [BigQuery Adapter](https://docs.getdbt.com/reference/warehouse-setups/bigquery-setup)
- [Jinja Templating](https://docs.getdbt.com/docs/build/jinja-macros)
