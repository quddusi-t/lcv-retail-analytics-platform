# Snowflake Setup

Second warehouse target for the LCV Retail Analytics dbt project. Same 11 models and 52 tests as the BigQuery target — same business logic, different warehouse.

## Connection Details

| Setting | Value |
|---|---|
| Account | `sa61806.europe-west3.gcp` |
| User | `ktusuz` |
| Warehouse | `COMPUTE_WH` |
| Role | `SYSADMIN` |
| Database | `RETAIL_ANALYTICS` |
| Cloud | GCP, europe-west3 |

### Schema layout (mirrors BigQuery dataset structure)

| Snowflake schema | Contents | BigQuery equivalent |
|---|---|---|
| `RETAIL_ANALYTICS_RAW` | Raw source tables loaded by `postgres_to_snowflake.py` | `retail_analytics_raw` dataset |
| `RETAIL_ANALYTICS_STAGING` | dbt staging views (5 models) | `retail_analytics_staging` dataset |
| `RETAIL_ANALYTICS_MARTS` | dbt mart tables (6 models) | `retail_analytics_marts` dataset |

## Profile (`~/.dbt/profiles.yml`)

The `snowflake` target sits under the same `lcv_retail_analytics` profile as BigQuery:

```yaml
lcv_retail_analytics:
  target: dev
  outputs:
    dev:       # BigQuery (unchanged)
      ...
    snowflake:
      type: snowflake
      account: sa61806.europe-west3.gcp
      user: ktusuz
      password: "..."          # store as env var SNOWFLAKE_PASSWORD in production
      role: SYSADMIN
      database: RETAIL_ANALYTICS
      warehouse: COMPUTE_WH
      schema: retail_analytics
      threads: 4
      query_tag: dbt_lcv
```

`profiles.yml` lives in `~/.dbt/` and is never committed to git.

## Running dbt against Snowflake

```bash
cd src/etl/dbt_project

# Connection check
dbt debug --target snowflake

# Run all 11 models
dbt run --target snowflake

# Run all 52 tests
dbt test --target snowflake

# Single model
dbt run --target snowflake --select fct_customer_churn_features
```

## Loading raw data into Snowflake

The BigQuery pipeline uses `gcs_to_bigquery.py`. For Snowflake, use the dedicated loader:

```bash
SNOWFLAKE_PASSWORD=<password> python src/etl/postgres_to_snowflake.py
```

This reads directly from PostgreSQL and loads all 5 raw tables into `RETAIL_ANALYTICS_RAW` using `write_pandas`. On 1M rows it takes ~45 seconds.

Re-run whenever the PostgreSQL source data changes.

## Cross-adapter SQL changes

To support both BigQuery and Snowflake from the same model SQL, seven adapter-specific functions were replaced with macros in `macros/cross_db_utils.sql`. The macros dispatch on `target.type` at compile time — no runtime overhead.

| Original (BigQuery) | Macro | Snowflake output |
|---|---|---|
| `` `dataset`.table `` backtick refs | removed (unquoted works on both) | `SCHEMA.TABLE` |
| `CAST(x AS STRING)` | `{{ cast_to_string('x') }}` | `CAST(x AS VARCHAR)` |
| `DATE_DIFF(end, start, DAY)` | `{{ datediff_days('start', 'end') }}` | `DATEDIFF(DAY, start, end)` |
| `DATE_TRUNC(field, MONTH)` | `{{ date_trunc_month('field') }}` | `DATE_TRUNC('MONTH', field)` |
| `DATE 'YYYY-MM-DD'` | `{{ date_literal('YYYY-MM-DD') }}` | `'YYYY-MM-DD'::DATE` |
| `DATE_SUB(date, INTERVAL n DAY)` | `{{ dateadd_days(date, -n) }}` | `DATEADD(DAY, -n, date)` |
| `COUNTIF(cond)` | `{{ countif('cond') }}` | `COUNT_IF(cond)` |
| `SAFE_DIVIDE(a, b)` | `{{ safe_divide('a', 'b') }}` | `IFF(b = 0, NULL, a / b)` |
| `partition_by` / `cluster_by` config | conditional `if target.type == 'bigquery'` | config omitted for Snowflake |

Models with no BigQuery-specific syntax (`fct_store_performance`, `fct_product_performance`) were not modified.

## Benchmark results (Snowflake, May 2026)

- `dbt run --target snowflake`: 11/11 models in **5.81 seconds**
- `dbt test --target snowflake`: 52/52 tests in **4.98 seconds**
- Raw data load (1M rows via `postgres_to_snowflake.py`): **~45 seconds**

## Security note

The Snowflake password is stored in `~/.dbt/profiles.yml`, which is outside the git repository and never committed. For CI/CD use the `env_var('SNOWFLAKE_PASSWORD')` form in `profiles.yml` and inject the secret at runtime.
