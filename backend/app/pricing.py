from typing import Dict

# Tax rates by country (ISO 3166-1 alpha-2)
# Using standard VAT rates as of 2024
TAX_RATES: Dict[str, float] = {
    "ES": 0.21,   # Spain - IVA 21%
    "DE": 0.19,   # Germany - MwSt 19%
    "FR": 0.20,   # France - TVA 20%
    "IT": 0.22,   # Italy - IVA 22%
    "PT": 0.23,   # Portugal - IVA 23%
    "NL": 0.21,   # Netherlands - BTW 21%
    "BE": 0.21,   # Belgium - BTW 21%
    "AT": 0.20,   # Austria - USt 20%
    "IE": 0.23,   # Ireland - VAT 23%
    "FI": 0.24,   # Finland - ALV 24%
    "GR": 0.24,   # Greece - FPA 24%
    "PL": 0.23,   # Poland - VAT 23%
    "CZ": 0.21,   # Czech Republic - DPH 21%
    "SE": 0.25,   # Sweden - Moms 25%
    "DK": 0.25,   # Denmark - Moms 25%
    "US": 0.0,    # US - No VAT (sales tax varies by state)
    "GB": 0.20,   # UK - VAT 20%
    "CH": 0.081,  # Switzerland - MWST 8.1%
    "NO": 0.25,   # Norway - MVA 25%
}

DEFAULT_TAX_RATE = 0.0

# Pricing tiers (in EUR cents per user)
# Each tier defines: number of users in this tier, price per user
TIERS = [
    {"count": 10, "price_per_user_cents": 1000},      # First 10 users: €10/user
    {"count": 40, "price_per_user_cents": 800},       # Next 40 users (11-50): €8/user
    {"count": float('inf'), "price_per_user_cents": 500},  # Remaining users (51+): €5/user
]


def calculate_base_price_cents(active_users: int) -> int:
    """
    Calculate base price using tiered pricing algorithm.

    Example: 15 users
    - First 10 users: 10 * 1000 = 10,000 cents (€100)
    - Next 5 users: 5 * 800 = 4,000 cents (€40)
    - Total: 14,000 cents (€140)
    """
    if active_users <= 0:
        return 0

    total_cents = 0
    remaining_users = active_users

    for tier in TIERS:
        tier_count = tier["count"]
        price = tier["price_per_user_cents"]

        # Calculate how many users fall in this tier
        users_in_tier = min(remaining_users, tier_count)

        if users_in_tier <= 0:
            break

        total_cents += users_in_tier * price
        remaining_users -= users_in_tier

        if remaining_users <= 0:
            break

    return total_cents


def get_tax_rate(country_code: str) -> float:
    """Get tax rate for a country (ISO 3166-1 alpha-2)"""
    return TAX_RATES.get(country_code.upper(), DEFAULT_TAX_RATE)


def calculate_simulation_pricing(active_users: int, country_code: str) -> Dict:
    """
    Calculate complete pricing for a simulation.
    Returns all amounts in EUR cents.
    """
    base_amount_cents = calculate_base_price_cents(active_users)
    tax_rate = get_tax_rate(country_code)
    tax_amount_cents = round(base_amount_cents * tax_rate)
    total_amount_cents = base_amount_cents + tax_amount_cents

    return {
        "base_amount_cents": base_amount_cents,
        "tax_rate": tax_rate,
        "tax_amount_cents": tax_amount_cents,
        "total_amount_cents": total_amount_cents,
    }