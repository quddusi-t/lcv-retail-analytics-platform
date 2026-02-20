"""
Synthetic Data Generator for LCV Retail Analytics Platform

Generates realistic retail data for testing and development:
- Configurable number of stores, products, customers, transactions
- 5 regions with store distribution
- 3 product categories (textile, accessories, seasonal)
- Returns, discounts, loyalty points

Usage:
    python src/postgres/seed_synthetic_data.py

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
    RANDOM_SEED: Random seed for reproducibility (default: 42)
"""

import logging
import os
from datetime import datetime, timedelta

import numpy as np
import psycopg2
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # console output
        logging.FileHandler("seed_data.log"),  # file output
    ],
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

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


class SyntheticDataGenerator:
    """Generate synthetic retail data for PostgreSQL."""

    def __init__(self, db_config: dict):
        """Initialize database connection."""
        self.db_config = db_config
        self.conn = None
        self.cursor = None

    def connect(self) -> None:
        """Connect to PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logger.info("Connected to PostgreSQL successfully")
        except psycopg2.OperationalError as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def disconnect(self) -> None:
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Disconnected from PostgreSQL")

    def clear_tables(self) -> None:
        """Clear existing data from tables (for idempotency)."""
        try:
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
            logger.info("Cleared existing data from all tables")
        except psycopg2.Error as e:
            logger.error(f"Error clearing tables: {e}")
            self.conn.rollback()
            raise

    def generate_dim_date(self) -> None:
        """Generate date dimension table."""
        logger.info("Generating date dimension...")
        np.random.seed(RANDOM_SEED)
        base_date = datetime.now() - timedelta(days=DATE_RANGE_DAYS)
        dates = []

        for i in range(DATE_RANGE_DAYS + 1):
            current_date = base_date + timedelta(days=i)
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
                    1 if current_date.weekday() >= 4 else 0,
                    False,
                    None,
                )
            )

        insert_query = """
            INSERT INTO dim_date (
                date_id, date_value, day_of_week, day_name, week_of_year,
                month, month_name, quarter, fiscal_quarter, year, fiscal_year,
                is_weekend, is_holiday, holiday_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.executemany(insert_query, dates)
        self.conn.commit()
        logger.info(f"Generated {len(dates)} date records")

    def generate_dim_store(self) -> None:
        """Generate store dimension table."""
        logger.info("Generating store dimension...")
        np.random.seed(RANDOM_SEED)
        stores = []

        for store_id in range(1, NUM_STORES + 1):
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

        insert_query = """
            INSERT INTO dim_store (
                store_id, store_name, store_code, region, country, city,
                latitude, longitude, store_type, opening_date, closing_date,
                store_manager, status, square_meters
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.executemany(insert_query, stores)
        self.conn.commit()
        logger.info(f"Generated {len(stores)} store records")

    def generate_dim_product(self) -> None:
        """Generate product dimension table."""
        logger.info("Generating product dimension...")
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

        insert_query = """
            INSERT INTO dim_product (
                product_id, product_name, product_code, category, subcategory,
                color, size, material, season, brand, unit_cost, list_price,
                status, created_at, updated_at, is_current, scd_start_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.executemany(insert_query, products)
        self.conn.commit()
        logger.info(f"Generated {len(products)} product records")

    def generate_dim_customer(self) -> None:
        """Generate customer dimension table."""
        logger.info("Generating customer dimension...")
        np.random.seed(RANDOM_SEED)
        customers = []

        for customer_id in range(1, NUM_CUSTOMERS + 1):
            loyalty_member = np.random.choice([True, False], p=[0.7, 0.3])
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

        insert_query = """
            INSERT INTO dim_customer (
                customer_id, loyalty_member, join_date, first_purchase_date,
                last_purchase_date, lifetime_purchases, lifetime_spend,
                country, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.executemany(insert_query, customers)
        self.conn.commit()
        logger.info(f"Generated {len(customers)} customer records")

    def generate_fact_sales(self) -> None:
        """Generate fact sales table (~1M transactions)."""
        logger.info("Generating fact sales table (~1M records)...")
        np.random.seed(RANDOM_SEED)

        base_date = datetime.now() - timedelta(days=DATE_RANGE_DAYS)
        sales_records = []
        sale_id = 1
        payment_methods = ["Cash", "Credit Card", "Debit Card", "Mobile Pay"]

        # Generate sales in batches to reduce memory usage
        batch_size = 10000
        for batch_num in range(0, NUM_SALES // batch_size):
            for _ in range(batch_size):
                sale_date = base_date + timedelta(
                    days=np.random.randint(0, DATE_RANGE_DAYS + 1)
                )
                store_id = np.random.randint(1, NUM_STORES + 1)
                product_id = np.random.randint(1, NUM_PRODUCTS + 1)

                # 80% of sales are from loyalty members
                if np.random.random() < 0.8:
                    customer_id = np.random.randint(1, NUM_CUSTOMERS + 1)
                else:
                    customer_id = None

                quantity = np.random.randint(1, 10)
                unit_price = np.random.uniform(10, 200)

                # Calculate cost (assume 40-60% margin on cost)
                cost_markup = np.random.uniform(1.5, 2.5)
                unit_cost = unit_price / cost_markup
                cost_amount = unit_cost * quantity

                # Discounts
                discount_pct = np.random.choice(
                    [0, 5, 10, 15, 20], p=[0.5, 0.2, 0.15, 0.1, 0.05]
                )
                total_amount = unit_price * quantity
                discount_amount = (
                    (total_amount * discount_pct) / 100 if discount_pct > 0 else 0
                )
                net_amount = total_amount - discount_amount

                # Margin calculation
                margin_amount = net_amount - cost_amount

                # Returns (5% chance)
                is_return = np.random.choice([True, False], p=[0.05, 0.95])
                if is_return:
                    net_amount = -abs(net_amount)
                    cost_amount = -abs(cost_amount)
                    margin_amount = net_amount - cost_amount

                payment_method = np.random.choice(payment_methods)

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
                f"Inserted sales batch {batch_num + 1}/{NUM_SALES // batch_size}"
            )
            sales_records = []

    def create_indexes(self) -> None:
        """Create indexes for query optimization."""
        logger.info("Creating indexes...")
        indexes = [
            "CREATE INDEX idx_fact_sales_date_2 ON fact_sales(sale_date);",
            "CREATE INDEX idx_fact_sales_store_2 ON fact_sales(store_id);",
            "CREATE INDEX idx_fact_sales_product_2 ON fact_sales(product_id);",
            "CREATE INDEX idx_fact_sales_customer_2 ON fact_sales(customer_id);",
            "CREATE INDEX idx_fact_sales_store_product_date_2 ON fact_sales(store_id, product_id, sale_date);",
        ]

        for index_query in indexes:
            try:
                self.cursor.execute(index_query)
                self.conn.commit()
            except psycopg2.Error as e:
                if "already exists" not in str(e):
                    logger.warning(f"Index creation warning: {e}")
                self.conn.rollback()

        logger.info("Indexes created successfully")

    def generate_all(self) -> None:
        """Run the complete data generation pipeline."""
        try:
            self.connect()
            self.clear_tables()
            self.generate_dim_date()
            self.generate_dim_store()
            self.generate_dim_product()
            self.generate_dim_customer()
            self.generate_fact_sales()
            self.create_indexes()
            logger.info("✅ Synthetic data generation completed successfully!")
        except Exception as e:
            logger.error(f"Error during data generation: {e}")
            raise
        finally:
            self.disconnect()


def main() -> None:
    """Entry point for synthetic data generation."""
    logger.info("Starting synthetic data generation for LCV Retail Analytics Platform")

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

    generator = SyntheticDataGenerator(DB_CONFIG)
    generator.generate_all()


if __name__ == "__main__":
    main()
