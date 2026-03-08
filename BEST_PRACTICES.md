# 🎯 Developer Habits & Best Practices

**Universal roadmap for professional software development.**
A comprehensive guide to prevent common mistakes, maintain consistency, and deliver production-quality code.

---

## 📋 Pre-Project Initialization

### Environment Management
- **Create `.env` file immediately** — Store all secrets, API keys, database credentials, tokens
  - Never commit `.env` to git (add to `.gitignore`)
  - Document required env vars in `.env.template` with clear descriptions
  - Copy `.env.template` to `.env` locally and fill in actual values

- **Validate required environment variables — Fail Fast**
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

- **Create `.gitignore` before first commit** with these patterns:
  - Standard ignores: `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `*.pyc`, `*.egg-info/`
  - IDE ignores: `.vscode/`, `.idea/`, `.DS_Store`, `*.swp`
  - Local env: `.env`, `.env.local`, `config.local.yml`
  - Build artifacts: `dist/`, `build/`, `.coverage/`

### Virtual Environments
- **Isolate dependencies** — Use venv/virtualenv/conda for every project
  - Never use system Python
  - Activate virtual environment in all terminals
  - Document setup in README: `python -m venv venv` or `conda create -n project_name`
- **Pin dependency versions** — Create `requirements.txt` or `pyproject.toml`
  - Document major dependency versions with inline comments explaining purpose
  - Consider using `uv` (faster, modern alternative to pip)

#### Package Manager Comparison

| Tool | Speed | Best For | Pros | Cons |
|------|-------|----------|------|------|
| **pip** | Standard | Simple projects, CI/CD | Ubiquitous, lightweight (30 MB) | No dependency conflict resolution |
| **uv** | ⚡ 10-100x faster | Modern Python projects | Fast (Rust-based), pip-compatible, single binary | Newer ecosystem, less adoption |
| **conda** | Slow | Data science, non-Python deps | Handles C/Fortran/system packages | Heavy (~500 MB), slower, overkill for pure Python |
| **Poetry** | Medium | Complex projects with lock files | Beautiful locks, publish to PyPI, dependency resolution | Slower than uv, steeper learning curve |
| **pipenv** | Slow | Locked dependencies + virtualenv | Combines venv + lock files | Less maintained, slower than Poetry |

**For this project**: `uv` (already in `pyproject.toml`) — fast, modern, Rust-based, pip-compatible.

**Decision guide:**
- **MVP / simple project**: pip + `requirements.txt`
- **Production Python project**: uv + `pyproject.toml` (our choice)
- **Data science**: conda (includes NumPy, SciPy, Jupyter pre-compiled)
- **Complex dependencies / publishing to PyPI**: Poetry
- **Legacy projects**: pipenv (avoid for new projects)

### Git Configuration
- **Initialize git repo before writing code**
  - Set up git with atomic commit history discipline
  - Configure pre-commit hooks (black, ruff, trailing-whitespace fixes)
- **Use `.gitattributes`** for consistent line endings (enforced by pre-commit hooks)

---

## 🌳 Branching Strategy & Code Review

### Feature Branch Workflow

**Core principle:** Never commit directly to `main`. Every change starts on a feature branch.

```
main (always deployable) ← never commit directly here
  ↑
  └─ feature/rfm-analysis (your work)
  │  ├─ commit: "feat: add RFM calculation"
  │  ├─ commit: "test: add RFM unit tests"
  │  └─ pull request → code review → merge
  │
  └─ fix/null-handling
  │  ├─ commit: "fix: handle null values in ETL"
  │  └─ pull request → code review → merge
```

**Why branching matters:**
- Main always stays clean and deployable
- Easy to revert bad changes (revert entire branch)
- Full commit history per feature (bisecting, debugging)
- Code review before merging (team learning)
- Parallel work (multiple branches simultaneously)

### Branch Naming Convention

| Type | Pattern | Example | Purpose |
|------|---------|---------|---------|
| **Feature** | `feature/short-description` | `feature/customer-segmentation` | New functionality |
| **Fix** | `fix/short-description` | `fix/null-handling-etl` | Bug fix |
| **Chore** | `chore/short-description` | `chore/update-dependencies` | Config, cleanup, tooling |
| **Refactor** | `refactor/short-description` | `refactor/etl-pipeline` | Code restructure (no feature change) |
| **Docs** | `docs/short-description` | `docs/add-architecture-guide` | Documentation only |

**Naming rules:**
- Lowercase with hyphens (not underscores or spaces)
- Descriptive (not `fix/bug` or `feature/stuff`)
- Start with type prefix (feature/, fix/, chore/, etc.)

### Feature Branch Workflow (Step-by-Step)

```bash
# Step 1: Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# Step 2: Make changes, commit atomically
git add src/etl/new_pipeline.py
git commit -m "feat: implement new ETL pipeline"

# Step 3: Push to GitHub
git push -u origin feature/your-feature-name
# Output: "Create a pull request for 'feature/your-feature-name'"

# Step 4: Create Pull Request (PR) on GitHub
# (See next section for PR details)

# Step 5: After PR is merged, clean up local branch
git checkout main
git pull origin main
git branch -d feature/your-feature-name
```

### What is a Pull Request (PR)?

**A Pull Request is a formal request to merge your changes into main.**

Think of it like a proposal:

```
Your Feature Branch:
  ✅ 3 new commits
  ✅ All tests passing
  ✅ Code formatted with black/ruff
  ✅ Documentation updated

You create a PR saying:
  "I have 3 new commits. Please review and merge them."

GitHub shows:
  - What changed (file diffs)
  - Which tests passed/failed
  - Code coverage impact
  - Comment threads for discussion

Reviewers:
  ✅ Approve & merge
  ❌ Request changes
  ❓ Ask questions in comments
```

### Code Review Process

**How review works (team context):**

```
Developer A:
  1. Creates feature/rfm-analysis branch
  2. Commits 3 changes
  3. Pushes to GitHub
  4. Creates Pull Request (PR)
  5. Requests review from Developer B

Developer B (Reviewer):
  1. Opens PR on GitHub
  2. Reads commit messages
  3. Reviews each file diff
  4. Checks if tests pass
  5. Leaves comments/suggestions
  6. Either:
     - ✅ "Approved! Looks good." → Merge
     - 📝 "Please fix formatting in line 42" → Developer A updates
     - ❌ "Logic looks wrong here..." → Discussion thread

Developer A (After feedback):
  1. Makes requested changes
  2. Commits fix: "refactor: address review feedback"
  3. Pushes to same branch (auto-updates PR)
  4. Comments: "Done! Check new commit."

Developer B:
  5. Reviews updated code
  6. ✅ "Approved!" → Merges PR to main

Result:
  main now has the feature (with peer review)
```

### PR Example: Real Conversation

```markdown
Pull Request: "feat: add RFM segmentation"
Created by: Developer A
Base: main ← Target: feature/rfm-analysis

---

Files Changed: 3
  ✅ models/staging/stg_rfm_clean.sql (+85 lines)
  ✅ tests/test_rfm_calculation.py (+40 lines)
  ✅ BEST_PRACTICES.md (+10 lines)

Commits:
  1. feat: add RFM staging model with deduplication
  2. test: add RFM calculation unit tests
  3. docs: document RFM business logic

Test Results:
  ✅ All 42 tests pass
  ✅ Code coverage: 87% (was 85%)
  ✅ Linting: 0 errors

---

REVIEW THREAD:

🔍 Reviewer (Developer B):
  "Nice! I have a couple questions:

  Line 42 in stg_rfm_clean.sql:
  ```sql
  CASE WHEN amount < 0 THEN NULL ELSE amount END
  ```
  Should we round to 2 decimals here? Or in marts layer?"

💬 Author (Developer A):
  "Good catch! Actually, I think rounding belongs in marts
  (final layer), not staging. Staging should just validate.
  What do you think?"

💬 Reviewer (Developer B):
  "Makes sense. Keep it in marts. Also, can you add a comment
  explaining why we null out negative amounts? For future devs?"

✏️ Author Updates Code:
  - Adds comment: "Null negative amounts (likely refunds/errors)"
  - Commits: "refactor: add comment explaining validation logic"
  - Pushes same branch → PR auto-updates

✅ Reviewer (Developer B):
  "Perfect! Approved and merged."

Result:
  Feature merged to main with peer validation
```

### Solo Developer: Do You Need PRs?

**Short answer:** Not strictly required, but recommended.

**Solo workflow options:**

| Approach | Pros | Cons | When to Use |
|----------|------|------|-------------|
| **No PR (direct merge)** | Fastest (skip review) | No self-check, easy mistakes | Emergency hotfixes only |
| **Self-review PR** | Catches your own mistakes | Takes 5 min extra | Recommended for all work |
| **No branch (direct commit)** | Absolute fastest | No ability to revert, loses history | ❌ Not recommended |

**Best practice (solo):**

```bash
# Still branch, still PR, but you review your own code
git checkout -b feature/new-analysis
# Make changes, commit, push
git push -u origin feature/new-analysis

