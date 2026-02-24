"""
Synthetic Data Generator for LCV Retail Analytics Platform

Generates realistic retail data for testing and development:
- Configurable number of stores, products, customers, transactions
- 5 regions with store distribution
- 3 product categories (textile, accessories, seasonal)
- Returns, discounts, loyalty points

Usage:
    python src/postgres/seed_synthetic_data.py

Logging:
    Execution logs are written to seed_data.log with rotation enabled (5MB max per file, 3 backups retained).
    Logs include step-by-step progress, record counts, and any errors for easy troubleshooting.

Reproducibility:
    Set RANDOM_SEED to generate identical datasets across runs (enables regression testing and debugging).
    Default seed=42 produces consistent results for development/testing workflows.

Required Environment Variables:
    POSTGRES_HOST: PostgreSQL host
    POSTGRES_PORT: PostgreSQL port (default: 5432)
    POSTGRES_USER: PostgreSQL username
    POSTGRES_PASSWORD: PostgreSQL password
    POSTGRES_DB: PostgreSQL database name

Optional Configuration (Defaults Provided):
    NUM_STORES: Number of stores to generate (default: 50)
    NUM_PRODUCTS: Number of products to generate (default: 500)
    NUM_CUSTOMERS: Number of customers to generate (default: 10000)
    NUM_SALES: Number of sales transactions to generate (default: 1000000)
    DATE_RANGE_DAYS: Historical data range in days (default: 730)
    RANDOM_SEED: Random seed for deterministic data generation (default: 42)
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

import numpy as np
import psycopg2
from dotenv import load_dotenv

# Configure logging with rotation
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # console output
        RotatingFileHandler(
            "seed_data.log", maxBytes=5_000_000, backupCount=3
        ),  # file output with rotation
    ],
)
logger = logging.getLogger(__name__)

# Suppress noisy database driver logs (psycopg2 is verbose in DEBUG/INFO mode)
logging.getLogger("psycopg2").setLevel(logging.WARNING)

# TODO: Future enhancement for observability at scale
# Consider switching to structured JSON logging (e.g., python-json-logger) when
# integrating with centralized monitoring/telemetry systems. Useful for parsing
# logs in ELK, Datadog, Splunk or similar platforms.

# Load environment variables
load_dotenv()

# Validate required environment variables: fail fast to prevent silent misconfigurations
# (e.g., running for 1M records, then failing at connection time)
required_vars = ["POSTGRES_HOST", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    raise RuntimeError(
        f"Missing required environment variables: {', '.join(missing_vars)}. "
        f"Please set them in .env or as system environment variables."
    )

# Extract configuration for safe logging
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# Database configuration
DB_CONFIG = {
    "host": POSTGRES_HOST,
    "port": POSTGRES_PORT,
    "user": POSTGRES_USER,
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": POSTGRES_DB,
}

# Domain Constants
# TODO: Future enhancement — Move to external YAML/JSON config when:
#   • Supporting international regions (more than 5-10 defined)
#   • Business rules need frequent updates without code deploy
#   • Multiple environments need different product hierarchies
# Current approach (code constants) is pragmatic for MVP/dev phase.
REGIONS = ["North", "South", "East", "West", "Central"]
PRODUCT_CATEGORIES = {
    "Textile": ["T-Shirt", "Dress", "Pants", "Jacket", "Sweater"],
    "Accessories": ["Hat", "Scarf", "Bag", "Shoes", "Gloves"],
    "Seasonal": ["Swimwear", "Thermal", "Snow Boots", "Sunglasses", "Winter Coat"],
}

# Data Generation Configuration (from environment)
NUM_STORES = int(os.getenv("NUM_STORES", 50))
NUM_PRODUCTS = int(os.getenv("NUM_PRODUCTS", 500))
NUM_CUSTOMERS = int(os.getenv("NUM_CUSTOMERS", 10000))
NUM_SALES = int(os.getenv("NUM_SALES", 1000000))
DATE_RANGE_DAYS = int(os.getenv("DATE_RANGE_DAYS", 730))  # 2 years
RANDOM_SEED = int(os.getenv("RANDOM_SEED", 42))


class DataGenerationError(Exception):
    """Custom exception for data generation failures."""

    pass


class SyntheticDataGenerator:
    """Generate synthetic retail data for PostgreSQL.

    Supports context manager for automatic resource cleanup:
        with SyntheticDataGenerator(DB_CONFIG) as gen:
            gen.generate_all()
    """

    def __init__(self, db_config: dict):
        """Initialize database connection."""
        self.db_config = db_config
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Context manager entry: establish database connection."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit: ensure connection always closes cleanly."""
        self.disconnect()
        # Return False to propagate exceptions (don't suppress them)
        return False

    def connect(self) -> None:
        """Connect to PostgreSQL database."""
        try:
            logger.info(
                "Connecting to PostgreSQL at %s:%s (database: %s, user: %s)",
                self.db_config["host"],
                self.db_config["port"],
                self.db_config["database"],
                self.db_config["user"],
            )
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("[OK] PostgreSQL connection established")
        except psycopg2.OperationalError as e:
            logger.error(f"[ERROR] Failed to connect to PostgreSQL: {e}")
            raise

    def disconnect(self) -> None:
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Disconnected from PostgreSQL")

    def validate_schema(self) -> None:
        """
        Validate that target tables exist and have expected schema.

        TODO: Schema validation enhancement roadmap:
        - Phase 1 (MVP): Check table existence only (prevent silent failure)
        - Phase 2: Verify column names and types match expected schema
        - Phase 3: Add detailed column constraint validation (NOT NULL, UNIQUE, etc.)
        - Phase 4: Integrate with Great Expectations for comprehensive data quality

        This runs before data insertion to fail fast on schema mismatches
        rather than discovering errors mid-pipeline.
        """
        required_tables = [
            "dim_date",
            "dim_store",
            "dim_product",
            "dim_customer",
            "fact_sales",
        ]
        try:
            logger.info("Validating target schema...")
            for table in required_tables:
                self.cursor.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM information_schema.tables
                        WHERE table_name = %s
                    )
                    """,
                    (table,),
                )
                exists = self.cursor.fetchone()[0]
                if not exists:
                    raise DataGenerationError(
                        f"Required table '{table}' does not exist in database. "
                        f"Run: psql -f SCHEMA/star_schema.sql"
                    )
                logger.debug(f"  ✓ {table}")
            logger.info("[OK] All required tables exist")
        except Exception as e:
            logger.error(f"[ERROR] Schema validation failed: {e}")
            raise

    def clear_tables(self) -> None:
        """Clear existing data from tables (for idempotency)."""
        try:
            logger.info("Clearing existing data from all tables...")
            tables = [
                "fact_sales",
                "dim_customer",
                "dim_store",
                "dim_product",
                "dim_date",
            ]
            for table in tables:
                self.cursor.execute(f"TRUNCATE TABLE {table} CASCADE;")
            self.conn.commit()
            logger.info("[OK] Cleared existing data from all tables")
        except psycopg2.Error as e:
            logger.error(f"[ERROR] Error clearing tables: {e}")
            self.conn.rollback()
            raise

    def generate_dim_date(self) -> None:
        """Generate date dimension table."""
        logger.info("Generating %d date dimension records...", DATE_RANGE_DAYS + 1)
        np.random.seed(RANDOM_SEED)
        # Date dimension covers 2-year lookback: enables trend analysis and YoY comparisons
        base_date = datetime.now() - timedelta(days=DATE_RANGE_DAYS)
        dates = []

        for i in range(DATE_RANGE_DAYS + 1):
            current_date = base_date + timedelta(days=i)
            # Format date_id as YYYYMMDD (e.g., 20260224) for easy sorting and period grouping
            date_id = int(current_date.strftime("%Y%m%d"))

            dates.append(
                (
                    date_id,
                    current_date.date(),
                    current_date.weekday() + 1,
                    current_date.strftime("%A"),
                    current_date.isocalendar()[1],
                    current_date.month,
                    current_date.strftime("%B"),
                    (current_date.month - 1) // 3 + 1,
                    (current_date.month - 1) // 3 + 1,
                    current_date.year,
                    current_date.year,
                    current_date.weekday() >= 4,  # True for Friday-Sunday (weekday 4-6)
                    False,
                    None,
                )
            )

        logger.info("Inserting %d records into dim_date...", len(dates))
        insert_query = """
            INSERT INTO dim_date (
                date_id, date_value, day_of_week, day_name, week_of_year,
                month, month_name, quarter, fiscal_quarter, year, fiscal_year,
                is_weekend, is_holiday, holiday_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.executemany(insert_query, dates)
        self.conn.commit()
        logger.info("[OK] Inserted %d date records", len(dates))

    def generate_dim_store(self) -> None:
        """Generate store dimension table."""
        logger.info("Generating %d store dimension records...", NUM_STORES)
        np.random.seed(RANDOM_SEED)
        stores = []

        for store_id in range(1, NUM_STORES + 1):
            # Distribute stores evenly across regions using modulo: enables regional sales analysis
            region = REGIONS[(store_id - 1) % len(REGIONS)]
            store_name = f"Store {store_id} - {region}"
            city = f"City_{region}_{store_id % 10}"
            country = "USA"
            store_type = np.random.choice(["Flagship", "Standard", "Express", "Pop-up"])

            stores.append(
                (
                    store_id,
                    store_name,
                    f"ST{store_id:04d}",
                    region,
                    country,
                    city,
                    float(np.random.uniform(30.0, 40.0)),  # latitude
                    float(np.random.uniform(-120.0, -70.0)),  # longitude
                    store_type,
                    (
                        datetime.now() - timedelta(days=np.random.randint(365, 3650))
                    ).date(),  # opening_date
                    None,  # closing_date
                    f"Manager_{store_id % 50}",
                    "Active",
                    np.random.randint(1000, 10000),  # square_meters
                )
            )

        logger.info("Inserting %d records into dim_store...", len(stores))
        insert_query = """
            INSERT INTO dim_store (
                store_id, store_name, store_code, region, country, city,
                latitude, longitude, store_type, opening_date, closing_date,
                store_manager, status, square_meters
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.executemany(insert_query, stores)
        self.conn.commit()
        logger.info("[OK] Inserted %d store records", len(stores))

    def generate_dim_product(self) -> None:
        """Generate product dimension table."""
        logger.info("Generating %d product dimension records...", NUM_PRODUCTS)
        np.random.seed(RANDOM_SEED)
        products = []
        product_id = 1

        for category, subcategories in PRODUCT_CATEGORIES.items():
            products_per_category = NUM_PRODUCTS // len(PRODUCT_CATEGORIES)
            for i in range(products_per_category):
                subcategory = subcategories[i % len(subcategories)]
                product_name = (
                    f"{subcategory} - {chr(65 + (i % 26))}{chr(65 + (i // 26) % 26)}"
                )
                unit_cost = np.random.uniform(5, 50)
                # Retail markup 1.5x-3.5x cost: simulates retail pricing strategy
                # Lower margins on commodity items, higher on branded products
                list_price = unit_cost * np.random.uniform(1.5, 3.5)

                products.append(
                    (
                        product_id,
                        product_name,
                        f"PRD{product_id:05d}",
                        category,
                        subcategory,
                        np.random.choice(["Red", "Blue", "Black", "White", "Green"]),
                        np.random.choice(["S", "M", "L", "XL", "One Size"]),
                        np.random.choice(["Cotton", "Polyester", "Wool", "Silk"]),
                        np.random.choice(
                            ["Spring", "Summer", "Fall", "Winter", "Year-Round"]
                        ),
                        np.random.choice(
                            ["Brand A", "Brand B", "Brand C", "Brand D", "Generic"]
                        ),
                        unit_cost,
                        list_price,
                        "Active",
                        datetime.now(),
                        datetime.now(),
                        True,
                        datetime.now(),
                    )
                )
                product_id += 1

        logger.info("Inserting %d records into dim_product...", len(products))
        insert_query = """
            INSERT INTO dim_product (
                product_id, product_name, product_code, category, subcategory,
                color, size, material, season, brand, unit_cost, list_price,
                status, created_at, updated_at, is_current, scd_start_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.executemany(insert_query, products)
        self.conn.commit()
        logger.info("[OK] Inserted %d product records", len(products))

    def generate_dim_customer(self) -> None:
        """Generate customer dimension table."""
        logger.info("Generating %d customer dimension records...", NUM_CUSTOMERS)
        np.random.seed(RANDOM_SEED)
        customers = []

        for customer_id in range(1, NUM_CUSTOMERS + 1):
            # 70% loyalty members, 30% one-time guests: reflects realistic retail mix
            # Loyalty members enable RFM analysis, repeat purchase tracking, churn detection
            loyalty_member = bool(
                np.random.choice([True, False], p=[0.7, 0.3])
            )  # Convert numpy.bool_ to Python bool
            country = "USA"

            # Generate dates for loyalty members
            if loyalty_member:
                join_date = (
                    datetime.now() - timedelta(days=np.random.randint(30, 1000))
                ).date()
                first_purchase_date = join_date
            else:
                join_date = None
                first_purchase_date = None

            customers.append(
                (
                    customer_id,
                    loyalty_member,
                    join_date,
                    first_purchase_date,
                    None,  # last_purchase_date (will be updated later)
                    0,  # lifetime_purchases
                    0.0,  # lifetime_spend
                    country,
                    "Active",
                )
            )

        logger.info("Inserting %d records into dim_customer...", len(customers))
        insert_query = """
            INSERT INTO dim_customer (
                customer_id, loyalty_member, join_date, first_purchase_date,
                last_purchase_date, lifetime_purchases, lifetime_spend,
                country, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.executemany(insert_query, customers)
        self.conn.commit()
        logger.info("[OK] Inserted %d customer records", len(customers))

    def generate_fact_sales(self) -> None:
        """Generate fact sales table (~1M transactions)."""
        # TODO: Data insertion optimization roadmap
        # Current approach (executemany in 10k batches) works well for MVP.
        # Future optimizations when scaling:
        #   1. Dimension tables batch inserts: When dim_* tables grow to 1M+ rows
        #      - Currently small (11k total), so single executemany() is fine
        #      - Batch when memory/performance becomes bottleneck
        #   2. Bulk loading with COPY FROM: When inserting 10M+ rows
        #      - PostgreSQL COPY is 2-5x faster than executemany() for large volumes
        #      - Useful for streaming pipelines or massive data imports
        #   3. Separate generate/insert methods: When testing data generation logic
        #      - Enables unit testing generation independently of DB I/O
        #      - Decouple business logic (random generation) from infrastructure (DB writes)
        # Trigger points:
        #   - Dimension batching: NUM_STORES > 100k OR NUM_PRODUCTS > 1M
        #   - COPY FROM: NUM_SALES > 10M
        #   - Generate/insert split: When data gen unit test coverage needed

        logger.info("Generating %d fact sales records (in batches)...", NUM_SALES)
        np.random.seed(RANDOM_SEED)

        # Get actual product, store, and customer IDs from database
        self.cursor.execute("SELECT product_id FROM dim_product ORDER BY product_id")
        product_ids = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT store_id FROM dim_store ORDER BY store_id")
        store_ids = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT customer_id FROM dim_customer ORDER BY customer_id")
        customer_ids = [row[0] for row in self.cursor.fetchall()]

        base_date = datetime.now() - timedelta(days=DATE_RANGE_DAYS)
        sales_records = []
        sale_id = 1
        payment_methods = ["Cash", "Credit Card", "Debit Card", "Mobile Pay"]

        # Generate sales in batches to reduce memory usage: prevents out-of-memory errors on large datasets
        batch_size = 10000
        total_batches = NUM_SALES // batch_size
        for batch_num in range(0, total_batches):
            for _ in range(batch_size):
                sale_date = base_date + timedelta(
                    days=int(np.random.randint(0, DATE_RANGE_DAYS + 1))
                )
                store_id = int(np.random.choice(store_ids))
                product_id = int(np.random.choice(product_ids))

                # 80% of sales tracked to loyalty members: enables customer segmentation analysis
                # 20% anonymous cash/guest transactions: realistic retail scenario
                if np.random.random() < 0.8:
                    customer_id = int(np.random.choice(customer_ids))
                else:
                    customer_id = None

                quantity = int(np.random.randint(1, 10))
                unit_price = float(np.random.uniform(10, 200))

                # Calculate cost: assumes 40-60% margin on cost
                # Markup ranges from 1.5x to 2.5x to cover wholesale cost + operating expenses + profit
                cost_markup = float(np.random.uniform(1.5, 2.5))
                unit_cost = unit_price / cost_markup
                cost_amount = unit_cost * quantity

                # Discount distribution: mimics promotional strategy
                # 50% no discount, 20% small (5%), 15% moderate (10%), 10% high (15%), 5% deep (20%)
                discount_pct = int(
                    np.random.choice([0, 5, 10, 15, 20], p=[0.5, 0.2, 0.15, 0.1, 0.05])
                )
                total_amount = unit_price * quantity
                discount_amount = (
                    (total_amount * discount_pct) / 100 if discount_pct > 0 else 0
                )
                net_amount = total_amount - discount_amount

                # Margin calculation: profit = revenue - cost
                margin_amount = net_amount - cost_amount

                # Returns (5% realistic e-commerce return rate): negative transactions reduce recognition
                is_return = bool(
                    np.random.choice([True, False], p=[0.05, 0.95])
                )  # Convert numpy.bool_ to Python bool
                if is_return:
                    # Returns are recorded as negative to offset original sale in fact table
                    net_amount = -abs(net_amount)
                    cost_amount = -abs(cost_amount)
                    margin_amount = net_amount - cost_amount

                payment_method = str(np.random.choice(payment_methods))

                sales_records.append(
                    (
                        sale_id,
                        store_id,
                        product_id,
                        customer_id,
                        sale_date,
                        quantity,
                        unit_price,
                        total_amount,
                        discount_pct,
                        discount_amount,
                        net_amount,
                        cost_amount,
                        margin_amount,
                        payment_method,
                        is_return,
                    )
                )
                sale_id += 1

            # Insert batch
            insert_query = """
                INSERT INTO fact_sales (
                    sale_id, store_id, product_id, customer_id, sale_date,
                    quantity, unit_price, total_amount, discount_pct,
                    discount_amount, net_amount, cost_amount, margin_amount,
                    payment_method, is_return
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.executemany(insert_query, sales_records)
            self.conn.commit()
            logger.info(
                "Inserted sales batch %d/%d (%d records)",
                batch_num + 1,
                total_batches,
                len(sales_records),
            )
            sales_records = []

        logger.info("[OK] Inserted %d total fact sales records", sale_id - 1)

    def create_indexes(self) -> None:
        """Create indexes for query optimization."""
        logger.info("Creating database indexes for query optimization...")
        indexes = [
            "CREATE INDEX idx_fact_sales_date_2 ON fact_sales(sale_date);",
            "CREATE INDEX idx_fact_sales_store_2 ON fact_sales(store_id);",
            "CREATE INDEX idx_fact_sales_product_2 ON fact_sales(product_id);",
            "CREATE INDEX idx_fact_sales_customer_2 ON fact_sales(customer_id);",
            "CREATE INDEX idx_fact_sales_store_product_date_2 ON fact_sales(store_id, product_id, sale_date);",
        ]

        created_count = 0
        for index_query in indexes:
            try:
                logger.debug("Creating index: %s", index_query[:50] + "...")
                self.cursor.execute(index_query)
                self.conn.commit()
                created_count += 1
            except psycopg2.Error as e:
                if "already exists" not in str(e):
                    logger.warning(f"Index creation warning: {e}")
                self.conn.rollback()

        logger.info("[OK] Created %d indexes", created_count)

    def generate_all(self) -> None:
        """Run the complete data generation pipeline.

        Should be called within a context manager to ensure proper resource cleanup:
            with SyntheticDataGenerator(DB_CONFIG) as gen:
                gen.generate_all()
        """
        try:
            logger.info("=" * 60)
            logger.info("STARTING SYNTHETIC DATA GENERATION PIPELINE")
            logger.info("=" * 60)

            logger.info("Step 1/8: Validating target schema...")
            self.validate_schema()

            logger.info("Step 2/8: Clearing existing data...")
            self.clear_tables()

            logger.info("Step 3/8: Generating date dimension...")
            self.generate_dim_date()

            logger.info("Step 4/8: Generating store dimension...")
            self.generate_dim_store()

            logger.info("Step 5/8: Generating product dimension...")
            self.generate_dim_product()

            logger.info("Step 6/8: Generating customer dimension...")
            self.generate_dim_customer()

            logger.info("Step 7/8: Generating fact sales...")
            self.generate_fact_sales()

            logger.info("Step 8/8: Creating indexes...")
            self.create_indexes()

            logger.info("=" * 60)
            logger.info("[OK] SYNTHETIC DATA GENERATION COMPLETED SUCCESSFULLY!")
            logger.info("=" * 60)
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"[ERROR] ERROR DURING DATA GENERATION: {e}")
            logger.error("=" * 60)
            raise
        finally:
            self.disconnect()


def main() -> None:
    """Entry point for synthetic data generation with proper error handling and exit codes.

    Exit codes:
        0 = success
        1 = fatal error (logs error and exits for CI/CD detection)
    """
    try:
        start_time = datetime.now()
        logger.info(" " * 60)
        logger.info("LCV RETAIL ANALYTICS PLATFORM - SYNTHETIC DATA GENERATOR")
        logger.info(" " * 60)

        # Log database configuration (safe - no password)
        logger.info(
            "Database config: host=%s port=%s db=%s user=%s",
            POSTGRES_HOST,
            POSTGRES_PORT,
            POSTGRES_DB,
            POSTGRES_USER,
        )

        # Log data generation configuration
        logger.info(
            "Data generation config: stores=%d products=%d customers=%d sales=%d days=%d seed=%d",
            NUM_STORES,
            NUM_PRODUCTS,
            NUM_CUSTOMERS,
            NUM_SALES,
            DATE_RANGE_DAYS,
            RANDOM_SEED,
        )

        # Use context manager to ensure database connection always closes cleanly
        with SyntheticDataGenerator(DB_CONFIG) as generator:
            generator.generate_all()

        # Calculate and log elapsed time for observability
        elapsed_seconds = (datetime.now() - start_time).total_seconds()
        elapsed_minutes = elapsed_seconds / 60
        logger.info(
            "Pipeline completed successfully in %.2f seconds (%.2f minutes)",
            elapsed_seconds,
            elapsed_minutes,
        )
        sys.exit(0)

    except Exception as e:
        # Top-level error handler: logs fatal errors cleanly for CI/CD detection
        logger.error("=" * 60)
        logger.error("[FATAL] Pipeline failed: %s", str(e), exc_info=True)
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
