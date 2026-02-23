# Changelog

All notable changes to the **LCV Retail Analytics Platform** project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Initial project setup with star schema design
- Synthetic data generator for PostgreSQL (`seed_synthetic_data.py`)
- Advanced SQL queries: YoY sales growth, RFM segmentation, inventory turnover, churn detection
- Data governance documentation with data dictionary and lineage
- Pre-commit hooks configured (black, ruff, trailing-whitespace)
- `.env.template` with configuration documentation
- BEST_PRACTICES.md (Developer Habits & Best Practices)
- GOVERNANCE.md (Data Dictionary & Quality Rules)
- ROADMAP.md (5-Week Development Roadmap)
- Comprehensive README with architecture diagrams and feature overview

### Changed
- Renamed `GOOD_PRACTICES.md` to `BEST_PRACTICES.md` (Feb 24, 2026)

### Fixed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Security
- `.env` excluded from version control
- Environment variables documented in `.env.template`

---

## [0.1.0] - 2026-02-24

### Initial Release

**Objective**: Establish foundation for end-to-end retail analytics platform

#### Added
- ✅ Project initialized with Python 3.10+
- ✅ PostgreSQL source database schema with fact/dimension tables
- ✅ Virtual environment setup with dependency pinning (`pyproject.toml`)
- ✅ Pre-commit hooks (black, ruff, trailing-whitespace, yaml validation)
- ✅ Synthetic data generator: 50 stores, 500 products, 10k customers, 1M transactions
- ✅ Advanced SQL queries for analytics:
  - Year-over-Year (YoY) sales growth analysis
  - RFM customer segmentation (Recency, Frequency, Monetary)
  - Inventory turnover by product category
  - Churn detection (inactive customers >90 days)
- ✅ Data governance documentation
- ✅ Architecture documentation with diagram

#### Planned (Future Versions)
- [ ] BigQuery integration and dbt transformation pipelines
- [ ] BI dashboard in Looker Studio
- [ ] Churn prediction ML model with FastAPI endpoint
- [ ] Demand forecasting model
- [ ] Unit tests (pytest)
- [ ] Data quality validation tests
- [ ] CI/CD pipeline configuration

---

## Version Roadmap

| Version | Target Date | Key Milestone |
|---------|-------------|---------------|
| 0.1.0 | Feb 24, 2026 | Data modeling, synthetic data, SQL queries |
| 0.2.0 | Mar 10, 2026 | BigQuery integration, dbt transformations |
| 0.3.0 | Mar 21, 2026 | Analytics dashboard, ML models, API |
| 1.0.0 | Q2 2026 | Production-ready with monitoring |

---

**Maintainer**: Kutsi Tusuz (ktusuz@gmail.com)
**License**: MIT
**Last Updated**: February 24, 2026