# On GitHub: Create PR (takes 1 min)
# Review your own code: "Does this fix the problem? Tests pass?"
# ✅ Approve and merge

# Why bother?
# - Clear commit history per feature
# - Can revert entire feature if needed
# - Easy to add team members later (they already have PR workflow)
# - Self-review catches ~30% of your own mistakes
```

### PR Best Practices

#### Writing a Good PR Description

```markdown
# PR Title (Short, descriptive)
feat: add RFM segmentation for customer analysis

## Description
Implements Recency, Frequency, Monetary (RFM) segmentation
to identify high-value customers for targeted campaigns.

## What Changed
- Added staging model: stg_rfm_clean.sql
- Calculates RFM scores using 90-day lookback
- Includes null handling for edge cases

## Testing
- Unit tests: 8 new tests, all passing
- Manual test: Validated against 1M synthetic records
- Performance: Query completes in <2 seconds

## Related Issues
Fixes #42 (Customer Segmentation)

## Checklist
- [x] Tests added/updated
- [x] Documentation updated
- [x] No hardcoded secrets
- [x] Linting passes (black, ruff)
```

**Why good descriptions help:**
- Reviewers understand context
- Future you knows why change was made
- Easy bisecting (git log --oneline shows descriptions)
- Audit trail for compliance

#### How to Request Review

```bash
# On GitHub, comment:
@Developer-B - could you review this when you get a chance?

# Or assign directly:
GitHub UI → Assignees → Select reviewer

# Reviewer gets notification → Reviews → Comments
```

#### Resolving Review Feedback

```bash
# Reviewer comments: "Fix formatting on line 42"

# You make the fix locally
git add file.py
git commit -m "refactor: address review feedback from @Developer-B"
git push  # Same branch (auto-updates PR)

# Comment in PR thread:
"Done! Check commit abc123"

# Reviewer re-checks
❌ Approve again if needed
✅ Merge to main
```

#### Never Force-Push to Main

```bash
# ❌ BAD (never do this)
git push --force-push origin main
# This DESTROYS history, breaks teammates' work

# ❌ BAD (don't rewrite shared branches)
git rebase -i origin/main

# ✅ GOOD (safe for your feature branch)
git rebase -i origin/main  # On feature branch only
git push --force-push origin feature/your-feature
```

### When to Bypass PR (Solo Developer)

Only in these cases:

```bash
# Emergency production hotfix (2am)
#   → Branch, fix fast, merge directly OR merge with --no-verify

# Documentation typo ("s/recieved/received/")
#   → Can direct commit or quick PR

# Config file that won't affect code
#   → Can merge directly (already tested by hooks)

# Everything else
#   → Create PR, even if you review it yourself
```

---

## 💾 Atomic Commits (Review Reminder)

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

> **See [Feature Branch Workflow](#feature-branch-workflow-step-by-step) section for full commit process, pre-commit checklist, and git commands.**

---

## 🏗️ Code Organization

### Directory Structure
- **Keep source code organized by layer/domain**
  ```
  src/
  ├── analytics/    (business logic, queries)
  ├── etl/         (data pipelines)
  ├── ml/          (model training, inference)
  ├── postgres/    (database setup, migrations)
  └── utils/       (shared utilities)
  ```

- **Separate concerns**
  - Data models in one place
  - Business logic in another
  - API endpoints separate from core logic
  - Always follow monorepo or multi-repo strategy consistently

### File Naming
- **Use descriptive, snake_case names** (Python) or camelCase (JS)
  - Good: `seed_synthetic_data.py`, `rfm_segmentation.sql`
  - Bad: `data.py`, `query.sql`, `script1.py`

- **Group related files**
  - All models together: `models/`, `models/staging/`, `models/marts/`
  - All tests together: `tests/unit/`, `tests/integration/`
  - All configs together: `config/`, `config/dev.yml`, `config/prod.yml`

---

## ✍️ Documentation (As You Go)

### README
- **Write README first** — Describes what, why, how
  - Project goal
  - Quick start (4 steps max)
  - Architecture overview
  - Development setup
  - Configuration instructions
  - Example usage

### Inline Comments
- **Comment WHY, not WHAT**
  - BAD: `x = x + 1  # increment x`
  - GOOD: `x = x + 1  # offset by 1 to match 1-indexed schema`

- **Use docstrings for functions/classes**
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
- **Document every table, column, and transformation**
  - Table name, purpose, grain
  - Column name, data type, business meaning, nullable?
  - Example: "customer_id: INT, unique identifier for customer, NOT NULL"

### Architecture Diagram
- **Include data flow diagram**
  - Sources → ETL → Warehouse → BI/ML
  - Use tools: Mermaid, Lucidchart, Draw.io
  - Update when architecture changes

### Changelog
- **Keep `CHANGELOG.md` or `HISTORY.md`**
  - What changed, when, why
  - Format: date, version, breaking changes highlighted
  - Example: "v1.2.0 — 2026-02-19 — Added RFM segmentation, deprecated batch_size parameter"

---

## 🧪 Testing & Quality

### Write Tests
- **Test-driven development (TDD) or write tests alongside code**
  - Unit tests: Test individual functions
  - Integration tests: Test features end-to-end
  - Data tests: Validate data quality (dbt tests, SQL checks)

- **Organize tests to mirror source structure**
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
- **Use linters and formatters**
  - Python formatters: `black` (auto-fix code style)
  - Python linters: `ruff` (detect issues, auto-fix most)
  - SQL linting: `sqlfluff`
  - **All run via pre-commit hooks** automatically on every `git commit`

- **Pre-commit hooks prevent common issues**
  - ✅ **Auto-fix**: black, ruff, trailing-whitespace, end-of-file-fixer (4 hooks fix problems)
  - ✅ **Detect**: check-yaml, check-merge-conflict (2 hooks catch mistakes before commit)
  - Result: Cleaner commits, fewer lint errors in CI/CD, consistent codebase

- **Type hints (Python)**
  ```python
  def load_data(path: str, limit: int = None) -> pd.DataFrame:
      ...
  ```

- **Configure pre-commit hooks** — Run on every commit to catch issues automatically
  ```bash
  # .pre-commit-config.yaml (full configuration with all hooks)
  repos:
    # Code formatter (auto-fixes)
    - repo: https://github.com/psf/black
      rev: 25.12.0
      hooks:
        - id: black
          language_version: python3.10
          # Auto-formats Python code (88 chars/line, consistent style)

    # Linter (auto-fixes)
    - repo: https://github.com/astral-sh/ruff-pre-commit
      rev: v0.15.1
      hooks:
        - id: ruff
          args: [--fix]
          # Fast Python linter (imports, unused vars, style)

    # General file checks
    - repo: https://github.com/pre-commit/pre-commit-hooks
      rev: v5.0.0
      hooks:
        - id: trailing-whitespace
          # Removes spaces/tabs at end of lines (commit only needed content)
        - id: end-of-file-fixer
          # Ensures all files end with exactly one newline (POSIX compliance)
        - id: check-yaml
          # Validates YAML syntax (catches malformed .yml files before commit)
        - id: check-merge-conflict
          # Detects merge conflict markers (<<<, ===, >>>) left in code
  ```

**Hook Details:**

| Hook | Type | Purpose | Example |
|------|------|---------|---------|
| **black** | Auto-fix | Format Python code consistently | `x=1+2` → `x = 1 + 2` |
| **ruff** | Auto-fix | Lint Python (unused imports, style) | `import os  # unused` → removed |
| **trailing-whitespace** | Auto-fix | Remove spaces at line ends | `"hello "` → `"hello"` |
| **end-of-file-fixer** | Auto-fix | Ensure newline at EOF | File ends at line 42 → adds `\n` |
| **check-yaml** | Detect | Validate YAML syntax | `key: [invalid` → fails commit |
| **check-merge-conflict** | Detect | Find merge markers | `<<<<<<< HEAD` → fails commit |

### Run Tests Before Committing
```bash
pytest tests/
python -m black --check src/
python -m ruff check src/
```

---

## 🔐 Secrets & Configuration

### Environment Variables
- **Use `.env` for local development**
  ```bash
  DATABASE_URL=postgresql://user:password@localhost/dbname
  GCP_PROJECT_ID=my-gcp-project
  API_KEY=sk-abc123xyz
  ENVIRONMENT=development
  ```

- **Create `.env.example` or `ENV_TEMPLATE.md`**
  ```bash
  # .env.example
  DATABASE_URL=postgresql://user:password@host/dbname
  GCP_PROJECT_ID=your-gcp-project-id
  API_KEY=your-api-key
  ```

- **Never hardcode secrets**
  - Load from environment: `os.getenv("DATABASE_URL")`
  - Use config management tools for production

