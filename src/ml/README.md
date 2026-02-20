# ML Module

This module contains machine learning models for churn prediction and demand forecasting, plus a FastAPI service for real-time predictions.

---

## 📦 Contents

- `api.py` – FastAPI application for model serving
- `churn_model.py` – Customer churn prediction model
- `demand_model.py` – Product demand forecasting model
- Model training scripts and evaluation utilities

---

## 🚀 Quick Start

### Prerequisites

- PostgreSQL or BigQuery with [ETL pipeline](../etl/README.md) run
- Python ML dependencies: `scikit-learn`, `pandas`, `numpy`, `fastapi`, `uvicorn`
- Trained models (download or train locally)

### Start ML API Service

```bash
uvicorn src.ml.api:app --reload --host 0.0.0.0 --port 8000
```

Service runs at `http://localhost:8000`

### API Documentation

Open `http://localhost:8000/docs` for interactive Swagger UI.

---

## 📊 Models

### 1. Churn Prediction

**Purpose**: Identify customers at risk of churning (not returning).

**Input Features**:
- Recency: Days since last purchase
- Frequency: Number of purchases in past 6 months
- Monetary: Average transaction value
- Loyalty status: Member vs non-member
- Days since join

**Output**:
- Churn probability (0–1)
- Risk category: Low / Medium / High

**Use Cases**:
- Identify at-risk customers for retention campaigns
- Predict next active/inactive period
- Prioritize customer support outreach

**API Endpoint**:

```bash
curl -X POST "http://localhost:8000/api/predict/churn" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 123,
    "recency_days": 30,
    "frequency": 5,
    "avg_monetary": 125.50,
    "loyalty_member": true,
    "days_since_join": 365
  }'
```

Response:

```json
{
  "customer_id": 123,
  "churn_probability": 0.23,
  "risk_category": "LOW",
  "next_action": "Monitor"
}
```

### 2. Demand Forecasting

**Purpose**: Predict product demand for inventory and sales planning.

**Input Features**:
- Product category
- Recent sales volume (7d, 14d, 30d)
- Seasonality indicator
- Day of week
- Is holiday

**Output**:
- Forecasted units for next 7 days, 30 days
- Confidence interval
- Seasonal trend

**Use Cases**:
- Optimize inventory levels
- Plan promotional campaigns
- Allocate stock to stores
- Identify slow-moving products

**API Endpoint**:

```bash
curl -X POST "http://localhost:8000/api/predict/demand" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 456,
    "category": "Textiles",
    "recent_sales_7d": 120,
    "recent_sales_30d": 450,
    "seasonality": "summer",
    "day_of_week": "Saturday"
  }'
```

Response:

```json
{
  "product_id": 456,
  "forecast_7d": 145,
  "forecast_30d": 550,
  "confidence_lower": 130,
  "confidence_upper": 160,
  "trend": "increasing"
}
```

---

## 🔄 Model Training

### Training Churn Model

```bash
python src/ml/train_churn_model.py \
  --data-source postgresql \
  --lookback-days 180 \
  --output-path models/churn_model.pkl
```

### Training Demand Model

```bash
python src/ml/train_demand_model.py \
  --data-source bigquery \
  --train-split 0.8 \
  --output-path models/demand_model.pkl
```

---

## 📊 API Endpoints

### Health Check

```
GET /health
```

Response:

```json
{"status": "ok", "version": "1.0.0"}
```

### Churn Prediction

```
POST /api/predict/churn
Content-Type: application/json

{
  "customer_id": integer,
  "recency_days": integer,
  "frequency": integer,
  "avg_monetary": float,
  "loyalty_member": boolean,
  "days_since_join": integer
}
```

### Batch Churn Prediction

```
POST /api/predict/churn/batch
Content-Type: application/json

{
  "customers": [
    {"customer_id": 1, "recency_days": 30, ...},
    {"customer_id": 2, "recency_days": 45, ...}
  ]
}
```

