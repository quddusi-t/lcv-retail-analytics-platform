"""
Churn prediction model: Pydantic schemas + ChurnPredictor inference class.

Loaded at API startup and called per request. Expects model artifacts produced
by train_churn.py: churn_model.pkl, churn_scaler.pkl, churn_metadata.json.
"""

import json
import pickle
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from pydantic import BaseModel

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

RiskTier = Literal["low", "medium", "high"]

_DEFAULT_MODEL_DIR = Path(__file__).parent / "models"


class ChurnFeatures(BaseModel):
    customer_id: int | None = None
    days_since_last_purchase: int
    purchases_l30d: int
    purchases_l60d: int
    purchases_l90d: int
    spend_l90d: float
    spend_prev_90d: float
    # NULL-able: 0 when no prior-period spend / single-purchase customer
    spend_trend_ratio: float | None = None
    return_rate: float | None = None
    avg_days_between_purchases: float | None = None
    purchase_count: int
    loyalty_member: bool


class ChurnPrediction(BaseModel):
    customer_id: int | None = None
    churn_score: float
    risk_tier: RiskTier
    is_predicted_churned: bool


def _risk_tier(score: float) -> RiskTier:
    if score >= 0.6:
        return "high"
    if score >= 0.3:
        return "medium"
    return "low"


class ChurnPredictor:
    """Loads model + scaler from disk and serves single / batch predictions."""

    def __init__(self, model_dir: str | Path = _DEFAULT_MODEL_DIR):
        model_dir = Path(model_dir)
        with open(model_dir / "churn_model.pkl", "rb") as f:
            self.model = pickle.load(f)
        with open(model_dir / "churn_scaler.pkl", "rb") as f:
            self.scaler = pickle.load(f)
        meta_path = model_dir / "churn_metadata.json"
        self.metadata: dict = (
            json.loads(meta_path.read_text()) if meta_path.exists() else {}
        )

    def _to_array(self, features: list["ChurnFeatures"]) -> np.ndarray:
        rows = [
            {
                "days_since_last_purchase": f.days_since_last_purchase,
                "purchases_l30d": f.purchases_l30d,
                "purchases_l60d": f.purchases_l60d,
                "purchases_l90d": f.purchases_l90d,
                "spend_l90d": f.spend_l90d,
                "spend_prev_90d": f.spend_prev_90d,
                "spend_trend_ratio": (
                    f.spend_trend_ratio if f.spend_trend_ratio is not None else 0.0
                ),
                "return_rate": f.return_rate if f.return_rate is not None else 0.0,
                "avg_days_between_purchases": (
                    f.avg_days_between_purchases
                    if f.avg_days_between_purchases is not None
                    else 0.0
                ),
                "purchase_count": f.purchase_count,
                "loyalty_member": int(f.loyalty_member),
            }
            for f in features
        ]
        X = pd.DataFrame(rows, columns=FEATURE_COLUMNS).values
        return self.scaler.transform(X)

    def predict(self, features: ChurnFeatures) -> ChurnPrediction:
        X = self._to_array([features])
        score = float(self.model.predict_proba(X)[0, 1])
        return ChurnPrediction(
            customer_id=features.customer_id,
            churn_score=round(score, 4),
            risk_tier=_risk_tier(score),
            is_predicted_churned=score >= 0.5,
        )

    def predict_batch(
        self, features_list: list[ChurnFeatures]
    ) -> list[ChurnPrediction]:
        X = self._to_array(features_list)
        scores = self.model.predict_proba(X)[:, 1]
        return [
            ChurnPrediction(
                customer_id=f.customer_id,
                churn_score=round(float(s), 4),
                risk_tier=_risk_tier(float(s)),
                is_predicted_churned=float(s) >= 0.5,
            )
            for f, s in zip(features_list, scores)
        ]