### CI/CD Secrets
- **Use GitHub Secrets, GitLab CI Variables, or platform equivalents**
  - Store in secure vault
  - Rotate regularly
  - Document what each secret is used for

### Domain Constants & Business Rules
- **Separate domain constants from configuration**
  ```python
  # ✅ GOOD: Keep small, stable constants in code
  REGIONS = ["North", "South", "East", "West"]
  PRODUCT_CATEGORIES = {"Textile": [...], "Accessories": [...]}

  # ✅ Configurable params from environment
  NUM_STORES = int(os.getenv("NUM_STORES", 50))
  NUM_PRODUCTS = int(os.getenv("NUM_PRODUCTS", 500))
  ```

- **Move to external config (YAML/JSON) when:**
  - Business rules change frequently (no code deploy needed)
  - Supporting multiple environments with different constants
  - Number of constants grows significantly (50+ items)
  - International expansion requires regional customization

- **Consider pragmatic approach for MVP:**
  - Code constants work well for stable, small datasets
  - Easy to version control and review
  - Upgrade to external config when requirements grow (Week 3-4+)

---

## 📦 Dependency Management

### Track Dependencies
- **Maintain single source of truth for dependencies**
  - `requirements.txt` (Python)
  - `pyproject.toml` + `poetry.lock` (Python with Poetry)
  - `package.json` + `package-lock.json` (Node.js)
  - `Gemfile` + `Gemfile.lock` (Ruby)

- **Document why each dependency exists**
  ```python
  # requirements.txt
  pandas==1.5.3        # Data manipulation
  apache-airflow==2.5.0  # Workflow orchestration
  pytest==7.2.1        # Testing framework
  ```

### Update Dependencies Safely
- **Check for breaking changes before updating**
  ```bash
  pip list --outdated
  pip install --upgrade package_name --dry-run
  ```

- **Test after updating dependencies**
  - Run full test suite
  - Check for compatibility issues

---

## 🚀 Deployment & DevOps

### Docker (if applicable)
- **Use `.dockerignore`** — Similar to `.gitignore`
  ```
  .git
  .gitignore
  .env
  __pycache__
  venv/
  .pytest_cache/
  *.pyc
  ```

- **Dockerfile best practices**
  - Use specific base image tags (not `latest`)
  - Pin RUN command package versions
  - Multi-stage builds for smaller images
  - `FROM python:3.11-slim` not `FROM python:latest`

### CI/CD Pipeline
- **Automate tests on every push**
  - GitHub Actions, GitLab CI, Jenkins, etc.
  - Run: tests, linting, type checking, security scans

- **Automate deployments**
  - Dev: Auto-deploy on main
  - Staging: Manual or schedule-based
  - Production: Manual approval required

### Monitoring & Logging
- **Add structured logging with rotation**
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

- **Suppress noisy third-party logs**
  ```python
  # Reduce verbosity from chatty libraries (psycopg2, urllib3, etc.)
  logging.getLogger("psycopg2").setLevel(logging.WARNING)
  logging.getLogger("urllib3").setLevel(logging.WARNING)
  ```
  - **Why?** Database drivers log internal protocol; clutters your application logs
  - **Result**: Only see YOUR events, not driver noise

- **Avoid emojis in log messages and scripts**
  - ❌ BAD: `logger.info("✅ Data loaded successfully")`
  - ✅ GOOD: `logger.info("[OK] Data loaded successfully")`
  - **Reason**: Emojis cause encoding issues on Windows terminals (charmap codec errors), CI/CD systems, and log aggregation pipelines that expect ASCII-only output. Use `[OK]`, `[ERROR]`, `[WARNING]` instead.

- **Plan for observability at scale** (future enhancement)
  - Current: Text logs to file ✅
  - Next: Structured JSON logging when adding ELK/Datadog (Week 3+)
  - **Why JSON?** Machine-parseable for log aggregation platforms; enables metrics extraction, anomaly detection, automated alerting
  - Tools: `python-json-logger`, Datadog Agent, ELK Stack, Splunk

- **Monitor in production**
  - Track errors, latency, resource usage
  - Set up alerts for failures
  - Log to centralized system (Datadog/ELK) for multi-service visibility

---

## 🔄 Code Review

### Before Merging
- **Create pull request (PR) with clear description**
  - What changed and why
  - Link to related issues
  - Screenshots (if UI)
  - Testing instructions

- **Request code review** — Never merge your own code
  - At least 1 other person reviews
  - Address all comments before merging

- **Ensure CI passes**
  - All tests pass
  - No linting errors
  - No security warnings

- **Squash or rebase** (optional)
  - Keep history clean: `git rebase -i origin/main`
  - Avoid "fix typo" commits in final history

---

## 🗂️ Project-Specific Habits

### Data Projects (SQL, dbt, Analytics)
- **Version control for SQL**
  - Store all DDL statements in `.sql` files
  - Version your data migrations
  - Use dbt for transformation logic

- **Test data quality**
  - Unit tests for transformations
  - Data profiling tests (nulls, duplicates, ranges)
  - Validation queries

- **Document data lineage**
  - Source → raw → staging → marts
  - Add comments in dbt models
  - Link to business glossary

---

## 🔍 SQL & dbt Best Practices

### SQL Execution Order vs Written Order

**Critical Concept:** SQL statements execute in a different order than they're written.

**Written Order:**
```sql
SELECT columns, aggregates
FROM table
WHERE conditions
GROUP BY key
HAVING aggregate_condition
ORDER BY sort_column
```

**Execution Order:**
```
1. FROM — Identify source table(s)
2. WHERE — Filter rows (aggregate functions NOT available here)
3. GROUP BY — Group remaining rows by key
4. SELECT — Calculate columns & aggregates (now aggregates exist)
5. HAVING — Filter groups (only use after GROUP BY)
6. ORDER BY — Sort results (can reference SELECT aliases)
```

**Practical Impact:**

| Clause | Available | NOT Available |
|--------|-----------|---------------|
| WHERE | Raw columns | Aggregates (SUM, COUNT), aliases |
| GROUP BY | Raw columns only | Aggregates, aliases |
| HAVING | Aggregates, GROUP BY columns | Other aliases |
| ORDER BY | SELECT outputs, aliases | Raw columns |

**Example — What NOT to do:**

```sql
-- ❌ FAILS: WHERE can't use aggregates
SELECT product_id, COUNT(*) AS sales_count
FROM sales
WHERE COUNT(*) > 5  -- ❌ COUNT(*) doesn't exist yet!
GROUP BY product_id

-- ✅ CORRECT: Use HAVING after GROUP BY
SELECT product_id, COUNT(*) AS sales_count
FROM sales
GROUP BY product_id
HAVING COUNT(*) > 5  -- ✅ Now COUNT(*) exists
```

---

### COUNT(*) vs COUNT(column_name)

**Key Difference:**

| Function | Counts | Skips NULLs? |
|----------|--------|---|
| `COUNT(*)` | All rows in group | No (counts everything) |
| `COUNT(column)` | Non-NULL values in column | Yes (skips NULLs) |
| `COUNT(DISTINCT column)` | Unique non-NULL values | Yes |

**Concrete Example with Data:**

Raw table:
```
sales_id  product_id  net_amount
1         101         50
2         101         NULL
3         101         100
4         102         200
5         102         NULL
```

Query results:
```sql
SELECT
    product_id,
    COUNT(*) AS count_all_rows,
    COUNT(net_amount) AS count_net_amount,
    COUNT(DISTINCT product_id) AS distinct_products
FROM sales
GROUP BY product_id
```

Results:
```
product_id  count_all_rows  count_net_amount  distinct_products
101         3               2                 1
102         2               1                 1
```

**When to use each:**
- `COUNT(*)` — "How many transactions per product?" (all rows matter)
- `COUNT(column)` — "How many customers have email on file?" (NULL = no email)
- `COUNT(DISTINCT key)` — "How many unique customers bought?" (duplicates irrelevant)

---

### JOIN Types: LEFT, INNER, RIGHT, FULL OUTER

**Pattern:**
```sql
FROM source_table st
[TYPE] JOIN dimension_table dt ON st.key = dt.key
```

| Type | Result | When Used |
|------|--------|-----------|
| **LEFT** | Keep all from LEFT table, add matches from RIGHT | Staging → Dimension (catch missing data) |
| **INNER** | Keep only matching rows from BOTH | Mart → Mart (assume upstream clean) |
| **RIGHT** | Keep all from RIGHT table, add matches from LEFT | Rare; flip tables and use LEFT instead |
| **FULL** | Keep all rows from BOTH; row appears if in either | Fact reconciliation, outer joins |

**Visual Example:**

```
Fact Table (LEFT):          Dimension Table (RIGHT):
product_id  revenue         product_id  name
101         $1000           101         Widget
102         $2000           103         Gadget
104         $500            (103 not in fact)
(104 not in dimension)
```

