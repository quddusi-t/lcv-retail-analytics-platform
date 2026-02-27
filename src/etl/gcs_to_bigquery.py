"""
Load Parquet files from Google Cloud Storage to BigQuery.

Reads files from gs://bucket/YYYY-MM-DD/*.parquet and creates native BigQuery tables
in the retail_analytics_raw dataset.

Usage:
    python src/etl/gcs_to_bigquery.py

Environment Variables (Required):
    GCP_PROJECT_ID: Google Cloud Project ID
    GCP_KEY_PATH: Path to GCP service account key (.json file)
    GCS_BUCKET: GCS bucket name
    BIGQUERY_DATASET: Target BigQuery dataset
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

from google.cloud import bigquery, storage
from google.oauth2 import service_account
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler("bigquery_load.log", maxBytes=5_000_000, backupCount=3),
    ],
)
logger = logging.getLogger(__name__)

# Suppress noisy logs
logging.getLogger("google.auth").setLevel(logging.WARNING)
logging.getLogger("google.cloud").setLevel(logging.WARNING)

# Load environment
load_dotenv()

# Config
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_KEY_PATH = os.getenv("GCP_KEY_PATH")
GCS_BUCKET = os.getenv("GCS_BUCKET")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")

# Validate env vars
required_vars = ["GCP_PROJECT_ID", "GCP_KEY_PATH", "GCS_BUCKET", "BIGQUERY_DATASET"]
missing = [v for v in required_vars if not os.getenv(v)]
if missing:
    logger.error(f"Missing env vars: {missing}")
    sys.exit(1)


class GCSToBigQueryLoader:
    """Load Parquet files from GCS to BigQuery."""

    def __init__(self, project_id: str, key_path: str, bucket: str, dataset: str):
        self.project_id = project_id
        self.key_path = key_path
        self.bucket = bucket
        self.dataset = dataset
        self.credentials = None
        self.bq_client = None
        self.gcs_client = None

    def __enter__(self):
        """Initialize clients."""
        credentials = service_account.Credentials.from_service_account_file(
            self.key_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        self.credentials = credentials
        self.bq_client = bigquery.Client(
            project=self.project_id, credentials=credentials
        )
        self.gcs_client = storage.Client(
            project=self.project_id, credentials=credentials
        )
        logger.info(f"[OK] BigQuery client initialized (project: {self.project_id})")
        logger.info(f"[OK] GCS client initialized (bucket: {self.bucket})")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup."""
        # BigQuery client doesn't need explicit close
        return False

    def list_parquet_files(self, date: str) -> list:
        """List all Parquet files in GCS for a given date.

        Args:
            date: Format YYYY-MM-DD (e.g., "2026-02-26")

        Returns:
            List of file names without directory prefix (e.g., ["dim_date.parquet", ...])
        """
        bucket = self.gcs_client.bucket(self.bucket)
        blobs = list(bucket.list_blobs(prefix=f"{date}/"))
        parquet_files = [
            blob.name.split("/")[-1] for blob in blobs if blob.name.endswith(".parquet")
        ]
        logger.info(
            f"Found {len(parquet_files)} Parquet files in gs://{self.bucket}/{date}/"
        )
        return parquet_files

    def load_parquet_to_bigquery(self, gcs_uri: str, table_name: str) -> None:
        """Load a single Parquet file from GCS to BigQuery native table.

        Args:
            gcs_uri: Full GCS URI (e.g., "gs://bucket/2026-02-26/dim_store.parquet")
            table_name: Target BigQuery table (e.g., "dim_store")
        """
        table_id = f"{self.project_id}.{self.dataset}.{table_name}"

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            autodetect=True,  # Automatically infer schema from Parquet
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrite
        )

        logger.info(f"Loading {gcs_uri} → {table_id}")
        load_job = self.bq_client.load_table_from_uri(
            gcs_uri, table_id, job_config=job_config
        )
        load_job.result()  # Wait for completion

        destination_table = self.bq_client.get_table(table_id)
        logger.info(
            f"[OK] {table_name}: {destination_table.num_rows} rows loaded into {table_id}"
        )

    def load_all_tables(self, date: str) -> None:
        """Load all Parquet files from a date into BigQuery.

        Args:
            date: Format YYYY-MM-DD
        """
        files = self.list_parquet_files(date)

        if not files:
            logger.error(f"No Parquet files found for date {date}")
            sys.exit(1)

        logger.info("=" * 60)
        logger.info("STARTING GCS → BIGQUERY LOAD")
        logger.info("=" * 60)

        for file_name in files:
            table_name = file_name.replace(".parquet", "")
            gcs_uri = f"gs://{self.bucket}/{date}/{file_name}"
            try:
                self.load_parquet_to_bigquery(gcs_uri, table_name)
            except Exception as e:
                logger.error(f"[ERROR] Failed to load {file_name}: {e}")
                raise

        logger.info("=" * 60)
        logger.info("[OK] ALL TABLES LOADED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"Dataset: {self.project_id}.{self.dataset}")
        logger.info(f"Tables: {len(files)} tables")


def main():
    """Main entry point."""
    try:
        start_time = datetime.now()

        # Use today's date by default (change manually if needed)
        load_date = "2026-02-26"

        with GCSToBigQueryLoader(
            GCP_PROJECT_ID, GCP_KEY_PATH, GCS_BUCKET, BIGQUERY_DATASET
        ) as loader:
            loader.load_all_tables(load_date)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Pipeline completed in {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)"
        )
        sys.exit(0)

    except Exception as e:
        logger.error(f"[FATAL] Pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
