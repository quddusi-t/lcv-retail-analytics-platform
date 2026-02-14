# Source Code Directory

This folder contains all source code for the LCV Retail Analytics Platform:

- **postgres/**: PostgreSQL schema setup and synthetic data generation
- **etl/**: Extract-Load pipeline (Postgres → GCS → BigQuery) + dbt models
- **analytics/**: SQL views and KPI definitions
- **ml/**: Machine learning models (churn prediction, demand forecasting) and FastAPI API

Each subfolder has its own README with specific setup instructions.
