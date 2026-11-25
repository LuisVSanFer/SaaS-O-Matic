import pytest
from app.pricing import (
    calculate_base_price_cents,
    get_tax_rate,
    calculate_simulation_pricing,
    TIERS
)


class TestCalculateBasePriceCents:
    """Tests for the tiered pricing calculation."""

    # Test cases from the specification
    @pytest.mark.parametrize("users,expected_cents", [
        (0, 0),
        (1, 1000),
        (5, 5000),
        (10, 10000),
        (11, 10800),
        (15, 14000),
        (20, 18000),
        (30, 26000),
        (40, 34000),
        (50, 42000),
        (51, 42500),
        (60, 47000),
        (100, 67000),
    ])
    def test_tier_boundaries(self, users, expected_cents):
        """Test pricing at tier boundaries and within tiers."""
        assert calculate_base_price_cents(users) == expected_cents

    def test_negative_users_returns_zero(self):
        """Negative or zero users should return zero price."""
        assert calculate_base_price_cents(-5) == 0
        assert calculate_base_price_cents(0) == 0

    def test_large_number_of_users(self):
        """Test with a large number of users."""
        # 1000 users: 10*1000 + 40*800 + 950*500 = 10000 + 32000 + 475000 = 517000
        assert calculate_base_price_cents(1000) == 517000


class TestGetTaxRate:
    """Tests for tax rate lookup."""

    @pytest.mark.parametrize("country,expected_rate", [
        ("ES", 0.21),
        ("DE", 0.19),
        ("FR", 0.20),
        ("IT", 0.22),
        ("PT", 0.23),
        ("NL", 0.21),
        ("BE", 0.21),
        ("AT", 0.20),
        ("IE", 0.23),
        ("FI", 0.24),
        ("GR", 0.24),
        ("PL", 0.23),
        ("CZ", 0.21),
        ("SE", 0.25),
        ("DK", 0.25),
        ("US", 0.0),
        ("GB", 0.20),
        ("CH", 0.081),
        ("NO", 0.25),
    ])
    def test_known_countries(self, country, expected_rate):
        """Test tax rates for all configured countries."""
        assert get_tax_rate(country) == expected_rate

    def test_case_insensitive(self):
        """Country codes should be case insensitive."""
        assert get_tax_rate("es") == 0.21
        assert get_tax_rate("Es") == 0.21
        assert get_tax_rate("ES") == 0.21

    def test_unknown_country_returns_default(self):
        """Unknown countries should return 0% tax rate."""
        assert get_tax_rate("XX") == 0.0
        assert get_tax_rate("ZZ") == 0.0


class TestCalculateSimulationPricing:
    """Tests for the complete pricing calculation."""

    def test_spain_customer(self):
        """Test pricing for a Spanish customer (21% VAT)."""
        result = calculate_simulation_pricing(10, "ES")
        assert result["base_amount_cents"] == 10000
        assert result["tax_rate"] == 0.21
        assert result["tax_amount_cents"] == 2100  # 10000 * 0.21 = 2100
        assert result["total_amount_cents"] == 12100

    def test_germany_customer(self):
        """Test pricing for a German customer (19% VAT)."""
        result = calculate_simulation_pricing(10, "DE")
        assert result["base_amount_cents"] == 10000
        assert result["tax_rate"] == 0.19
        assert result["tax_amount_cents"] == 1900
        assert result["total_amount_cents"] == 11900

    def test_us_customer_no_vat(self):
        """Test pricing for US customer (0% VAT)."""
        result = calculate_simulation_pricing(10, "US")
        assert result["base_amount_cents"] == 10000
        assert result["tax_rate"] == 0.0
        assert result["tax_amount_cents"] == 0
        assert result["total_amount_cents"] == 10000

    def test_zero_users(self):
        """Test pricing with zero users."""
        result = calculate_simulation_pricing(0, "ES")
        assert result["base_amount_cents"] == 0
        assert result["tax_amount_cents"] == 0
        assert result["total_amount_cents"] == 0

    def test_tier_transitions(self):
        """Test pricing at exact tier transitions."""
        # 10 users - end of first tier
        r10 = calculate_simulation_pricing(10, "ES")
        assert r10["base_amount_cents"] == 10000

        # 11 users - start of second tier
        r11 = calculate_simulation_pricing(11, "ES")
        assert r11["base_amount_cents"] == 10800

        # 50 users - end of second tier
        r50 = calculate_simulation_pricing(50, "ES")
        assert r50["base_amount_cents"] == 42000

        # 51 users - start of third tier
        r51 = calculate_simulation_pricing(51, "ES")
        assert r51["base_amount_cents"] == 42500

    def test_all_amounts_are_integers(self):
        """All monetary amounts should be integers (cents)."""
        result = calculate_simulation_pricing(15, "ES")
        assert isinstance(result["base_amount_cents"], int)
        assert isinstance(result["tax_amount_cents"], int)
        assert isinstance(result["total_amount_cents"], int)
        assert isinstance(result["tax_rate"], float)


class TestTierConfiguration:
    """Tests to verify tier configuration matches specification."""

    def test_tier_definitions(self):
        """Verify tiers match the specification."""
        assert TIERS[0]["count"] == 10
        assert TIERS[0]["price_per_user_cents"] == 1000  # €10
        assert TIERS[1]["count"] == 40
        assert TIERS[1]["price_per_user_cents"] == 800   # €8
        assert TIERS[2]["count"] == float('inf')
        assert TIERS[2]["price_per_user_cents"] == 500   # €5