### Demand Forecasting

```
POST /api/predict/demand
Content-Type: application/json

{
  "product_id": integer,
  "category": string,
  "recent_sales_7d": integer,
  "recent_sales_30d": integer,
  "seasonality": string,
  "day_of_week": string
}
```

### Model Metadata

```
GET /api/models
```

Returns list of available models with versions and metrics.

---

## ⚙️ Configuration

Environment variables:

```env
# ML Service
ML_API_PORT=8000
ML_DEBUG=false

# Model Paths
CHURN_MODEL_PATH=models/churn_model.pkl
DEMAND_MODEL_PATH=models/demand_model.pkl

# Data Source
ML_DATA_SOURCE=bigquery  # Or "postgresql"
GOOGLE_PROJECT_ID=your_project
```

---

## 📈 Model Metrics

### Churn Model

- **Accuracy**: % correct predictions
- **Precision**: % of predicted churners who actually churned
- **Recall**: % of true churners identified
- **AUC-ROC**: Trade-off between true positives and false positives
- **F1-Score**: Harmonic mean of precision and recall

### Demand Model

- **MAE** (Mean Absolute Error): Average prediction error in units
- **RMSE** (Root Mean Squared Error): Penalizes large errors
- **MAPE** (Mean Absolute Percentage Error): % error relative to actual
- **R² Score**: Variance explained by model

---

## 🔍 Model Monitoring

### Prediction Logging

All predictions are logged to `ml_predictions.log`:

```
2026-02-20 14:30:45 [INFO] Churn prediction for customer 123: prob=0.23, category=LOW
2026-02-20 14:31:12 [INFO] Demand forecast for product 456: 7d=145, 30d=550
```

### Model Drift Detection

Periodically compare new predictions against historical baseline:

```bash
python src/ml/detect_drift.py --model churn --threshold 0.1
```

Returns alert if drift detected.

---

## 🔄 Batch Prediction

For bulk predictions on customer or product lists:

```bash
python src/ml/batch_predict.py \
  --model churn \
  --input-file customers.csv \
  --output-file predictions.csv
```

---

## 🧪 Testing

### Unit Tests

```bash
pytest src/ml/tests/test_churn_model.py -v
```

### Integration Tests

```bash
pytest src/ml/tests/test_api.py::test_churn_endpoint -v
```

### Load Testing

```bash
locust -f src/ml/tests/load_test.py --host=http://localhost:8000
```

---

## 📁 Project Structure

```
ml/
├── api.py                   # FastAPI application
├── churn_model.py           # Churn prediction logic
├── demand_model.py          # Demand forecasting logic
├── train_churn_model.py     # Churn model training
├── train_demand_model.py    # Demand model training
├── detect_drift.py          # Model drift detection
├── batch_predict.py         # Batch prediction utility
├── models/                  # Trained model artifacts
│   ├── churn_model.pkl
│   └── demand_model.pkl
├── tests/
│   ├── test_api.py
│   ├── test_churn_model.py
│   └── load_test.py
└── logs/
    └── ml_predictions.log
```

---

## 🐛 Troubleshooting

### Model Loading Error

```
FileNotFoundError: No such file or directory: 'models/churn_model.pkl'
```

- Train models: `python src/ml/train_churn_model.py`
- Or download pre-trained models from artifact repository

### API Connection Timeout

- Check database connectivity (PostgreSQL/BigQuery)
- Verify credentials in `.env`
- Check firewall rules if using cloud database

### Poor Model Performance

- Retrain with recent data: `python src/ml/train_churn_model.py --data-source bigquery`
- Check for data drift or schema changes
- Review logs for prediction errors

---

## 📋 Notes

- Models are **versioned** in the `models/` directory
- Predictions are **logged** for audit and feedback loops
- API supports **batch** and **single** predictions
- **Retraining** recommended quarterly or when drift detected
- All endpoints require **input validation** before passing to models
