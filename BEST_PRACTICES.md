# 🎯 Developer Habits & Best Practices

**Universal roadmap for professional software development.**
A checklist to prevent common mistakes, maintain consistency, and deliver production-quality code.

---

## 📋 Pre-Project Initialization

### Environment Management
- [x] **Create `.env` file immediately** — Store all secrets, API keys, database credentials, tokens
  - [x] Never commit `.env` to git (excluded in `.gitignore`)
  - [x] Add `.env` to `.gitignore` (checked on line 2)
  - [x] Document required env vars in `.env.template` (includes PostgreSQL, GCP, API, dbt config)
  - **Next step**: Copy `.env.template` to `.env` and fill in actual values

- [x] **Validate required environment variables — Fail Fast**
  ```python
  from dotenv import load_dotenv
  import os

  load_dotenv()

  # Validate required env vars immediately (prevents silent misconfigurations)
  required_vars = ["POSTGRES_HOST", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"]
  missing_vars = [var for var in required_vars if not os.getenv(var)]
  if missing_vars:
      raise RuntimeError(
          f"Missing required environment variables: {', '.join(missing_vars)}. "
          f"Please set them in .env or as system environment variables."
      )
  ```
  - **Why?** Prevents runtime failures after hours of processing (fail at startup instead)
  - **Example error**: `RuntimeError: Missing required environment variables: POSTGRES_HOST. Please set them in .env or as system environment variables.`
  - **Benefit**: Immediate feedback, saves time debugging

- [x] **Create `.gitignore` before first commit**
  - [x] Standard ignores: `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `*.pyc`, `*.egg-info/`
  - [x] IDE ignores: `.vscode/`, `.idea/`, `.DS_Store`, `*.swp`
  - [x] Local env: `.env`, `.env.local`, `config.local.yml`
  - [x] Build artifacts: `dist/`, `build/`, `.coverage/`

### Virtual Environments
- [x] **Isolate dependencies** — Use venv/virtualenv/conda for every project
  - [x] `.venv/` created and activated
  - [x] Never use system Python
  - [x] Document setup in README: `python -m venv venv` or `conda create -n project_name`
- [x] **Pin dependency versions** — Create `requirements.txt` or `pyproject.toml`
  - [x] `pyproject.toml` configured with uv package manager
  - [x] Document major versions with comments
  - Note: Used `uv` (faster, modern alternative to pip)

### Git Configuration
- [x] **Initialize git repo before writing code**
  - [x] Git repo initialized with atomic commit history
  - [x] Pre-commit hooks configured (black, ruff, trailing-whitespace fixes)
- [x] **Create `.gitattributes`** — Covered in `.gitignore`
  - Consistent line endings enforced by pre-commit hooks

---

## 💾 Atomic Commits (Most Critical)

### Commit Philosophy
**One logical change = One commit. Never mix multiple features/fixes in a single commit.**

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Code style (formatting, semicolons, etc.)
- `refactor:` Code refactoring (no feature change)
- `perf:` Performance improvements
- `test:` Add or update tests
- `chore:` Build, dependency updates, tooling
- `ci:` CI/CD configuration

### Examples of Good Atomic Commits

✅ **GOOD:**
```bash
git commit -m "feat: add RFM segmentation SQL query"
git commit -m "test: add unit tests for RFM calculation"
git commit -m "docs: document RFM business logic in data dictionary"
git commit -m "refactor: optimize RFM query with indexes"
```

❌ **BAD:**
```bash
git commit -m "lots of changes"
git commit -m "add RFM, fix bugs, update docs, and optimize queries"
git commit -m "wip"
```

### Before Every Commit
- [ ] **Review what you're committing** — `git diff` before staging
- [ ] **Test the code** — Run tests/linter/type checker locally
- [ ] **Write a meaningful message** — Explain WHY, not WHAT
- [ ] **One feature per commit** — Don't mix concerns

### Commit Workflow
```bash
# 1. Check what changed
git status
git diff

# 2. Stage only related changes
git add path/to/related/files
git add -p  # Interactive staging (stage chunks, not whole files)

# 3. Commit with clear message
git commit -m "feat: implement user authentication module"

