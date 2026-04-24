"""
PostgreSQL to Google Cloud Storage ETL Pipeline

Extracts data from PostgreSQL (fact and dimension tables), converts to Parquet format,
and uploads to Google Cloud Storage for downstream BigQuery ingestion.

Usage:
    # Extract and upload to GCS
    python src/etl/postgres_to_gcs.py

    # Local testing (write Parquet files locally only, no GCS upload)
    python src/etl/postgres_to_gcs.py --local

Environment Variables (Required):
    POSTGRES_HOST: PostgreSQL host
    POSTGRES_PORT: PostgreSQL port
    POSTGRES_DB: PostgreSQL database name
    POSTGRES_USER: PostgreSQL username
    POSTGRES_PASSWORD: PostgreSQL password
    GCP_PROJECT_ID: Google Cloud Project ID
    GCP_KEY_PATH: Path to GCP service account key (.json file)
    GCS_BUCKET: Google Cloud Storage bucket name
    BIGQUERY_DATASET: BigQuery dataset name (for documentation)

Output:
    - Local Parquet files (temporary staging)
    - Uploaded to GCS: gs://bucket-name/yyyy-MM-dd/table-name.parquet
    - Execution logs: etl_extract.log (with rotation)
    - Exit codes: 0 (success), 1 (fatal error)
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account
from sqlalchemy import create_engine, text

# Configure logging with rotation
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
        RotatingFileHandler(
            "etl_extract.log", maxBytes=5_000_000, backupCount=3
        ),  # File output with rotation
    ],
)
logger = logging.getLogger(__name__)

# Suppress noisy library logs
logging.getLogger("google.auth").setLevel(logging.WARNING)
logging.getLogger("google.cloud.storage").setLevel(logging.WARNING)

# Load environment variables
load_dotenv()

# Validate required environment variables: fail fast
required_vars = [
    "POSTGRES_HOST",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "GCP_PROJECT_ID",
    "GCP_KEY_PATH",
    "GCS_BUCKET",
]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    logger.error("Missing required environment variables: %s", ", ".join(missing_vars))
    sys.exit(1)

# Extract configuration for safe logging
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_DB = os.getenv("POSTGRES_DB")

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_KEY_PATH = os.getenv("GCP_KEY_PATH")
GCS_BUCKET = os.getenv("GCS_BUCKET")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "retail_analytics_raw")

# Database configuration
DB_CONFIG = {
    "host": POSTGRES_HOST,
    "port": POSTGRES_PORT,
    "user": POSTGRES_USER,
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": POSTGRES_DB,
}

# Tables to extract (order matters: dimensions first, then fact)
TABLES_TO_EXTRACT = [
    "dim_date",
    "dim_store",
    "dim_product",
    "dim_customer",
    "fact_sales",
]

# Temporary directory for local Parquet staging
PARQUET_STAGING_DIR = Path("./parquet_staging")


class ETLPipelineError(Exception):
    """Custom exception for ETL pipeline failures."""

    pass


class PostgresToGCSExtractor:
    """Extract data from PostgreSQL and load to Google Cloud Storage.

    Supports context manager for automatic resource cleanup:
        with PostgresToGCSExtractor(DB_CONFIG, GCS_BUCKET) as extractor:
            extractor.extract_all()
    """

    def __init__(self, db_config: dict, gcs_bucket: str, local_only: bool = False):
        """Initialize extractor with database and GCS configuration.

        Args:
            db_config: PostgreSQL connection dict
            gcs_bucket: GCS bucket name
            local_only: If True, only write Parquet files locally (no GCS upload)
        """
        self.db_config = db_config
        self.gcs_bucket = gcs_bucket
        self.local_only = local_only
        self.conn = None
        self.cursor = None
        self.engine = None
        self.gcs_client = None
        self.run_date = datetime.now().strftime("%Y-%m-%d")

    def __enter__(self):
        """Context manager entry: establish connections."""
        self.connect_postgres()
        if not self.local_only:
            self.connect_gcs()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit: ensure connections always close cleanly."""
        self.disconnect()
        return False

    def connect_postgres(self) -> None:
        """Connect to PostgreSQL database."""
        try:
            logger.info(
                "Connecting to PostgreSQL at %s:%s (database: %s, user: %s)",
                self.db_config["host"],
                self.db_config["port"],
                self.db_config["database"],
                self.db_config["user"],
            )
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            url = (
                f"postgresql+psycopg2://{self.db_config['user']}:"
                f"{self.db_config['password']}@{self.db_config['host']}:"
                f"{self.db_config['port']}/{self.db_config['database']}"
            )
            self.engine = create_engine(url)
            logger.info("[OK] PostgreSQL connection established")
        except psycopg2.OperationalError as e:
            logger.error("Failed to connect to PostgreSQL: %s", str(e))
            raise ETLPipelineError(f"PostgreSQL connection failed: {e}")

    def connect_gcs(self) -> None:
        """Authenticate with Google Cloud Storage using service account key."""
        try:
            logger.info("Authenticating with Google Cloud Storage...")
            # Load credentials from service account key
            credentials = service_account.Credentials.from_service_account_file(
                GCP_KEY_PATH
            )
            self.gcs_client = storage.Client(
                project=GCP_PROJECT_ID, credentials=credentials
            )
            # Verify bucket exists
            bucket = self.gcs_client.bucket(self.gcs_bucket)
            bucket.reload()
            logger.info(
                "[OK] GCS authentication successful (bucket: %s)", self.gcs_bucket
            )
        except FileNotFoundError as e:
            logger.error("GCP key file not found at %s: %s", GCP_KEY_PATH, str(e))
            raise ETLPipelineError(f"GCP key file not found: {e}")
        except Exception as e:
            logger.error("GCS authentication failed: %s", str(e))
            raise ETLPipelineError(f"GCS authentication failed: {e}")

    def disconnect(self) -> None:
        """Close database and GCS connections."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        if self.engine:
            self.engine.dispose()
        logger.info("Disconnected from PostgreSQL")

    def extract_table(self, table_name: str) -> pd.DataFrame:
        """Extract a table from PostgreSQL as DataFrame.

        Args:
            table_name: Name of table to extract

        Returns:
            pandas DataFrame containing table data

        Raises:
            ETLPipelineError: If query fails
        """
        try:
            logger.info("Extracting table: %s", table_name)
            with self.engine.connect() as conn:
                df = pd.read_sql(text(f"SELECT * FROM {table_name}"), conn)
            record_count = len(df)
            logger.info("[OK] Extracted %d records from %s", record_count, table_name)
            return df
        except Exception as e:
            logger.error("Failed to extract %s: %s", table_name, str(e))
            raise ETLPipelineError(f"Failed to extract {table_name}: {e}")

    def save_parquet_locally(self, df: pd.DataFrame, table_name: str) -> Path:
        """Save DataFrame as Parquet file locally.

        Args:
            df: pandas DataFrame to save
            table_name: Table name (used for filename)

        Returns:
            Path to saved Parquet file

        Raises:
            ETLPipelineError: If write fails
        """
        try:
            # Create staging directory if it doesn't exist
            PARQUET_STAGING_DIR.mkdir(parents=True, exist_ok=True)

            parquet_path = PARQUET_STAGING_DIR / f"{table_name}.parquet"
            df.to_parquet(parquet_path, engine="pyarrow", compression="snappy")
            file_size_mb = parquet_path.stat().st_size / (1024 * 1024)
            logger.info("[OK] Saved %s as Parquet (%.2f MB)", table_name, file_size_mb)
            return parquet_path
        except Exception as e:
            logger.error("Failed to save Parquet for %s: %s", table_name, str(e))
            raise ETLPipelineError(f"Failed to save Parquet for {table_name}: {e}")

    def upload_to_gcs(self, local_path: Path, gcs_path: str) -> None:
        """Upload local Parquet file to Google Cloud Storage.

        Args:
            local_path: Path to local Parquet file
            gcs_path: Destination path in GCS (e.g., "2026-02-25/fact_sales.parquet")

        Raises:
            ETLPipelineError: If upload fails
        """
        try:
            bucket = self.gcs_client.bucket(self.gcs_bucket)
            blob = bucket.blob(gcs_path)
            blob.upload_from_filename(str(local_path))
            file_size_mb = local_path.stat().st_size / (1024 * 1024)
            logger.info(
                "[OK] Uploaded to gs://%s/%s (%.2f MB)",
                self.gcs_bucket,
                gcs_path,
                file_size_mb,
            )
        except Exception as e:
            logger.error("Failed to upload to GCS: %s", str(e))
            raise ETLPipelineError(f"GCS upload failed: {e}")

    def extract_all(self) -> None:
        """Run the complete ETL extraction pipeline.

        Extracts all tables from PostgreSQL, converts to Parquet, and uploads to GCS.
        """
        try:
            logger.info("=" * 60)
            logger.info("STARTING ETL EXTRACTION PIPELINE")
            logger.info("=" * 60)

            extracted_count = 0
            uploaded_count = 0
            total_records = 0

            for table_name in TABLES_TO_EXTRACT:
                # Extract from Postgres
                df = self.extract_table(table_name)
                total_records += len(df)

                # Save to local Parquet
                parquet_path = self.save_parquet_locally(df, table_name)
                extracted_count += 1

                # Upload to GCS (if not local-only mode)
                if not self.local_only:
                    gcs_path = f"{self.run_date}/{table_name}.parquet"
                    self.upload_to_gcs(parquet_path, gcs_path)
                    uploaded_count += 1
                else:
                    logger.info("[LOCAL MODE] Skipped GCS upload for %s", table_name)

            logger.info("=" * 60)
            logger.info("[OK] ETL EXTRACTION COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(
                "Summary: Extracted %d tables, %d total records",
                extracted_count,
                total_records,
            )
            if not self.local_only:
                logger.info("Uploaded %d tables to GCS", uploaded_count)
            else:
                logger.info("Local mode: Files saved to %s", PARQUET_STAGING_DIR)

        except ETLPipelineError as e:
            logger.error("=" * 60)
            logger.error("[ERROR] ETL extraction failed: %s", str(e))
            logger.error("=" * 60)
            raise
        except Exception as e:
            logger.error("=" * 60)
            logger.error("[FATAL] Unexpected error: %s", str(e), exc_info=True)
            logger.error("=" * 60)
            raise


def main() -> None:
    """Entry point for ETL extraction pipeline with error handling and exit codes.

    Exit codes:
        0 = success
        1 = fatal error (CI/CD detection)
    """
    try:
        start_time = datetime.now()
        logger.info(" " * 60)
        logger.info("LCV RETAIL ANALYTICS - ETL EXTRACTION PIPELINE")
        logger.info(" " * 60)

        # Check for --local flag for local-only testing
        local_only = "--local" in sys.argv

        if local_only:
            logger.info("Running in LOCAL-ONLY mode (no GCS upload)")
        else:
            logger.info("Running in FULL mode (PostgreSQL → Parquet → GCS)")

        # Log configuration
        logger.info(
            "PostgreSQL: %s:%s (db=%s, user=%s)",
            POSTGRES_HOST,
            POSTGRES_PORT,
            POSTGRES_DB,
            POSTGRES_USER,
        )
        if not local_only:
            logger.info("GCS Bucket: gs://%s", GCS_BUCKET)
            logger.info("BigQuery Dataset: %s", BIGQUERY_DATASET)

        # Run extraction pipeline
        with PostgresToGCSExtractor(
            DB_CONFIG, GCS_BUCKET, local_only=local_only
        ) as extractor:
            extractor.extract_all()

        # Calculate and log elapsed time
        elapsed_seconds = (datetime.now() - start_time).total_seconds()
        elapsed_minutes = elapsed_seconds / 60
        logger.info(
            "Pipeline completed successfully in %.2f seconds (%.2f minutes)",
            elapsed_seconds,
            elapsed_minutes,
        )
        sys.exit(0)

    except Exception as e:
        # Top-level error handler: logs fatal errors cleanly for CI/CD detection
        logger.error("=" * 60)
        logger.error("[FATAL] Pipeline failed: %s", str(e), exc_info=True)
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
