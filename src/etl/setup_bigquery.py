"""
Set up BigQuery datasets for dbt transformations.

Creates required datasets:
- retail_analytics_staging: For dbt staging models
- retail_analytics_marts: For dbt mart models (analytics layer)

Usage:
    python src/etl/setup_bigquery.py
"""

import os
import sys
import logging
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_KEY_PATH = os.getenv("GCP_KEY_PATH")


def create_dataset(bq_client, dataset_id: str, location: str = "US"):
    """Create a BigQuery dataset if it doesn't exist."""
    try:
        dataset = bq_client.get_dataset(dataset_id)
        logger.info(f"[OK] Dataset {dataset_id} already exists")
        return dataset
    except Exception:
        pass

    dataset = bigquery.Dataset(f"{GCP_PROJECT_ID}.{dataset_id}")
    dataset.location = location
    dataset.description = f"Dataset: {dataset_id}"

    dataset = bq_client.create_dataset(dataset, timeout=30)
    logger.info(f"[OK] Created dataset {GCP_PROJECT_ID}.{dataset_id}")
    return dataset


def main():
    """Set up BigQuery datasets."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            GCP_KEY_PATH,
            scopes=["https://www.googleapis.com/auth/cloud-platform"],
        )
        bq_client = bigquery.Client(project=GCP_PROJECT_ID, credentials=credentials)

        logger.info("=" * 60)
        logger.info("Setting up BigQuery datasets")
        logger.info("=" * 60)

        # Create staging dataset (for dbt staging models)
        create_dataset(bq_client, "retail_analytics_staging")

        # Create marts dataset (for dbt mart models)
        create_dataset(bq_client, "retail_analytics_marts")

        logger.info("=" * 60)
        logger.info("[OK] BigQuery setup complete!")
        logger.info("=" * 60)
        logger.info("Datasets ready for dbt:")
        logger.info("  - retail_analytics_raw (raw data)")
        logger.info("  - retail_analytics_staging (staging models)")
        logger.info("  - retail_analytics_marts (analytics models)")
        sys.exit(0)

    except Exception as e:
        logger.error(f"[FATAL] Setup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
