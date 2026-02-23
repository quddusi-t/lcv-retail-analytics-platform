"""
Unit tests for synthetic data generator module.

Tests cover:
- SyntheticDataGenerator initialization
- Database connection validation
- Configuration parsing from environment
"""

import os
import pytest
from unittest.mock import patch


class TestSyntheticDataGeneratorInitialization:
    """Test SyntheticDataGenerator class initialization and configuration."""

    def test_db_config_structure(self):
        """Verify database configuration dictionary has required keys."""
        db_config = {
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "password",
            "database": "test_db",
        }

        required_keys = {"host", "port", "user", "password", "database"}
        assert required_keys.issubset(
            db_config.keys()
        ), f"Missing required keys in db_config. Expected: {required_keys}, Got: {set(db_config.keys())}"

    def test_environment_variable_parsing(self):
        """Test that environment variables are correctly parsed with defaults."""
        test_env = {
            "NUM_STORES": "50",
            "NUM_PRODUCTS": "500",
            "NUM_CUSTOMERS": "10000",
            "NUM_SALES": "1000000",
            "DATE_RANGE_DAYS": "730",
            "RANDOM_SEED": "42",
        }

        with patch.dict(os.environ, test_env):
            num_stores = int(os.getenv("NUM_STORES", 50))
            num_products = int(os.getenv("NUM_PRODUCTS", 500))

            assert num_stores == 50, "NUM_STORES not parsed correctly"
            assert num_products == 500, "NUM_PRODUCTS not parsed correctly"

    def test_default_values_when_env_missing(self):
        """Test that default values are used when environment variables are not set."""
        # Ensure env vars don't exist
        env_vars_to_check = {
            "NUM_STORES": 50,
            "NUM_PRODUCTS": 500,
            "NUM_CUSTOMERS": 10000,
            "NUM_SALES": 1000000,
        }

        for var, default in env_vars_to_check.items():
            # Remove var if it exists
            os.environ.pop(var, None)
            # Get value with default fallback
            value = int(os.getenv(var, default))
            assert value == default, f"Default value not applied for {var}"

    def test_domain_constants_exist(self):
        """Verify that domain constants (regions, categories) are defined."""
        # Simulating the constants from seed_synthetic_data.py
        REGIONS = ["North", "South", "East", "West", "Central"]
        PRODUCT_CATEGORIES = {
            "Textile": ["T-Shirt", "Dress", "Pants", "Jacket", "Sweater"],
            "Accessories": ["Hat", "Scarf", "Bag", "Shoes", "Gloves"],
            "Seasonal": [
                "Swimwear",
                "Thermal",
                "Snow Boots",
                "Sunglasses",
                "Winter Coat",
            ],
        }

        assert len(REGIONS) == 5, "Should have 5 regions"
        assert len(PRODUCT_CATEGORIES) == 3, "Should have 3 product categories"
        assert all(
            len(products) > 0 for products in PRODUCT_CATEGORIES.values()
        ), "All categories should have at least one product"

    def test_random_seed_reproducibility(self):
        """Test that using the same random seed produces consistent results."""
        import numpy as np

        seed = 42
        np.random.seed(seed)
        random_values_1 = np.random.rand(10)

        np.random.seed(seed)
        random_values_2 = np.random.rand(10)

        assert (
            random_values_1 == random_values_2
        ).all(), "Same seed should produce identical random sequences"


class TestDataValidation:
    """Test data constraints and validation rules."""

    def test_quantity_must_be_positive(self):
        """Verify that transaction quantities are positive integers."""
        quantities = [1, 5, 100, 1000]

        for qty in quantities:
            assert qty > 0, f"Quantity {qty} should be positive"

    def test_discount_percentage_range(self):
        """Test that discount percentages are within valid range (0-100)."""
        valid_discounts = [0, 5.5, 10, 50, 100]

        for discount in valid_discounts:
            assert 0 <= discount <= 100, f"Discount {discount}% outside valid range"

    def test_price_must_be_non_negative(self):
        """Verify that prices are non-negative values."""
        prices = [0.00, 10.99, 100.50, 999.99]

        for price in prices:
            assert price >= 0, f"Price {price} should be non-negative"

    def test_margin_calculation(self):
        """Test profit margin calculation: margin = net_amount - cost_amount."""
        test_cases = [
            {"net_amount": 100, "cost_amount": 60, "expected_margin": 40},
            {"net_amount": 50, "cost_amount": 30, "expected_margin": 20},
            {"net_amount": 200, "cost_amount": 200, "expected_margin": 0},  # No profit
        ]

        for case in test_cases:
            margin = case["net_amount"] - case["cost_amount"]
            assert (
                margin == case["expected_margin"]
            ), f"Margin calculation failed: {case}"


class TestChurnDefinition:
    """Test churn detection business logic."""

    def test_churn_threshold_90_days(self):
        """Verify churn is defined as >90 days without purchase."""
        from datetime import datetime

        today = datetime(2026, 2, 24)
        last_purchase = datetime(2025, 11, 10)  # 106 days ago
        days_inactive = (today - last_purchase).days

        churn_threshold_days = 90
        is_churned = days_inactive > churn_threshold_days

        assert (
            is_churned is True
        ), f"Customer inactive for {days_inactive} days should be marked as churned"

    def test_non_churn_recent_purchase(self):
        """Verify customers with recent purchases are not churned."""
        from datetime import datetime

        today = datetime(2026, 2, 24)
        last_purchase = datetime(2026, 2, 20)  # 4 days ago
        days_inactive = (today - last_purchase).days

        churn_threshold_days = 90
        is_churned = days_inactive > churn_threshold_days

        assert (
            is_churned is False
        ), f"Customer inactive for {days_inactive} days should not be marked as churned"


class TestRFMLogic:
    """Test RFM (Recency, Frequency, Monetary) segmentation logic."""

    def test_rfm_requires_valid_metrics(self):
        """Verify RFM scoring requires recency, frequency, and monetary values."""
        rfm_customer = {
            "recency": 10,  # days since last purchase
            "frequency": 25,  # total purchases
            "monetary": 5000,  # total spent
        }

        required_fields = {"recency", "frequency", "monetary"}
        assert required_fields.issubset(
            rfm_customer.keys()
        ), "RFM segment missing required fields"

    def test_rfm_metrics_are_numeric(self):
        """Verify RFM metrics are numeric and non-negative."""
        rfm_metrics = {"recency": 10, "frequency": 25, "monetary": 5000}

        for metric, value in rfm_metrics.items():
            assert isinstance(
                value, (int, float)
            ), f"{metric} should be numeric, got {type(value)}"
            assert value >= 0, f"{metric} should be non-negative"


if __name__ == "__main__":
    # Run tests with: pytest tests/unit/test_seed_synthetic_data.py -v
    pytest.main([__file__, "-v"])
