"""
Train churn prediction models from fct_customer_churn_features in BigQuery.

Trains Logistic Regression and Random Forest, compares AUC-ROC, saves the
better model to src/ml/models/ along with its scaler and metadata JSON.

Usage:
    python src/ml/train_churn.py
    python src/ml/train_churn.py --model-dir src/ml/models
    python src/ml/train_churn.py --dataset retail_analytics_marts

Environment Variables (Required):
    GCP_PROJECT_ID: Google Cloud Project ID
    GCP_KEY_PATH: Path to GCP service account key (.json file)

Environment Variables (Optional):
    BIGQUERY_MART_DATASET: BigQuery dataset containing mart tables
                           (default: marts)
"""

import argparse
import json
import logging
import os
import pickle
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

load_dotenv()

FEATURE_COLUMNS = [
    "days_since_last_purchase",
    "purchases_l30d",
    "purchases_l60d",
    "purchases_l90d",
    "spend_l90d",
    "spend_prev_90d",
    "spend_trend_ratio",
    "return_rate",
    "avg_days_between_purchases",
    "purchase_count",
    "loyalty_member",
]
TARGET_COLUMN = "is_churned"


def load_training_data(project_id: str, key_path: str, dataset: str) -> pd.DataFrame:
    credentials = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = bigquery.Client(project=project_id, credentials=credentials)

    cols = ", ".join(FEATURE_COLUMNS + [TARGET_COLUMN])
    query = f"SELECT {cols} FROM `{project_id}.{dataset}.fct_customer_churn_features`"

    logger.info(
        "Loading from BigQuery: %s.%s.fct_customer_churn_features", project_id, dataset
    )
    df = client.query(query).to_dataframe()
    logger.info("[OK] %d rows loaded", len(df))
    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # NULL means no prior-period spend or single-purchase cadence — treat as 0
    df["spend_trend_ratio"] = df["spend_trend_ratio"].fillna(0.0)
    df["avg_days_between_purchases"] = df["avg_days_between_purchases"].fillna(0.0)
    df["return_rate"] = df["return_rate"].fillna(0.0)
    df["loyalty_member"] = df["loyalty_member"].astype(int)
    return df


def train(project_id: str, key_path: str, dataset: str, model_dir: Path) -> None:
    df = load_training_data(project_id, key_path, dataset)
    df = preprocess(df)

    churn_rate = df[TARGET_COLUMN].mean()
    logger.info(
        "Churn rate: %.1f%% (%d churned / %d total)",
        churn_rate * 100,
        df[TARGET_COLUMN].sum(),
        len(df),
    )

    X = df[FEATURE_COLUMNS].values
    y = df[TARGET_COLUMN].astype(int).values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    results = {}

    # --- Logistic Regression ---
    logger.info("Training Logistic Regression...")
    lr = LogisticRegression(
        C=1.0, max_iter=500, class_weight="balanced", random_state=42
    )
    lr.fit(X_train_scaled, y_train)

    lr_proba = lr.predict_proba(X_test_scaled)[:, 1]
    lr_pred = lr.predict(X_test_scaled)
    lr_auc = roc_auc_score(y_test, lr_proba)
    lr_report = classification_report(
        y_test, lr_pred, target_names=["active", "churned"], output_dict=True
    )

    logger.info("Logistic Regression  AUC-ROC: %.4f", lr_auc)
    logger.info(
        "\n%s",
        classification_report(y_test, lr_pred, target_names=["active", "churned"]),
    )

    results["logistic_regression"] = {"model": lr, "auc": lr_auc, "report": lr_report}

    # --- Random Forest ---
    logger.info("Training Random Forest (200 trees)...")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train_scaled, y_train)

    rf_proba = rf.predict_proba(X_test_scaled)[:, 1]
    rf_pred = rf.predict(X_test_scaled)
    rf_auc = roc_auc_score(y_test, rf_proba)
    rf_report = classification_report(
        y_test, rf_pred, target_names=["active", "churned"], output_dict=True
    )

    logger.info("Random Forest        AUC-ROC: %.4f", rf_auc)
    logger.info(
        "\n%s",
        classification_report(y_test, rf_pred, target_names=["active", "churned"]),
    )

    importances = dict(zip(FEATURE_COLUMNS, rf.feature_importances_))
    logger.info("Feature importances (RF):")
    for feat, imp in sorted(importances.items(), key=lambda x: -x[1]):
        logger.info("  %-35s %.4f", feat, imp)

    results["random_forest"] = {
        "model": rf,
        "auc": rf_auc,
        "report": rf_report,
        "feature_importances": importances,
    }

    # --- Select best by AUC ---
    best_name = max(results, key=lambda k: results[k]["auc"])
    best = results[best_name]
    logger.info("=" * 50)
    logger.info("Best model: %s  (AUC=%.4f)", best_name, best["auc"])
    logger.info("=" * 50)

    # --- Persist artifacts ---
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "churn_model.pkl"
    scaler_path = model_dir / "churn_scaler.pkl"
    metadata_path = model_dir / "churn_metadata.json"

    with open(model_path, "wb") as f:
        pickle.dump(best["model"], f)
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)

    metadata: dict = {
        "model_type": best_name,
        "trained_at": datetime.now().isoformat(),
        "bigquery_source": f"{project_id}.{dataset}.fct_customer_churn_features",
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "train_samples": int(len(y_train)),
        "test_samples": int(len(y_test)),
        "churn_rate": float(churn_rate),
        "risk_tier_thresholds": {
            "low": "< 0.30",
            "medium": "0.30 – 0.60",
            "high": ">= 0.60",
        },
        "metrics": {
            "auc_roc": float(best["auc"]),
            "classification_report": best["report"],
        },
        "all_models": {
            name: {"auc_roc": float(r["auc"])} for name, r in results.items()
        },
    }
    if best_name == "random_forest":
        metadata["feature_importances"] = {k: float(v) for k, v in importances.items()}

    metadata_path.write_text(json.dumps(metadata, indent=2))

    logger.info("[OK] Saved model   → %s", model_path)
    logger.info("[OK] Saved scaler  → %s", scaler_path)
    logger.info("[OK] Saved metadata → %s", metadata_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train churn prediction model from BigQuery mart"
    )
    parser.add_argument(
        "--model-dir",
        default="src/ml/models",
        help="Output directory for model artifacts",
    )
    parser.add_argument(
        "--dataset",
        default=os.getenv("BIGQUERY_MART_DATASET", "marts"),
        help="BigQuery dataset containing fct_customer_churn_features (default: marts)",
    )
    args = parser.parse_args()

    required = ["GCP_PROJECT_ID", "GCP_KEY_PATH"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        logger.error("Missing required env vars: %s", missing)
        sys.exit(1)

    try:
        train(
            project_id=os.getenv("GCP_PROJECT_ID"),
            key_path=os.getenv("GCP_KEY_PATH"),
            dataset=args.dataset,
            model_dir=Path(args.model_dir),
        )
        sys.exit(0)
    except Exception as e:
        logger.error("[FATAL] Training failed: %s", str(e), exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