# 4. Verify before push
git log --oneline -3
git push origin feature-branch
```

---

## 🏗️ Code Organization

### Directory Structure
- [ ] **Keep source code organized by layer/domain**
  ```
  src/
  ├── analytics/    (business logic, queries)
  ├── etl/         (data pipelines)
  ├── ml/          (model training, inference)
  ├── postgres/    (database setup, migrations)
  └── utils/       (shared utilities)
  ```

- [ ] **Separate concerns**
  - Data models in one place
  - Business logic in another
  - API endpoints separate from core logic
  - Always follow monorepo or multi-repo strategy consistently

### File Naming
- [ ] **Use descriptive, snake_case names** (Python) or camelCase (JS)
  - Good: `seed_synthetic_data.py`, `rfm_segmentation.sql`
  - Bad: `data.py`, `query.sql`, `script1.py`

- [ ] **Group related files**
  - All models together: `models/`, `models/staging/`, `models/marts/`
  - All tests together: `tests/unit/`, `tests/integration/`
  - All configs together: `config/`, `config/dev.yml`, `config/prod.yml`

---

## ✍️ Documentation (As You Go)

### README
- [ ] **Write README first** — Describes what, why, how
  - Project goal
  - Quick start (4 steps max)
  - Architecture overview
  - Development setup
  - Configuration instructions
  - Example usage

### Inline Comments
- [ ] **Comment WHY, not WHAT**
  - BAD: `x = x + 1  # increment x`
  - GOOD: `x = x + 1  # offset by 1 to match 1-indexed schema`

- [ ] **Use docstrings for functions/classes**
  ```python
  def calculate_rfm_score(customer_id: int, lookback_days: int = 90) -> dict:
      """
      Calculate RFM (Recency, Frequency, Monetary) score for a customer.

      Args:
          customer_id: Unique customer identifier
          lookback_days: Historical window in days (default 90)

      Returns:
          dict with keys 'recency', 'frequency', 'monetary', 'score'

      Raises:
          ValueError: If customer_id not found in database
      """
  ```

### Data Dictionary
- [ ] **Document every table, column, and transformation**
  - Table name, purpose, grain
  - Column name, data type, business meaning, nullable?
  - Example: "customer_id: INT, unique identifier for customer, NOT NULL"

### Architecture Diagram
- [ ] **Include data flow diagram**
  - Sources → ETL → Warehouse → BI/ML
  - Use tools: Mermaid, Lucidchart, Draw.io
  - Update when architecture changes

### Changelog
- [ ] **Keep `CHANGELOG.md` or `HISTORY.md`**
  - What changed, when, why
  - Format: date, version, breaking changes highlighted
  - Example: "v1.2.0 — 2026-02-19 — Added RFM segmentation, deprecated batch_size parameter"

---

## 🧪 Testing & Quality

### Write Tests
- [ ] **Test-driven development (TDD) or write tests alongside code**
  - Unit tests: Test individual functions
  - Integration tests: Test features end-to-end
  - Data tests: Validate data quality (dbt tests, SQL checks)

- [ ] **Organize tests to mirror source structure**
  ```
  tests/
  ├── unit/
  │   ├── test_rfm_calculation.py
  │   └── test_churn_model.py
  ├── integration/
  │   └── test_etl_pipeline.py
  └── data/
      └── test_quality_checks.sql
  ```

### Code Quality
- [ ] **Use linters and formatters**
  - Python: `black`, `ruff`, `pylint`
  - SQL: `sqlfluff`
  - Use pre-commit hooks to auto-check

- [ ] **Type hints (Python)**
  ```python
  def load_data(path: str, limit: int = None) -> pd.DataFrame:
      ...
  ```

- [ ] **Configure pre-commit hooks**
  ```bash
  # .pre-commit-config.yaml
  repos:
    - repo: https://github.com/psf/black
      rev: 23.1.0
      hooks:
        - id: black
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.1.0
      hooks:
        - id: ruff
  ```

### Run Tests Before Committing
```bash
pytest tests/
python -m black --check src/
python -m ruff check src/
```

---

## 🔐 Secrets & Configuration

### Environment Variables
- [ ] **Use `.env` for local development**
  ```bash
  DATABASE_URL=postgresql://user:password@localhost/dbname
  GCP_PROJECT_ID=my-gcp-project
  API_KEY=sk-abc123xyz
  ENVIRONMENT=development
  ```

- [ ] **Create `.env.example` or `ENV_TEMPLATE.md`**
  ```bash
  # .env.example
  DATABASE_URL=postgresql://user:password@host/dbname
  GCP_PROJECT_ID=your-gcp-project-id
  API_KEY=your-api-key
  ```

- [ ] **Never hardcode secrets**
  - Load from environment: `os.getenv("DATABASE_URL")`
  - Use config management tools for production

### CI/CD Secrets
- [ ] **Use GitHub Secrets, GitLab CI Variables, or platform equivalents**
  - Store in secure vault
  - Rotate regularly
  - Document what each secret is used for

