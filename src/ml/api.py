"""
FastAPI ML service — churn prediction.

Usage:
    uvicorn src.ml.api:app --reload --host 0.0.0.0 --port 8000
    Docs: http://localhost:8000/docs

Environment Variables (Optional):
    CHURN_MODEL_DIR: Path to model artifact directory (default: src/ml/models)
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .churn_model import ChurnFeatures, ChurnPrediction, ChurnPredictor

logger = logging.getLogger(__name__)

_MODEL_DIR = Path(os.getenv("CHURN_MODEL_DIR", Path(__file__).parent / "models"))

_predictor: ChurnPredictor | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _predictor
    try:
        _predictor = ChurnPredictor(_MODEL_DIR)
        meta = _predictor.metadata
        logger.info(
            "[OK] Churn model loaded: %s  AUC=%.4f  trained=%s",
            meta.get("model_type"),
            meta.get("metrics", {}).get("auc_roc", 0),
            meta.get("trained_at", "unknown"),
        )
    except FileNotFoundError:
        logger.warning(
            "Churn model not found at %s — run: python src/ml/train_churn.py",
            _MODEL_DIR,
        )
    yield


app = FastAPI(
    title="LCV Retail Analytics ML API",
    description="Churn prediction for LCV retail customers",
    version="1.0.0",
    lifespan=lifespan,
)


class BatchChurnRequest(BaseModel):
    customers: list[ChurnFeatures]


class BatchChurnResponse(BaseModel):
    predictions: list[ChurnPrediction]
    count: int


def _require_model() -> ChurnPredictor:
    if _predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Churn model not loaded. Run: python src/ml/train_churn.py",
        )
    return _predictor


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "churn_model_loaded": _predictor is not None,
    }


@app.get("/api/models")
def list_models():
    predictor = _require_model()
    meta = predictor.metadata
    return {
        "models": [
            {
                "name": "churn",
                "type": meta.get("model_type"),
                "trained_at": meta.get("trained_at"),
                "auc_roc": meta.get("metrics", {}).get("auc_roc"),
                "churn_rate_train": meta.get("churn_rate"),
                "train_samples": meta.get("train_samples"),
                "features": meta.get("feature_columns"),
                "risk_tiers": meta.get("risk_tier_thresholds"),
                "feature_importances": meta.get("feature_importances"),
            }
        ]
    }


@app.post("/api/predict/churn", response_model=ChurnPrediction)
def predict_churn(features: ChurnFeatures):
    return _require_model().predict(features)


@app.post("/api/predict/churn/batch", response_model=BatchChurnResponse)
def predict_churn_batch(request: BatchChurnRequest):
    if not request.customers:
        raise HTTPException(status_code=400, detail="customers list cannot be empty")
    predictions = _require_model().predict_batch(request.customers)
    return BatchChurnResponse(predictions=predictions, count=len(predictions))
