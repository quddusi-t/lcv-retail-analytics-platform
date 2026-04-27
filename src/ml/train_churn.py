"""
Train churn prediction models from fct_customer_churn_features in BigQuery.

Trains Logistic Regression and Random Forest on CLEAN (non-leaky) features,
compares AUC-ROC against a dummy majority-class baseline, saves the better
model to src/ml/models/ along with its scaler and metadata JSON.

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

import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
from matplotlib import pyplot as plt
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

matplotlib.use("Agg")  # headless — no display required

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

load_dotenv()

# ---------------------------------------------------------------------------
# Feature leakage audit
#
# is_churned is defined in fct_customer_churn_features.sql as:
#   days_since_last_purchase > GREATEST(90, avg_days_between_purchases * 1.5)
#
# LEAKY — directly encode the churn criterion; excluded from training:
#   days_since_last_purchase  IS the LHS of the churn formula
#   purchases_l30d/l60d/l90d  all 0 for every churned customer (seeder caps
#                             their sale_date >90 days before reference date)
#   spend_l90d                0 for all churned customers by seeder construction
#   spend_trend_ratio         spend_l90d / spend_prev_90d → 0 when spend_l90d=0
#
# CLEAN — genuine pre-churn behavioral signals; used for training:
#   spend_prev_90d             activity 91–180 days before reference; predates churn window
#   return_rate                lifetime return fraction; seeded at 10% vs 4% per cohort
#   avg_days_between_purchases historical purchase cadence; not recency-sensitive
#   purchase_count             lifetime non-return count; not recency-sensitive
#   loyalty_member             static demographic attribute
# ---------------------------------------------------------------------------

LEAKY_FEATURES = [
    "days_since_last_purchase",
    "purchases_l30d",
    "purchases_l60d",
    "purchases_l90d",
    "spend_l90d",
    "spend_trend_ratio",
]

CLEAN_FEATURES = [
    "spend_prev_90d",
    "return_rate",
    "avg_days_between_purchases",
    "purchase_count",
    "loyalty_member",
]

# ---------------------------------------------------------------------------
# Future feature improvements
#
# FEATURE CANDIDATES (require dbt mart changes to add the columns):
#
#   return_rate_prev_90d       Windowed return rate for the 91–180d window only.
#                              Note: return_rate_l90d (last 90d) would be leaky —
#                              churned customers have no purchases in that window,
#                              so their return count is 0 by construction, same
#                              failure mode as spend_l90d. Use the prev window to
#                              mirror spend_prev_90d's safe boundary.
#
#   purchase_count_prev_90d    Purchase count for the 91–180d window (not l180d).
#                              purchase_count_l180d is partially leaky: the 0–90d
#                              half of the window is 0 for all churned customers.
#                              The prev-90d slice is clean for the same reason
#                              spend_prev_90d is.
#
#   log1p(avg_days_between_purchases)
#                              avg_days_between_purchases is right-skewed (many
#                              customers cluster <30d, a long tail to 300d+).
#                              log1p compression improves Logistic Regression's
#                              linear boundary; less critical for Random Forest
#                              since trees split on thresholds. Apply in
#                              preprocess() before scaling.
#
# DATA QUALITY NOTE (synthetic data):
#
#   loyalty_member             Currently seeded as a static binary with no
#                              engineered correlation to churn behavior. In
#                              production, loyalty members should have a
#                              measurably lower churn rate. Until the seeder
#                              encodes that relationship, this feature contributes
#                              near-zero signal and will show low RF importance.
# ---------------------------------------------------------------------------

TARGET_COLUMN = "is_churned"

# Reference date: 2025-10-31. Temporal train/test cutoff: 2025-07-31 = 92 days prior.
# Customers whose last purchase was BEFORE 2025-07-31 → train cohort (historically silent).
# Customers whose last purchase was ON/AFTER 2025-07-31 → test cohort (recently active).
TEMPORAL_CUTOFF_DAYS = 92


def load_training_data(project_id: str, key_path: str, dataset: str) -> pd.DataFrame:
    credentials = service_account.Credentials.from_service_account_file(
        key_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    client = bigquery.Client(project=project_id, credentials=credentials)

    # Fetch leaky features too — needed for temporal split diagnostics, not training
    all_cols = ", ".join(LEAKY_FEATURES + CLEAN_FEATURES + [TARGET_COLUMN])
    query = (
        f"SELECT {all_cols} FROM `{project_id}.{dataset}.fct_customer_churn_features`"
    )

    logger.info(
        "Loading from BigQuery: %s.%s.fct_customer_churn_features", project_id, dataset
    )
    df = client.query(query).to_dataframe()
    logger.info("[OK] %d rows loaded", len(df))
    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # NULL → 0 for three fields that are undefined for single-purchase customers
    # or when prior-period spend is zero.
    df["spend_trend_ratio"] = df["spend_trend_ratio"].fillna(0.0)
    df["avg_days_between_purchases"] = df["avg_days_between_purchases"].fillna(0.0)
    df["return_rate"] = df["return_rate"].fillna(0.0)
    df["loyalty_member"] = df["loyalty_member"].astype(int)
    return df


def temporal_split_audit(df: pd.DataFrame) -> None:
    """Log churn rates in a temporal train/test split to surface leakage."""
    train_mask = df["days_since_last_purchase"] > TEMPORAL_CUTOFF_DAYS
    test_mask = ~train_mask

    train_churn = df.loc[train_mask, TARGET_COLUMN].mean()
    test_churn = df.loc[test_mask, TARGET_COLUMN].mean()

    logger.info("--- Temporal split audit (cutoff: %d days) ---", TEMPORAL_CUTOFF_DAYS)
    logger.info(
        "  Train cohort (last purchase before 2025-07-31): %d rows, %.1f%% churned",
        train_mask.sum(),
        train_churn * 100,
    )
    logger.info(
        "  Test  cohort (last purchase after  2025-07-31): %d rows, %.1f%% churned",
        test_mask.sum(),
        test_churn * 100,
    )

    if train_churn > 0.85 and test_churn < 0.15:
        logger.warning(
            "LEAKAGE CONFIRMED: temporal split is ~%.0f%% / ~%.0f%% churn."
            " Recency features perfectly separate classes — they ARE the churn definition.",
            train_churn * 100,
            test_churn * 100,
        )
        logger.warning(
            "Falling back to stratified random split on CLEAN features for honest evaluation."
        )


def evaluate_model(name: str, model, X_test: np.ndarray, y_test: np.ndarray) -> dict:
    proba = model.predict_proba(X_test)[:, 1]
    pred = model.predict(X_test)
    auc = roc_auc_score(y_test, proba)
    report = classification_report(
        y_test, pred, target_names=["active", "churned"], output_dict=True
    )
    logger.info("%s  AUC-ROC: %.4f", name.ljust(28), auc)
    logger.info(
        "\n%s", classification_report(y_test, pred, target_names=["active", "churned"])
    )
    return {"auc": auc, "report": report}


def plot_confusion_matrix(
    model_name: str,
    auc: float,
    y_true: np.ndarray,
    y_pred: np.ndarray,
    output_path: Path,
) -> None:
    cm = confusion_matrix(y_true, y_pred)
    total = cm.sum()
    labels = [[f"{v}\n({v / total:.1%})" for v in row] for row in cm]

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=labels,
        fmt="",
        cmap="Blues",
        xticklabels=["Active", "Churned"],
        yticklabels=["Active", "Churned"],
        linewidths=0.5,
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"{model_name}  |  AUC-ROC = {auc:.4f}")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info("[OK] Saved confusion matrix → %s", output_path)


def train(project_id: str, key_path: str, dataset: str, model_dir: Path) -> None:
    df = load_training_data(project_id, key_path, dataset)
    df = preprocess(df)

    churn_rate = df[TARGET_COLUMN].mean()
    logger.info(
        "Overall churn rate: %.1f%% (%d churned / %d total)",
        churn_rate * 100,
        int(df[TARGET_COLUMN].sum()),
        len(df),
    )

    # --- Temporal split audit: confirms leakage before we proceed ---
    temporal_split_audit(df)

    # --- Stratified random split on clean features ---
    X = df[CLEAN_FEATURES].values
    y = df[TARGET_COLUMN].astype(int).values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    logger.info("=" * 55)
    logger.info("TRAINING ON CLEAN FEATURES ONLY: %s", CLEAN_FEATURES)
    logger.info("EXCLUDED (leaky): %s", LEAKY_FEATURES)
    logger.info("=" * 55)

    results = {}

    # --- Dummy baseline ---
    dummy = DummyClassifier(strategy="stratified", random_state=42)
    dummy.fit(X_train_scaled, y_train)
    dummy_metrics = evaluate_model(
        "DummyClassifier (baseline)", dummy, X_test_scaled, y_test
    )
    results["dummy_baseline"] = {"model": dummy, **dummy_metrics}

    # --- Logistic Regression ---
    lr = LogisticRegression(
        C=1.0, max_iter=500, class_weight="balanced", random_state=42
    )
    lr.fit(X_train_scaled, y_train)
    lr_metrics = evaluate_model("Logistic Regression", lr, X_test_scaled, y_test)
    results["logistic_regression"] = {"model": lr, **lr_metrics}

    # --- Random Forest ---
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=8,
        min_samples_leaf=10,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    rf.fit(X_train_scaled, y_train)
    rf_metrics = evaluate_model("Random Forest", rf, X_test_scaled, y_test)

    importances = dict(zip(CLEAN_FEATURES, rf.feature_importances_))
    logger.info("Feature importances (RF):")
    for feat, imp in sorted(importances.items(), key=lambda x: -x[1]):
        logger.info("  %-35s %.4f", feat, imp)

    results["random_forest"] = {
        "model": rf,
        "feature_importances": importances,
        **rf_metrics,
    }

    # --- Summary ---
    logger.info("=" * 55)
    logger.info("MODEL COMPARISON (AUC-ROC, stratified 80/20 split)")
    logger.info("=" * 55)
    for name, r in results.items():
        logger.info("  %-30s %.4f", name, r["auc"])

    # Exclude dummy from "best" selection — only real models compete
    real_models = {k: v for k, v in results.items() if k != "dummy_baseline"}
    best_name = max(real_models, key=lambda k: real_models[k]["auc"])
    best = results[best_name]
    dummy_auc = results["dummy_baseline"]["auc"]

    logger.info(
        "Best model: %s  (AUC=%.4f, baseline=%.4f, lift=+%.4f)",
        best_name,
        best["auc"],
        dummy_auc,
        best["auc"] - dummy_auc,
    )

    # --- Persist artifacts ---
    model_dir.mkdir(parents=True, exist_ok=True)

    plot_confusion_matrix(
        model_name=best_name.replace("_", " ").title(),
        auc=best["auc"],
        y_true=y_test,
        y_pred=best["model"].predict(X_test_scaled),
        output_path=model_dir / "confusion_matrix.png",
    )

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
        "feature_columns": CLEAN_FEATURES,
        "excluded_leaky_features": LEAKY_FEATURES,
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
        "baseline_auc": float(dummy_auc),
        "auc_lift_over_baseline": float(best["auc"] - dummy_auc),
    }
    if best_name == "random_forest":
        metadata["feature_importances"] = {k: float(v) for k, v in importances.items()}

    metadata_path.write_text(json.dumps(metadata, indent=2))

    logger.info("[OK] Saved model    → %s", model_path)
    logger.info("[OK] Saved scaler   → %s", scaler_path)
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