### Domain Constants & Business Rules
- [ ] **Separate domain constants from configuration**
  ```python
  # ✅ GOOD: Keep small, stable constants in code
  REGIONS = ["North", "South", "East", "West"]
  PRODUCT_CATEGORIES = {"Textile": [...], "Accessories": [...]}

  # ✅ Configurable params from environment
  NUM_STORES = int(os.getenv("NUM_STORES", 50))
  NUM_PRODUCTS = int(os.getenv("NUM_PRODUCTS", 500))
  ```

- [ ] **Move to external config (YAML/JSON) when:**
  - Business rules change frequently (no code deploy needed)
  - Supporting multiple environments with different constants
  - Number of constants grows significantly (50+ items)
  - International expansion requires regional customization

- [ ] **Current approach is pragmatic for MVP:**
  - Code constants work fine for stable, small datasets
  - Easy to version control and review
  - Upgrade to external config in Week 3-4 if needed

---

## 📦 Dependency Management

### Track Dependencies
- [ ] **Maintain single source of truth for dependencies**
  - `requirements.txt` (Python)
  - `pyproject.toml` + `poetry.lock` (Python with Poetry)
  - `package.json` + `package-lock.json` (Node.js)
  - `Gemfile` + `Gemfile.lock` (Ruby)

- [ ] **Document why each dependency exists**
  ```python
  # requirements.txt
  pandas==1.5.3        # Data manipulation
  apache-airflow==2.5.0  # Workflow orchestration
  pytest==7.2.1        # Testing framework
  ```

### Update Dependencies Safely
- [ ] **Check for breaking changes before updating**
  ```bash
  pip list --outdated
  pip install --upgrade package_name --dry-run
  ```

- [ ] **Test after updating dependencies**
  - Run full test suite
  - Check for compatibility issues

---

## 🚀 Deployment & DevOps

### Docker (if applicable)
- [ ] **Use `.dockerignore`** — Similar to `.gitignore`
  ```
  .git
  .gitignore
  .env
  __pycache__
  venv/
  .pytest_cache/
  *.pyc
  ```

- [ ] **Dockerfile best practices**
  - Use specific base image tags (not `latest`)
  - Pin RUN command package versions
  - Multi-stage builds for smaller images
  - `FROM python:3.11-slim` not `FROM python:latest`

### CI/CD Pipeline
- [ ] **Automate tests on every push**
  - GitHub Actions, GitLab CI, Jenkins, etc.
  - Run: tests, linting, type checking, security scans

- [ ] **Automate deployments**
  - Dev: Auto-deploy on main
  - Staging: Manual or schedule-based
  - Production: Manual approval required

### Monitoring & Logging
- [x] **Add structured logging with rotation**
  ```python
  import logging
  from logging.handlers import RotatingFileHandler

  logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s [%(levelname)s] %(message)s",
      handlers=[
          logging.StreamHandler(),  # console output
          RotatingFileHandler(
              "app.log", maxBytes=5_000_000, backupCount=3
          )  # 5MB files, keep 3 backups
      ],
  )
  logger = logging.getLogger(__name__)
  logger.info(f"Processing customer {customer_id}")
  logger.error(f"Failed to load data: {error}")
  ```
  - **Why rotating?** Prevents unbounded log file growth; keeps last 3 rotations (15MB max)
  - **Console + File**: Immediate visibility during dev, permanent record for debugging

- [x] **Suppress noisy third-party logs**
  ```python
  # Reduce verbosity from chatty libraries (psycopg2, urllib3, etc.)
  logging.getLogger("psycopg2").setLevel(logging.WARNING)
  logging.getLogger("urllib3").setLevel(logging.WARNING)
  ```
  - **Why?** Database drivers log internal protocol; clutters your application logs
  - **Result**: Only see YOUR events, not driver noise

- [ ] **Avoid emojis in log messages and scripts**
  - ❌ BAD: `logger.info("✅ Data loaded successfully")`
  - ✅ GOOD: `logger.info("[OK] Data loaded successfully")`
  - **Reason**: Emojis cause encoding issues on Windows terminals (charmap codec errors), CI/CD systems, and log aggregation pipelines that expect ASCII-only output. Use `[OK]`, `[ERROR]`, `[WARNING]` instead.

- [ ] **Plan for observability at scale** (future enhancement)
  - Current: Text logs to file ✅
  - Next: Structured JSON logging when adding ELK/Datadog (Week 3+)
  - **Why JSON?** Machine-parseable for log aggregation platforms; enables metrics extraction, anomaly detection, automated alerting
  - Tools: `python-json-logger`, Datadog Agent, ELK Stack, Splunk

- [ ] **Monitor in production**
  - Track errors, latency, resource usage
  - Set up alerts for failures
  - Log to centralized system (Datadog/ELK) for multi-service visibility