Results:
```
LEFT JOIN:           INNER JOIN:          FULL OUTER JOIN:
101 $1000 Widget     101 $1000 Widget     101 $1000 Widget
102 $2000 NULL       102 $2000 NULL       102 $2000 NULL
104 $500 NULL                             103 NULL Gadget
                                          104 $500 NULL
```

**In Analytics:**
- **Staging → Dimension (LEFT):** Catch data quality issues (NULL dimension columns = missing dimension record)
- **Mart → Mart (INNER):** Assume upstream cleaned; only analyze valid combinations

---

### CTE (WITH Clause) Pattern: Three-Layer Architecture

**Best Practice Structure:**

```sql
-- CTE 1: AGGREGATION
-- Raw data → grouped entity level
WITH entity_aggregates AS (
    SELECT
        entity_id,
        SUM(metric1) AS total_metric1,
        COUNT(*) AS transaction_count
    FROM raw_table
    WHERE is_valid = TRUE
    GROUP BY entity_id
)

-- CTE 2: CALCULATION
-- Aggregated data → add rankings/tiers
, entity_ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY total_metric1 DESC) AS rank,
        NTILE(4) OVER (ORDER BY total_metric1 DESC) AS quartile
    FROM entity_aggregates
)

-- Main SELECT: ENRICH + SEGMENT
-- Final output with business logic
SELECT
    er.entity_id,
    ed.entity_name,
    er.total_metric1,
    er.rank,
    CASE
        WHEN er.quartile = 1 THEN 'Premium'
        WHEN er.quartile = 2 THEN 'Standard'
        ELSE 'Basic'
    END AS customer_segment
FROM entity_ranked er
LEFT JOIN entity_dimension ed ON er.entity_id = ed.entity_id
```

**Why This Works:**
- **Layer 1:** Reduces 1M transactions → 10K entities (GROUP BY)
- **Layer 2:** Adds metrics on those 10K rows (window functions, no GROUP BY = keeps row count)
- **Layer 3:** Enriches with business context (JOINs dimensions, applies CASE logic)

Each layer has a clear purpose; easy to debug/reuse/modify.

---

### Window Functions vs Aggregate Functions

**Critical Difference:**

| Type | Behavior | ROW COUNT | Use Case |
|------|----------|-----------|----------|
| **Aggregate** (SUM, COUNT, AVG) | Reduces rows with GROUP BY | Fewer rows | Summary metrics |
| **Window** (ROW_NUMBER, NTILE, RANK) | Adds columns without GROUP BY | SAME rows | Rankings, tiers, running totals |

**Example:**

Data:
```
customer_id  lifetime_value
5            $5000
12           $4200
8            $3800
```

Aggregate approach (reduces rows):
```sql
SELECT COUNT(*) AS total_customers, AVG(lifetime_value) AS avg_value
FROM customers
GROUP BY region
-- Result: 1 row per region (5000 customers → 50 regions = 50 rows)
```

Window approach (keeps all rows):
```sql
SELECT
    customer_id,
    lifetime_value,
    ROW_NUMBER() OVER (ORDER BY lifetime_value DESC) AS rank,
    NTILE(4) OVER (ORDER BY lifetime_value DESC) AS quartile
FROM customers
-- Result: STILL 5000 rows, now with rank/quartile added
```

**When to use each:**
- **Aggregate:** "What's total revenue per product?" → One row per product
- **Window:** "Rank all products by revenue" → All products listed with ranks

---

### dbt Schema Configuration (Avoid Concatenation Issues)

**The Problem:**
```yaml
# profiles.yml
dev:
  schema: retail_analytics

# dbt_project.yml
models:
  marts:
    +schema: marts

# Result: retail_analytics + marts = retail_analytics_marts (CONCATENATION!)
```

**The Solution:**
Instead of using `+schema` in dbt_project.yml, use `{{ config() }}` blocks in individual models:

```sql
-- fct_product_performance.sql

{{ config(
    materialized='table'
) }}

WITH aggregates AS (
    ...
)

SELECT ...
```

**And in profiles.yml, keep schemas separate:**

```yaml
dev:
  schema: retail_analytics_staging  # Base for staging models

prod:
  schema: retail_analytics_marts    # Different output for prod
```

**Why This Avoids Concatenation:**
- `{{ config() }}` overrides per-model, no concatenation
- profiles.yml determines WHERE (which dataset) models go
- dbt doesn't try to concatenate base + project settings
- One source of truth per model

**If You MUST Use +schema, Be Explicit:**

```yaml
# dbt_project.yml
models:
  staging:
    +schema: stg_staging    # Explicitly set full schema name
  marts:
    +schema: retail_marts   # No "retail_" prefix in profile
```

With profile:
```yaml
dev:
  schema: ""  # Empty! Let dbt_project.yml handle it
```

Result: No concatenation, explicit schema names.

---

### schema.yml Documentation: One Source of Truth

**Best Practice:**
- Model descriptions go in **schema.yml** (not config() blocks)
- Generates dbt documentation site (visible in `dbt docs serve`)
- Single place to update; feeds documentation + validation

**Structure:**

```yaml
version: 2

models:
  - name: fct_customer_lifetime_value
    description: "Customer segmentation answering: who are our best customers?"
    columns:
      - name: customer_id
        description: "Unique customer identifier"
        data_tests:
          - unique
          - not_null
      - name: lifetime_value
        description: "Total revenue (net_amount) from non-return purchases"
      - name: customer_segment
        description: "Business segment: At Risk, VIP Loyal, High Value, Medium Value, Low Value"
```

**View with:**
```bash
dbt docs generate  # Creates documentation site
dbt docs serve     # Open http://localhost:8000 (shows lineage, descriptions, tests)
```

---

### SELECT * vs SELECT Specific Columns

**When to Use SELECT *:**

```sql
, customer_ranked AS (
    SELECT
        *,  -- ← All 6 columns from CTE 1
        ROW_NUMBER() OVER (...) AS rank,  -- Add 2 new columns
        NTILE(4) OVER (...) AS quartile
    FROM customer_aggregates
)
```

**When to use SELECT specific:**

```sql
, customer_filtered AS (
    SELECT
        customer_id,
        lifetime_value,
        days_since_purchase
    FROM customer_ranked
)
-- Drop rank, quartile if not needed downstream (performance + clarity)
```

**Decision Logic:**

| Situation | Approach | Why |
|-----------|----------|-----|
| Adding columns to all from previous CTE | SELECT * | Flexibility; simpler code |
| Dropping many columns | SELECT specific | Reduce data passed; clearer intent |
| Final output in mart | SELECT specific | Explicit; downstream knows exact columns |
| Intermediate CTE | SELECT * if adding, SELECT specific if filtering | Pragmatic |

---

### CTE Aliasing (Optional but Recommended)

**Standard (without alias):**
```sql
FROM customer_ranked
```

**With Alias (recommended for multi-CTE queries):**
```sql
FROM customer_ranked cr
LEFT JOIN dimension_table dt ON cr.customer_id = dt.customer_id
```

**When Alias Helps:**
- Multiple JOINs (clarifies which table columns come from)
- Long table names (saves typing)
- CTEs with similar names (distinguishes context)

**Production Pattern:**
```sql
FROM customer_ranked cr           -- "cr" = customer ranked
LEFT JOIN stg_customer_clean sc   -- "sc" = source customer
LEFT JOIN stg_date_clean dc       -- "dc" = dimension customer
ON cr.customer_id = sc.customer_id
```

Aliases make code scannable; readers immediately know which columns belong to which table.

---

### Configuration Block Best Practices

**Minimal Config (Recommended):**

```sql
{{ config(
    materialized='table'
) }}
```

Only set what differs from dbt_project.yml defaults. Makes files lighter.

**Common Configs:**

```sql
-- Table (reusable downstream)
{{ config(materialized='table') }}

-- View (lightweight, always latest)
{{ config(materialized='view') }}

-- Ephemeral (only exists in compilation, not in database)
{{ config(materialized='ephemeral') }}
```

**NOT needed in config():**
- ❌ `schema` (use profiles.yml + dbt_project.yml logic)
- ❌ `description` (use schema.yml)
- ❌ `tags` (define in schema.yml)

---

### Data Quality Tests in schema.yml

```yaml
models:
  - name: fct_product_performance
    columns:
      - name: product_id
        description: "Unique product identifier"
        data_tests:
          - unique      # No duplicates
          - not_null    # Can't be NULL
      - name: total_revenue
        description: "Sum of net sales"
        data_tests:
          - accepted_values:  # Only positive values
              values: [0, 1]  # Nonsense example for illustration
          - dbt_utils.expression_is_true:  # >= 0
              expression: "> 0"
```

**Built-in Tests (generic):**
- `unique` — No duplicates
- `not_null` — No NULLs
- `accepted_values` — Column values in list
- `relationships` — Foreign key exists in other table

**Run tests:**
```bash
dbt test  # All tests
dbt test -s fct_product_performance  # Single model
```

---

