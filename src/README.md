# Source Code Directory

This folder contains all source code for the **LCV Retail Analytics Platform**.
It is organized into modular components for database setup, data pipelines, analytics, and machine learning services.

---

## 📂 Structure

- [**postgres/**](postgres/README.md)
  PostgreSQL schema setup and synthetic data generation scripts.

- [**etl/**](etl/README.md)
  Extract–Load pipeline (Postgres → GCS → BigQuery) and dbt models.

- [**analytics/**](analytics/README.md)
  SQL views and KPI definitions for reporting and dashboards.

- [**ml/**](ml/README.md)
  Machine learning models (churn prediction, demand forecasting) and FastAPI API service.

---

## ⚙️ Configuration

- All modules read environment variables from `.env`.
- A `.env.template` is provided with required and optional settings.
- Create a `.env` file per environment (dev, staging, prod) to override dataset sizes, seeds, and credentials.

---

## ▶️ Running

Typical entry points:

- **Synthetic data generation**
  ```bash
  python postgres/seed_synthetic_data.py
  ```

- **ETL pipeline**
  ```bash
  python etl/run_pipeline.py
  ```

- **ML API service**
  ```bash
  uvicorn ml.api:app --reload
  ```

---

## 📦 Dependencies

- Python dependencies are tracked in `requirements.txt` or `pyproject.toml`.
- dbt models are defined in `dbt_project.yml`.
- Each subfolder README contains specific setup instructions.

---

## 🗺️ Notes

- Keep documentation close to the code: each subfolder has its own README.
- Use environment-specific `.env` files to separate dev/staging/prod runs.
- Logs from synthetic data generation are written to `seed_data.log` with rotation enabled.