---

## 🔄 Code Review

### Before Merging
- [ ] **Create pull request (PR) with clear description**
  - What changed and why
  - Link to related issues
  - Screenshots (if UI)
  - Testing instructions

- [ ] **Request code review** — Never merge your own code
  - At least 1 other person reviews
  - Address all comments before merging

- [ ] **Ensure CI passes**
  - All tests pass
  - No linting errors
  - No security warnings

- [ ] **Squash or rebase** (optional)
  - Keep history clean: `git rebase -i origin/main`
  - Avoid "fix typo" commits in final history

---

## 🗂️ Project-Specific Habits

### Data Projects (SQL, dbt, Analytics)
- [ ] **Version control for SQL**
  - Store all DDL statements in `.sql` files
  - Version your data migrations
  - Use dbt for transformation logic

- [ ] **Test data quality**
  - Unit tests for transformations
  - Data profiling tests (nulls, duplicates, ranges)
  - Validation queries

- [ ] **Document data lineage**
  - Source → raw → staging → marts
  - Add comments in dbt models
  - Link to business glossary

### ML/AI Projects
- [ ] **Track training data versions**
  - Which dataset was used for training?
  - Random seed for reproducibility
  - Data splits documented

- [ ] **Version models**
  - Store models with metadata (date, performance, hyperparams)
  - Use MLflow, DVC, or similar

- [ ] **Document model assumptions**
  - Features used
  - Training period
  - Performance metrics
  - Known limitations

### Python Projects
- [ ] **Use type hints everywhere**
  ```python
  from typing import Optional, List
  def process(data: List[dict], limit: Optional[int] = None) -> dict:
      ...
  ```

- [ ] **Use dataclasses or Pydantic for data models**
  ```python
  from dataclasses import dataclass

  @dataclass
  class Customer:
      customer_id: int
      name: str
      email: str
  ```

---

## 📋 Project Launch Checklist

Before pushing to production or sharing publicly:

- [ ] All tests pass locally and in CI
- [ ] Code reviewed by at least one peer
- [ ] No hardcoded secrets
- [ ] `.env.example` exists with template
- [ ] `.gitignore` excludes all sensitive files
- [ ] README is complete and accurate
- [ ] CHANGELOG updated
- [ ] Docstrings added to all functions
- [ ] Architecture diagram up-to-date
- [ ] Performance benchmarked (if applicable)
- [ ] Error handling implemented (no bare `except:`)
- [ ] Logging added (at DEBUG, INFO, ERROR levels)
- [ ] Dependencies documented in requirements file
- [ ] Commit history is clean (meaningful messages, atomic commits)
- [ ] Database migrations tested (if applicable)
- [ ] No TODO comments left in code (or tracked in issues)

---

## 🎓 Principles to Live By

| Principle | Meaning |
|-----------|---------|
| **DRY** | Don't Repeat Yourself — Extract reusable functions |
| **KISS** | Keep It Simple, Stupid — Avoid over-engineering |
| **SOLID** | Single Responsibility, Open/Closed, Liskov, Interface, Dependency — Design patterns |
| **YAGNI** | You Aren't Gonna Need It — Don't add features you don't need yet |
| **SoC** | Separation of Concerns — Different layers do different things |
| **Atomic** | Each commit is a complete, working change |
| **Explicit** | Clear > clever; readable code > compact code |

---

## 🧠 Mental Checklist Before Pushing

```
Before each git push, ask yourself:

1. ✅ Did I test this locally?
2. ✅ Did I write/update tests?
3. ✅ Did I run linter/formatter?
4. ✅ Did I add comments where needed?
5. ✅ Did I check .gitignore? (no .env, no venv/)
6. ✅ Is my commit message clear and atomic?
7. ✅ Did I remove debugging code? (print, console.log, etc.)
8. ✅ Did I update documentation?
9. ✅ Is there any hardcoded data/secrets?
10. ✅ Would my team understand this in 6 months?
```

---

## 📚 References & Tools

- **Git**: [Git Book](https://git-scm.com/book/en/v2)
- **Conventional Commits**: [conventionalcommits.org](https://www.conventionalcommits.org/)
- **Python Style**: [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- **Pre-commit**: [pre-commit.com](https://pre-commit.com/)
- **dbt Best Practices**: [dbt Docs](https://docs.getdbt.com/)
- **Data Quality**: [Great Expectations](https://greatexpectations.io/)
- **SQL Linting**: [SQLFluff](https://www.sqlfluff.com/)

---

**Last Updated**: February 19, 2026
**Purpose**: Universal roadmap for professional development practices