### ML/AI Projects
- **Track training data versions**
  - Which dataset was used for training?
  - Random seed for reproducibility
  - Data splits documented

- **Version models**
  - Store models with metadata (date, performance, hyperparams)
  - Use MLflow, DVC, or similar

- **Document model assumptions**
  - Features used
  - Training period
  - Performance metrics
  - Known limitations

### Python Projects
- **Use type hints everywhere**
  ```python
  from typing import Optional, List
  def process(data: List[dict], limit: Optional[int] = None) -> dict:
      ...
  ```

- **Use context managers for resource management**
  ```python
  # ❌ BAD: Manual resource handling
  connection = create_connection()
  try:
      do_work(connection)
  finally:
      connection.close()

  # ✅ GOOD: Context manager ensures cleanup even on exceptions
  with create_connection() as connection:
      do_work(connection)

  # Implement context managers in classes:
  class DatabaseGenerator:
      def __enter__(self):
          self.connect()
          return self

      def __exit__(self, exc_type, exc_val, exc_tb):
          self.disconnect()
          return False  # Don't suppress exceptions
  ```
  - **Benefit**: Guarantees resource cleanup (files, DB connections, locks, etc.)
  - **Example**: `with SyntheticDataGenerator(db_config) as gen: gen.generate_all()`

- **Use custom exceptions for domain errors**
  ```python
  class DataGenerationError(Exception):
      """Raised when synthetic data generation fails."""
      pass

  # Usage:
  try:
      generate_data()
  except DataGenerationError as e:
      logger.error(f"Data generation failed: {e}")
      raise
  ```
  - **Benefit**: Clearer error handling upstream; domains errors distinct from system errors

- **Use dataclasses or Pydantic for data models**
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

- All tests pass locally and in CI
- Code reviewed by at least one peer
- No hardcoded secrets
- `.env.example` exists with template
- `.gitignore` excludes all sensitive files
- README is complete and accurate
- CHANGELOG updated
- Docstrings added to all functions
- Architecture diagram up-to-date
- Performance benchmarked (if applicable)
- Error handling implemented (no bare `except:`)
- Logging added (at DEBUG, INFO, ERROR levels)
- Dependencies documented in requirements file
- Commit history is clean (meaningful messages, atomic commits)
- Database migrations tested (if applicable)
- No TODO comments left in code (or tracked in issues)

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

## 🚀 MVP (Minimum Viable Product) Philosophy

**Definition:** Release the smallest feature set that solves the core problem and creates value immediately.

**Core Principles:**
- ✅ Works end-to-end (even if not optimized)
- ✅ Solves the real problem
- ✅ Measurable success criteria
- ✅ Fast feedback loop
- ❌ Don't over-engineer "just in case"

**In Data Engineering Context:**
```
MVP: Generate 1M transactions + load to PostgreSQL with basic quality checks
❌ NOT MVP: Real-time pipelines, distributed processing, Kubernetes, etc.
```

