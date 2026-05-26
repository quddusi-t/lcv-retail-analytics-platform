"""
Load raw tables from PostgreSQL directly into Snowflake RETAIL_ANALYTICS_RAW schema.

Reads the same 5 tables used by the BigQuery pipeline and writes them to Snowflake
using write_pandas, creating tables automatically from the DataFrame schema.

Usage:
    python src/etl/postgres_to_snowflake.py

Environment Variables (Required):
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
    SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ROLE,
    SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE
"""

import logging
import os
import sys

import pandas as pd
import psycopg2
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

load_dotenv()

TABLES = ["fact_sales", "dim_customer", "dim_product", "dim_store", "dim_date"]
SNOWFLAKE_SCHEMA = "RETAIL_ANALYTICS_RAW"


def pg_conn():
    return psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def sf_conn():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT", "sa61806.europe-west3.gcp"),
        user=os.getenv("SNOWFLAKE_USER", "ktusuz"),
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.getenv("SNOWFLAKE_ROLE", "SYSADMIN"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
        database=os.getenv("SNOWFLAKE_DATABASE", "RETAIL_ANALYTICS"),
        schema=SNOWFLAKE_SCHEMA,
    )


def load_table(pg, sf, table: str) -> None:
    logger.info("Reading %s from PostgreSQL...", table)
    df = pd.read_sql(f"SELECT * FROM {table}", pg)
    logger.info("  %d rows read", len(df))

    df.columns = [c.upper() for c in df.columns]

    cur = sf.cursor()
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {SNOWFLAKE_SCHEMA}")
    cur.execute(f"DROP TABLE IF EXISTS {SNOWFLAKE_SCHEMA}.{table.upper()}")

    success, n_chunks, n_rows, _ = write_pandas(
        sf,
        df,
        table_name=table.upper(),
        schema=SNOWFLAKE_SCHEMA,
        auto_create_table=True,
        overwrite=True,
    )
    if not success:
        raise RuntimeError(f"write_pandas failed for {table}")
    logger.info("[OK] %s: %d rows loaded to Snowflake", table, n_rows)


def main() -> None:
    missing = [
        v
        for v in ["POSTGRES_HOST", "POSTGRES_PASSWORD", "SNOWFLAKE_PASSWORD"]
        if not os.getenv(v)
    ]
    if missing:
        logger.error("Missing env vars: %s", missing)
        sys.exit(1)

    with pg_conn() as pg, sf_conn() as sf:
        for table in TABLES:
            load_table(pg, sf, table)

    logger.info(
        "[OK] All %d tables loaded to %s.%s",
        len(TABLES),
        "RETAIL_ANALYTICS",
        SNOWFLAKE_SCHEMA,
    )


if __name__ == "__main__":
    main()