**When to Optimize Beyond MVP:**
- **Measure first**: Identify the actual bottleneck (don't guess)
- **Prove problem**: Show that current approach is too slow/expensive
- **Simple → complex**: executemany() → batch loading → COPY FROM → streaming

---

## 🗄️ Database Operations: Scale-Appropriate Approaches

### **Data Loading: Three Tiers**

| Approach | Records | Speed | When to Use | Complexity |
|----------|---------|-------|-------------|------------|
| **executemany()** | < 1M | ~10k rows/sec | MVP, development, error handling needed | ⭐ |
| **Batch + COPY** | 1M-100M | ~100k rows/sec | Production data loads, ETL pipelines | ⭐⭐ |
| **Streaming (Kafka)** | 100M+ | Continuous | Real-time ingestion, 24/7 pipelines | ⭐⭐⭐ |

### **Analogy: Moving Boxes**

```
executemany():  🚶 Walk through door one box at a time (show ticket each time)
COPY FROM:      🚚 Back truck to dock, dump all boxes at once
Kafka Stream:   🏗️  Conveyor belt (boxes arrive continuously)
```

### **COPY FROM vs executemany()** (PostgreSQL Example)

```python
# ❌ Current: Individual INSERT statements (MVP appropriate)
insert_query = "INSERT INTO sales (...) VALUES (%s, %s, ...)"
cursor.executemany(insert_query, records_list)  # Each row: parse → bind → execute
# Speed: ~30-50 sec for 1M records

# ✅ Future: PostgreSQL bulk load (when scaling)
import io
csv_buffer = io.StringIO()
for record in records:
    csv_buffer.write(f"{record[0]},{record[1]},...\n")
csv_buffer.seek(0)
cursor.copy_from(csv_buffer, 'sales', columns=['col1', 'col2', ...])
# Speed: ~3-5 sec for 1M records (10x faster!)
```

**Why COPY is faster:**
- Skips SQL parsing overhead
- Direct data format (binary or CSV)
- Single index update pass
- Optimized for sequential writes

**When to upgrade from executemany to COPY:**
- Volume > 5M records
- Measured latency > acceptable threshold
- Cost/time clearly justifies refactoring

---

## ☁️ Cloud Infrastructure & Credentials (GCP, BigQuery, GCS)

### Service Account & Authentication Setup

- **Create GCP Service Account (never use personal account)**
  ```
  GCP Console → Service Accounts → Create Service Account
  - Name: etl-pipeline (descriptive, lowercase)
  - Grant roles: BigQuery Admin, Storage Admin
  - Create JSON key file (download & store securely)
  ```
  - **Why separate account?** Audit trail, revoke access without touching personal account, CI/CD-safe
  - **Key file location:** Store in project root: `./gcp-key.json` (add to `.gitignore`)
  - **Never commit key files** — They're authentication tokens equivalent to passwords

- **Store GCP credentials in `.env`**
  ```bash
  # .env (never commit this)
  GCP_PROJECT_ID=lcv-retail-analytics-dw
  GCP_KEY_PATH=./lcv-gcp-key.json
  GCS_BUCKET=lcv-retail-analytics-dw
  BIGQUERY_DATASET=retail_analytics_raw
  ```

  ```bash
  # .env.template (safe to commit, shows structure)
  GCP_PROJECT_ID=your-project-id
  GCP_KEY_PATH=path/to/service-account-key.json
  GCS_BUCKET=your-bucket-name
  BIGQUERY_DATASET=your_dataset_name
  ```

- **Authenticate in Python with service account**
  ```python
  from google.oauth2 import service_account
  from google.cloud import storage
  import os
  from dotenv import load_dotenv

  load_dotenv()

  # Load service account key
  key_path = os.getenv("GCP_KEY_PATH")
  credentials = service_account.Credentials.from_service_account_file(
      key_path,
      scopes=["https://www.googleapis.com/auth/cloud-platform"]
  )

  # Initialize GCS client
  storage_client = storage.Client(credentials=credentials)
  bucket = storage_client.bucket(os.getenv("GCS_BUCKET"))
  ```

### Google Cloud Storage (GCS) Best Practices

- **Organize with date-partitioned folders**
  ```
  gs://bucket-name/
  ├── 2026-02-25/
  │   ├── dim_date.parquet
  │   ├── dim_store.parquet
  │   └── fact_sales.parquet
  ├── 2026-02-26/
  │   ├── dim_date.parquet
  │   ├── dim_store.parquet
  │   └── fact_sales.parquet
  ```
  - **Why?** YYYY-MM-DD format makes archival, versioning, and troubleshooting easy
  - Enables BigQuery partition pruning (scan only needed dates)
  - Simple data lineage: "which files loaded yesterday?"

- **Use Parquet format with Snappy compression**
  ```python
  df.to_parquet(
      path,
      engine="pyarrow",
      compression="snappy",  # Best compression/speed tradeoff
      coerce_timestamps="us"  # Ensure timestamp compatibility
  )
  ```
  - **Parquet benefits:** Columnar (scan only needed cols), 60-80% compression, schema enforcement
  - **Snappy tradeoff:** ~1.5-2x faster than gzip, ~10-15% larger; good for ETL pipelines
  - **Use gzip instead if:** Storage cost >> compute cost (archive data)

- **Validate file uploads**
  ```python
  blob = bucket.blob(f"{date}/table.parquet")
  blob.upload_from_filename(local_path)

  # Verify: compare file sizes
  local_size = os.path.getsize(local_path)
  gcs_size = blob.size
  assert local_size == gcs_size, f"Upload mismatch: {local_size} != {gcs_size}"
  ```

### BigQuery Best Practices

- **Create datasets with appropriate locations**
  ```python
  from google.cloud import bigquery

  client = bigquery.Client(credentials=credentials)
  dataset_id = os.getenv("BIGQUERY_DATASET")
  dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
  dataset.location = "US"  # Multi-region for availability
  dataset = client.create_dataset(dataset, exists_ok=True)
  ```
  - **Location:** "US" (multi-region) for high availability, "us-east1" if cost is critical
  - **Separate datasets:** `raw` (GCS import), `staging` (dbt), `marts` (analytics)

- **Use External Tables for Parquet in GCS (cheap exploration)**
  ```sql
  CREATE OR REPLACE EXTERNAL TABLE raw.fact_sales
  OPTIONS (
    format = 'PARQUET',
    uris = ['gs://bucket-name/2026-02-26/*.parquet'],
    hive_partition_uri_prefix = 'gs://bucket-name/',
    require_partition_filter = false
  );
  ```
  - **External table scanning:** $7.25/TB (same as regular query)
  - **Native table copy:** $0.023/GB first 100GB/month (cheaper for frequent access)
  - **Strategy:** Explore with external → copy to native when stable

- **Load GCS Parquet into native BigQuery table**
  ```sql
  CREATE OR REPLACE TABLE raw.fact_sales AS
  SELECT * FROM `project.raw.fact_sales_external`;
  ```
  - Copies data into BigQuery's columnar storage
  - Enables clustering, partitioning, incremental loads
  - ~3-5x faster than external tables for repeated queries

- **Always partition & cluster large tables**
  ```sql
  CREATE OR REPLACE TABLE marts.fact_sales (
    sale_id INT64,
    sale_date DATE,
    store_id INT64,
    amount NUMERIC(10, 2)
  )
  PARTITION BY sale_date
  CLUSTER BY store_id
  AS SELECT * FROM raw.fact_sales;
  ```
  - **Partitioning:** Prune entire date ranges (10-100x scan reduction)
  - **Clustering:** Sort within partitions (column filtering speedup)
  - **Cost impact:** Can reduce query costs 50-80% on large tables

### Secrets & Credentials Patterns

- **NEVER hardcode secrets**
  ```python
  # ❌ BAD
  key_path = "/absolute/path/to/key.json"
  password = "super_secret_123"

  # ✅ GOOD
  key_path = os.getenv("GCP_KEY_PATH")
  password = os.getenv("POSTGRES_PASSWORD")
  ```

- **Rotate credentials periodically**
  - Service account keys: 90-day rotation (automatic alerts in GCP)
  - Database passwords: Every 6 months minimum
  - Check git history: `git log -p | grep -i "password\|key\|secret"` (should be empty)

- **Use `.env` template pattern**
  ```bash
  # .env.template (commit this)
  POSTGRES_HOST=localhost
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=your_password_here
  GCP_KEY_PATH=./path/to/key.json

  # .env (never commit)
  POSTGRES_HOST=localhost
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=malezya2652%&
  GCP_KEY_PATH=./lcv-gcp-key.json
  ```

- **Validate credentials at startup (Fail-Fast)**
  ```python
  def validate_gcp_credentials():
      """Validate GCP service account key exists and is readable"""
      key_path = os.getenv("GCP_KEY_PATH")
      if not os.path.exists(key_path):
          raise FileNotFoundError(f"GCP key not found: {key_path}")
      try:
          from google.oauth2 import service_account
          service_account.Credentials.from_service_account_file(key_path)
      except Exception as e:
          raise ValueError(f"Invalid GCP key: {e}")
      logger.info(f"✓ GCP credentials validated: {key_path}")

  # Call at application startup
  validate_gcp_credentials()
  ```

---

## 🔄 ETL Pipeline Patterns (Extract, Transform, Load)

- **Use context managers for resource cleanup**
  ```python
  class DataExtractor:
      def __init__(self, db_config, gcs_credentials):
          self.db_config = db_config
          self.gcs_credentials = gcs_credentials
          self.db_conn = None
          self.gcs_client = None

      def __enter__(self):
          self.db_conn = create_connection(self.db_config)
          self.gcs_client = storage.Client(credentials=self.gcs_credentials)
          return self

      def __exit__(self, exc_type, exc_val, exc_tb):
          """Cleanup: close connections regardless of success/failure"""
          if self.db_conn:
              self.db_conn.close()
          return False  # Don't suppress exceptions

  # Usage
  with DataExtractor(config, creds) as extractor:
      data = extractor.extract_table("sales")
  ```
  - **Why?** Guarantees cleanup even if exception occurs (prevents resource leaks)

- **Implement idempotent pipelines**
  ```python
  # ✅ If pipeline crashes halfway, re-run produces same result
  # Upload with date-based path (skip if file exists)
  gcs_path = f"gs://bucket/{YYYY-MM-DD}/table.parquet"
  if not blob_exists(gcs_path):
      upload_to_gcs(data, gcs_path)
  else:
      logger.info(f"Skipping {gcs_path} (already uploaded)")
  ```

- [x] **Add timestamps & exit codes for monitoring**
  ```python
  import sys
  from datetime import datetime

  def main():
      start_time = datetime.now()
      try:
          logger.info("Pipeline started")
          extract_and_load_data()
          elapsed = (datetime.now() - start_time).total_seconds()
          logger.info(f"✓ Pipeline completed in {elapsed:.2f} seconds")
          sys.exit(0)  # Success
      except Exception as e:
          logger.error(f"✗ Pipeline failed: {e}", exc_info=True)
          sys.exit(1)  # Failure
  ```
  - **Exit codes:** 0 = success, 1 = fatal error (CI/CD can detect failures)
  - **Elapsed time:** Monitor performance trends

- [x] **Log extraction metadata**
  ```python
  logger.info(f"[OK] Extracted {record_count} records from {table_name}")
  logger.info(f"[OK] Saved {table_name}.parquet ({file_size_mb:.2f} MB)")
  logger.info(f"[OK] Uploaded to gs://{bucket}/{date}/{table_name}.parquet")
  ```
  - **Why?** Audit trail, debugging, monitoring pipeline health

---

## 📊 BigQuery Loading Patterns (GCS → BigQuery)

### Comparing Three Approaches

When loading Parquet files from GCS into BigQuery, you have three options. Here's the comparison:

| Approach | Method | Pros | Cons | Best For |
|----------|--------|------|------|----------|
| **Python Script** | `bigquery.Client.load_table_from_uri()` | ✅ Automated, version controlled, error handling, extensible, schedulable | Requires library | **Production pipelines** |
| **bq CLI** | `bq load --source_format=PARQUET` | ✅ Simple one-liners, easy testing | ❌ Manual per-table, no version control, hard to scale | Ad-hoc exploration |
| **External Tables** | `CREATE EXTERNAL TABLE ... OPTIONS(format='PARQUET')` | ✅ Fast preview, minimal setup | ❌ Slow queries, repeated GCS scans, not production-ready | Quick data exploration |

**Winner: Python Script** 🏆

### Implementation: Python Script (Recommended)

**Why Python = Production Standard:**
```
1. Extract (Python) → GCS Parquet files
2. Load (Python) → BigQuery native tables ← YOU ARE HERE
3. Transform (dbt) → Staging/mart models
4. Schedule → Airflow/Cloud Scheduler runs all three daily
```

- ✅ **Automated** — Single command loads all tables
- ✅ **Version controlled** — Code in git, reproducible
- ✅ **Error handling** — Fail-fast, comprehensive logging
- ✅ **Orchestration-ready** — Easy to schedule with Airflow, Cloud Scheduler, cron
- ✅ **Scalable** — Same pattern works for 5 tables or 500
- ✅ **Maintainable** — Team can understand & modify code

```python
# Example: Load all Parquet files from GCS to BigQuery
from google.cloud import bigquery
from google.oauth2 import service_account

class GCSToBigQueryLoader:
    def __init__(self, project_id, key_path, bucket, dataset):
        credentials = service_account.Credentials.from_service_account_file(key_path)
        self.bq_client = bigquery.Client(project=project_id, credentials=credentials)
        self.project_id = project_id
        self.dataset = dataset
        self.bucket = bucket

    def load_parquet_to_bigquery(self, gcs_uri: str, table_name: str) -> None:
        """Load single Parquet file from GCS to BigQuery native table."""
        table_id = f"{self.project_id}.{self.dataset}.{table_name}"

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            autodetect=True,  # Auto-infer schema from Parquet
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrite
        )

        load_job = self.bq_client.load_table_from_uri(
            gcs_uri, table_id, job_config=job_config
        )
        load_job.result()  # Wait for completion

        table = self.bq_client.get_table(table_id)
        logger.info(f"[OK] Loaded {table.num_rows} rows into {table_id}")

    def load_all_tables(self, date: str) -> None:
        """Load all Parquet files from a date into BigQuery."""
        files = self.list_parquet_files(date)  # e.g., ["dim_store.parquet", ...]

        for file_name in files:
            table_name = file_name.replace(".parquet", "")
            gcs_uri = f"gs://{self.bucket}/{date}/{file_name}"
            self.load_parquet_to_bigquery(gcs_uri, table_name)

# Usage
with GCSToBigQueryLoader(project_id, key_path, bucket, dataset) as loader:
    loader.load_all_tables("2026-02-27")  # Loads all tables with one call
```

**Key features:**
- ✅ Schema auto-detection from Parquet
- ✅ `WRITE_TRUNCATE` mode (idempotent: safe to re-run)
- ✅ Error handling + logging
- ✅ Works with context managers (automatic cleanup)

### When to Use Each Approach

**Use Python Script if:**
- ✅ You have 2+ tables to load
- ✅ You want automated, schedulable pipelines
- ✅ You need error handling and logging
- ✅ You value version control & team reproducibility

**Use bq CLI if:**
- ✅ One-off load (manual, ad-hoc)
- ✅ Testing a single table
- ✅ You prefer shell scripts

**Use External Tables if:**
- ✅ You want to explore data before copying
- ✅ Cost is not a concern (repeated GCS scans)
- ✅ Data changes frequently and you don't want to copy

### BigQuery Load Configuration Best Practices

```python
job_config = bigquery.LoadJobConfig(
    # Schema handling
    source_format=bigquery.SourceFormat.PARQUET,
    autodetect=True,  # Let BigQuery infer schema from file
    # OR specify schema explicitly for stricter validation

    # Data deduplication
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    # Options: WRITE_TRUNCATE (overwrite), WRITE_APPEND (insert), WRITE_EMPTY (fail if exists)

    # Timestamps
    time_partitioning=bigquery.TimePartitioning(type_="DAY", field="date_column"),
    # Optional: partition large tables by date for faster queries

    # Clustering for performance
    clustering_fields=["store_id", "product_id"],
    # Optional: co-locate related rows for query speedup
)

load_job = self.bq_client.load_table_from_uri(gcs_uri, table_id, job_config=job_config)
load_job.result()  # Wait for completion with .result()
```

**Common configurations:**
- `autodetect=True` — Let BigQuery infer schema (fast setup, less validation)
- `autodetect=False` + explicit schema — Strict validation (catches schema issues early)
- `WRITE_TRUNCATE` — Idempotent (safe for nightly re-runs)
- `time_partitioning` — For large tables (fact tables with dates)
- `clustering_fields` — Co-locate rows for query performance

---

## 🔄 dbt (Data Build Tool) Best Practices

### What dbt Accomplishes: Before and After

**The Data Pipeline Without dbt:**
```
PostgreSQL (OLTP)
    ↓ [Manual Python script: postgres_to_gcs.py]
GCS Parquet Files (~27 MB)
    ↓ [Manual Python script: gcs_to_bigquery.py]
BigQuery Raw Dataset (1.01M records, as-is)
    ↓ [???]
    ↓ Ad-hoc SQL scripts scattered across notebooks, email attachments, local files?
    ↓ No version control, no tests, no documentation
    ↓ "I think this is the sales table... someone updated it last month?"
Analytics (Hope for the best 🤞)
```

**The Data Pipeline With dbt:**
```
PostgreSQL (OLTP)
    ↓ [postgres_to_gcs.py: Extract to Parquet]
GCS Parquet Files
    ↓ [gcs_to_bigquery.py: Load to BigQuery raw]
BigQuery Raw Dataset
    ↓ [dbt run: Execute models in version control]
    ├─ Staging models (stg_sales_clean, stg_stores_clean, ...)
    │  • Null validation, deduplication, derived fields
    │  • Automatically tested with dbt tests
    │  • Documented with descriptions
    ├─ Mart models (fct_sales, dim_date, ...)
    │  • Clean analytics layer
    │  • Performance-optimized (Tables with clustering)
    │  • Tested for data quality
    └─ Full lineage tracked (know where each column came from)
Analytics (Confident in data quality ✅)
```

#### Analogy 1: Restaurant Kitchen

**Without dbt:**
- Receipt comes in (Parquet from GCS)
- Multiple chefs write ingredients on napkins (ad-hoc SQL)
- No recipe documented
- Each chef does plating differently
- Quality varies day to day
- Health inspector comes: "What's in this dish?" Nobody knows.

**With dbt:**
- Receipt comes in (Parquet from GCS)
- **Head chef** (dbt_project.yml) defines the recipe (transformation steps)
- Each **station** (staging/marts models) has a specific job: prep, cook, plate
- **Quality control** (dbt tests): weight ingredients, check temps, verify plating
- **Documentation** (columns/descriptions): know what goes in every dish
- **Version control** (git): any recipe change is tracked, can roll back
- Health inspector comes: "This is exactly what it says on the menu, every time."

#### Analogy 2: Software Version Control for Data

**Without dbt:**
- SQL transformations are like code before Git
- No version history: Who changed what and when?
- Nobody knows if this query is deprecated or production-critical
- Manual copy-paste errors
- Testing is: "Run it and hope"

**With dbt:**
- SQL in `models/` are just `.sql` files: **Version control with git**
- Each model is in git (commit history, blame attribution)
- **Dependent models are auto-updated**: Change one model, downstream models recompute
- **Tests prevent regressions**: dbt tests catch breaking changes
- **Reproducibility**: Same git commit = same transformation output, always

#### Analogy 3: Construction Blueprint

**Without dbt:**
- Raw materials arrive (Parquet)
- Builders improvise with no blueprint
- House looks different each time
- When foundation cracks, nobody knows why
- Adding a room requires rebuilding everything

**With dbt:**
- Raw materials arrive (Parquet)
- **Blueprint** (dbt_project.yml + models): Clear plan
- **Staging** (Framing + electrical): Raw materials → standardized, validated intermediate
- **Marts** (Finished walls + flooring): Staging → beautiful, ready for occupants (analysts)
- **Quality inspection** (dbt tests): Every room meets code
- **Permits** (git commits): Every change documented
- **Maintenance** (SQL updates): Easy to rebuild a room without affecting others

---

### Why dbt is Essential with Real Data (Not Just Synthetic)

**Our Project Today: Synthetic Data**
- ✅ Clean by design (no missing values, perfect format)
- ✅ No duplicates (generated uniqueness built-in)
- ✅ No schema surprises (controlled data generation)
- ✅ dbt is "nice to have" (testing validates the test data)

**Real-World Data Tomorrow:**
- ❌ Missing values in customer names (null handling required)
- ❌ Duplicate transaction IDs from system bugs (deduplication with `QUALIFY ROW_NUMBER`)
- ❌ Negative prices from refunds (validation: `CASE WHEN price < 0 THEN NULL`)
- ❌ Future dates from data entry errors (temporal validation)
- ❌ Orphaned foreign keys (customers deleted, sales remain)
- ❌ Schema changes mid-year (new columns appear without warning)

**Why dbt becomes critical with real data:**

| Problem | Without dbt | With dbt |
|---------|------------|---------|
| **Duplicate transactions** | Run SQL, update manually, hope you caught all cases | `dbt run` auto-deduplicates, `dbt test` verifies |
| **Missing customer names** | Check Excel, update in BigQuery, lose audit trail | `stg_customer.sql` handles nulls, git shows when logic changed |
| **Negative prices** | Someone notices wrong revenue report in week 4 | `dbt test` catches in hour 1: "price must be > 0" |
| **New phone column appears** | Where do we add this? Which models? | Add to `stg_customer.sql`, `dbt run` updates all downstream |
| **Why does Q3 Revenue look wrong?** | "Uhhh, either the load failed or we changed something?" | Git: commit history of every transformation change |
| **Can we trust this number?** | "I ran this query last month, probably?" | `dbt test` proves it: unique transactions, no nulls, data quality assertions |

**Real Data Issues dbt Solves:**
1. **Testing** — Catch data quality issues before reporting (not after)
2. **Lineage** — See exactly which raw columns → which analytics columns
3. **Documentation** — Why did we null out certain prices? (Commit message + `.sql` comments)
4. **Reproducibility** — Same data, same dbt version = identical results
5. **Maintenance** — Update cleaning logic in one place (stg_sales_clean.sql), all dependent models rebuild
6. **Debugging** — Data looks wrong? Check git history, see what changed

**Use Case: A Bug in Real Data**

Week 6, an analyst reports: *"Revenue in March looks 20% high."*

**Without dbt:**
- "Let me check... not sure which query that was."
- Manual investigation: open 10 SQL files, check who ran them
- Uncertainty: "Did we dedup? Did we include refunds? Which refund logic?"
- Risk: Fix it wrong, break something else

**With dbt:**
```bash
# With dbt:
dbt run --select fct_sales+  # Recompute fact_sales and all upstream
dbt test --select fct_sales+ # Validate (if data looks good, dbt tests still pass)
git log models/marts/fct_sales.sql  # See what changed
# Found it: Commit from Feb 27 added discount logic
# Revert if needed: git revert <commit>
# dbt run again to recompute with old logic
```

Your team knows:
- ✅ Exactly what transformation logic was used
- ✅ When it changed
- ✅ Who changed it (commit author)
- ✅ What it looked like before (git history)
- ✅ Immediate reproduction (dbt run)

---

### Project Initialization: Manual vs `dbt init`

**Scenario**: When should you use `dbt init` vs manual setup?

#### Option 1: Use `dbt init` (Quick Start)
- Good for: Prototypes, single-developer projects, learning dbt
- Pros: Automatic scaffolding, standard directory structure
- Cons: Can have CLI version issues, harder to customize
```bash
dbt init my_project
cd my_project
dbt run
```

#### Option 2: Manual Setup (Recommended for Teams)
- Good for: Production projects, teams, strict version control
- Pros: Full control, reproducible configuration, no CLI quirks
- Cons: Slightly more setup work
- **Why it's better**: dbt projects are just YAML + SQL files. Manual setup ensures:
  1. Everything is version-controlled
  2. Onboarding is explicit (no "magic" from CLI)
  3. Configuration is team-standardized
  4. Works consistently across environments

**Pitfall**: `dbt init` can fail with Python version compatibility issues (e.g., dbt-core 1.7.0 on Python 3.10: `KeyboardInterrupt` in dataclasses module). Manual setup avoids this entirely.

### dbt Project Structure (Manual Setup)

Create this structure in your project:

```
src/etl/dbt_project/
├── dbt_project.yml           # Project config (required)
├── models/
│   ├── staging/              # Raw data → cleaning layer
│   │   ├── stg_sales_clean.sql
│   │   ├── stg_stores_clean.sql
│   │   └── ... (other staging models)
│   └── marts/                # Staging → analytics layer
│       ├── fct_sales.sql
│       └── dim_*.sql
├── tests/                    # YAML + SQL tests (data quality)
│   ├── generic/
│   └── data_quality.yml
├── macros/                   # Reusable dbt code
├── seeds/                    # CSV lookup tables
├── analysis/                 # Ad-hoc analysis files
└── README.md                 # Project documentation

~/.dbt/
└── profiles.yml              # Database connections (user-level, shared across projects)
```

### dbt_project.yml Configuration

```yaml
# dbt_project.yml
name: 'lcv_retail_analytics'
version: '1.0.0'
config-version: 2

profile: 'lcv_retail_analytics'  # Must match profiles.yml profile name

model-paths: ["models"]
analysis-paths: ["analysis"]
test-paths: ["tests"]
data-paths: ["seeds"]
macro-paths: ["macros"]

vars:
  raw_dataset: "retail_analytics_raw"
  staging_dataset: "retail_analytics_staging"
  marts_dataset: "retail_analytics_marts"

models:
  lcv_retail_analytics:
    staging:
      materialized: view           # Create as views (cheap, fast)
      columns:
        # Optional: Define column-level docs here
    marts:
      materialized: table          # Final tables (optimized for queries)
      indexes:
        - columns: ['date_key']    # Performance: skip common filters
          unique: false
```

**Key principles:**
- `staging` layer → Views (cheap, no storage overhead)
- `marts` layer → Tables (for reporting, optimized)
- Large fact tables (>1M rows) → Materialized table, not view
- Use `vars:` for dataset names (easy to switch dev→prod)

### profiles.yml Configuration

```yaml
# ~/.dbt/profiles.yml
lcv_retail_analytics:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account-json
      project: "lcv-retail-analytics-dw"
      dataset: "retail_analytics_staging"  # Dev dataset for testing
      threads: 4                           # Parallel dbt run threads
      timeout_seconds: 300
      location: "US"
      keyfile: "/path/to/lcv-gcp-key.json"
    prod:
      type: bigquery
      method: service-account-json
      project: "lcv-retail-analytics-dw"
      dataset: "retail_analytics_marts"    # Prod dataset for analytics
      threads: 8
      timeout_seconds: 300
      location: "US"
      keyfile: "/path/to/lcv-gcp-key.json"
```

**Security note**: Keep `.dbt/profiles.yml` in `~/.dbt/` (home directory), NOT in version control. Reference the key file path, don't embed credentials.

### Model Organization Strategy

#### Staging Layer (Cleaning & Validation)

```sql
-- stg_sales_clean.sql
-- Purpose: Clean fact_sales from raw, add validation, derive fields
-- Materialization: Table (1M+ rows = performance)

SELECT
    sale_id,
    store_id,
    product_id,
    CASE WHEN quantity <= 0 THEN NULL ELSE quantity END AS quantity,
    CASE WHEN unit_price <= 0 THEN NULL ELSE unit_price END AS unit_price,
    ROUND(quantity * unit_price, 2) AS total_amount,
    profit,
    updated_at,
FROM `{{ var('raw_dataset') }}.fact_sales`
WHERE sale_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY sale_id ORDER BY updated_at DESC) = 1
```

**Staging layer validation patterns:**
- Null checks: `CASE WHEN column IS NULL THEN NULL ELSE column END`
- Positive values: `CASE WHEN amount <= 0 THEN NULL ELSE amount END`
- Deduplication: `QUALIFY ROW_NUMBER() OVER (...) = 1`
- Text standardization: `UPPER(column)`, `TRIM(column)`
- Derived fields: Calculate common metrics (profit, total_amount, etc.)

#### Marts Layer (Analytics Ready)

```sql
-- fct_sales.sql
-- Purpose: Final fact table for reporting (optimized for queries)
-- Materialization: Table
-- Partitioning: By date (monthly)

SELECT
    stg.sale_id,
    stg.store_id,
    stg.product_id,
    stg.quantity,
    stg.total_amount,
    stg.profit,
    DATE_TRUNC(stg.date, MONTH) AS month_partition,
FROM {{ ref('stg_sales_clean') }} stg
WHERE stg.sale_id IS NOT NULL
```

**Key dbt functions:**
- `{{ ref('table_name') }}` — References another model (creates lineage)
- `{{ var('variable_name') }}` — Uses dbt variables (defined in dbt_project.yml)
- `{{ execute }}` — Executes Python within SQL (advanced)

### Materialization Strategy

| Layer | Type | When | Example |
|-------|------|------|---------|
| Staging | VIEW | Always <1M rows, frequently updated | Clean raw tables |
| Marts | TABLE | >1M rows, used for reporting | Final fact tables |
| Intermediate | EPHEMERAL | Never queried directly | Re-used calculations |

```yaml
models:
  lcv_retail_analytics:
    staging:
      materialized: view         # Free, always fresh (recomputes on each query)
    marts:
      materialized: table        # Storage cost, but query-optimized
    intermediate:
      materialized: ephemeral    # No storage, inlined into dependent models
```

### Data Quality Tests (dbt Tests)

```yaml
# tests/data_quality.yml
version: 2

models:
  - name: stg_sales_clean
    columns:
      - name: sale_id
        tests:
          - unique
          - not_null
      - name: quantity
        tests:
          - not_null
          - dbt_utils.accepted_values:
              values: [1, 2, 3, 4, 5]  # Custom validation
      - name: total_amount
        tests:
          - relationships:  # Foreign key check
              to: ref('dim_date')
              field: date_key
```

**Run tests:**
```bash
dbt test                    # Run all tests
dbt test -s stg_sales      # Run tests for specific model
dbt test --select tag:post_hook  # Run tests with tag
```

### Common dbt Workflows

```bash
# Development workflow
dbt run                     # Transform all models
dbt run -s stg_sales       # Transform specific model
dbt test                    # Validate data quality
dbt docs generate          # Create documentation site
dbt docs serve             # View docs at localhost:8000

# Version control workflow
git add models/ tests/ dbt_project.yml profiles.yml
git commit -m "feat: add staging models with validation"

# Production workflow
dbt run --target prod      # Run against prod dataset
dbt snapshot               # Track slowly changing dimensions
dbt run --models state:modified+  # Only modified + downstream
```

### Debugging Common Issues

| Issue | Root Cause | Solution |
|-------|-----------|----------|
| `KeyboardInterrupt` on `dbt init` | Python 3.10 compatibility | Use manual setup (this guide) |
| `dbt: command not found` | Not in PATH, venv not active | `source venv/bin/activate` |
| `Profile not found` | profiles.yml missing or misnamed | Check `~/.dbt/profiles.yml` exists |
| Model fails to run | Missing dependencies or invalid SQL | Check `dbt parse` output, look at dbt logs |
| Tests failing | Data quality issue, not code issue | Good! Run `dbt test -d` for detailed failure |

### dbt + BigQuery Specifics

- **Method**: Use service account JSON (`method: service-account-json` in profiles.yml)
- **Threads**: Set to 4-8 (BigQuery can handle parallel queries)
- **Location**: Specify `location: US` if all datasets in same region (cheaper queries)
- **Incremental**: For large tables, use incremental materializations (only load new data)

```sql
-- Incremental model example
{{ config(materialized='incremental') }}

SELECT ... FROM raw_table
WHERE 1=1
{% if execute %}
  AND updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

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

**Last Updated**: February 27, 2026
**Purpose**: Universal roadmap for professional development practices
**Latest Additions**: GCP/BigQuery setup, credentials management, ETL pipeline patterns, BigQuery loading patterns (Python vs CLI vs External Tables)
