"""
Custom Macroeconomic Shock Simulator for Cross-Asset Sensitivity Analysis.
"""
from typing import Dict, Any, List


class MacroScenarioSimulator:
    """
    Simulates portfolio and stock returns under user-customized macroeconomic shocks:
    - Interest Rates (Fed Funds / 10Y Yield delta in basis points)
    - Inflation (CPI delta in %)
    - Crude Oil (WTI/Brent delta in %)
    - Real GDP Growth shock (delta in %)
    - US Dollar Index (DXY delta in %)
    """

    # Sector Elasticity Matrix: Sensitivity coefficients (\beta_{factor})
    SECTOR_SENSITIVITIES = {
        "Information Technology": {"rates": -0.065, "inflation": -0.35, "oil": -0.15, "gdp": 1.20, "usd": -0.40},
        "Financials":             {"rates": 0.045,  "inflation": 0.10,  "oil": 0.05,  "gdp": 1.10, "usd": 0.10},
        "Energy":                 {"rates": -0.015, "inflation": 0.60,  "oil": 0.85,  "gdp": 0.90, "usd": -0.50},
        "Consumer Discretionary": {"rates": -0.055, "inflation": -0.50, "oil": -0.30, "gdp": 1.35, "usd": -0.20},
        "Consumer Staples":       {"rates": -0.020, "inflation": -0.10, "oil": -0.10, "gdp": 0.40, "usd": -0.15},
        "Health Care":            {"rates": -0.025, "inflation": -0.15, "oil": -0.05, "gdp": 0.50, "usd": -0.20},
        "Industrials":            {"rates": -0.035, "inflation": -0.20, "oil": -0.25, "gdp": 1.15, "usd": -0.30},
        "Utilities":              {"rates": -0.080, "inflation": -0.30, "oil": -0.10, "gdp": 0.20, "usd": 0.05},
        "Real Estate":            {"rates": -0.095, "inflation": -0.40, "oil": -0.10, "gdp": 0.70, "usd": 0.00},
        "Communication Services": {"rates": -0.050, "inflation": -0.30, "oil": -0.10, "gdp": 1.05, "usd": -0.30},
    }

    def simulate_macro_shock(
        self,
        ticker: str,
        current_price: float,
        sector: str = "Information Technology",
        beta: float = 1.10,
        rate_shock_bps: float = 100.0,       # e.g., +100 bps
        inflation_shock_pct: float = 1.5,    # e.g., +1.5%
        oil_shock_pct: float = 20.0,         # e.g., +20%
        gdp_shock_pct: float = -1.0,         # e.g., -1.0%
        usd_shock_pct: float = 5.0           # e.g., +5.0%
    ) -> Dict[str, Any]:
        """
        Calculates price impact of multi-variable macroeconomic shock.
        """
        sens = self.SECTOR_SENSITIVITIES.get(
            sector,
            {"rates": -0.045, "inflation": -0.25, "oil": -0.10, "gdp": 1.0, "usd": -0.20}
        )

        # Factor contributions to return
        # rate_shock_bps / 100 * rates_coeff
        rate_contrib = (rate_shock_bps / 100.0) * sens["rates"] * 100.0
        inflation_contrib = inflation_shock_pct * sens["inflation"]
        oil_contrib = oil_shock_pct * sens["oil"]
        gdp_contrib = gdp_shock_pct * sens["gdp"]
        usd_contrib = usd_shock_pct * sens["usd"]

        # Aggregate return adjusted by stock beta
        total_unscaled_shock = (
            rate_contrib + inflation_contrib + oil_contrib + gdp_contrib + usd_contrib
        )
        total_projected_return_pct = total_unscaled_shock * (1.0 + (beta - 1.0) * 0.3)
        projected_price = max(0.01, current_price * (1.0 + total_projected_return_pct / 100.0))

        return {
            "ticker": ticker,
            "current_price": current_price,
            "projected_price": round(float(projected_price), 2),
            "total_projected_return_pct": round(float(total_projected_return_pct), 2),
            "dollar_impact_per_share": round(float(projected_price - current_price), 2),
            "factor_decomposition": {
                "rates_effect_pct": round(float(rate_contrib), 2),
                "inflation_effect_pct": round(float(inflation_contrib), 2),
                "oil_effect_pct": round(float(oil_contrib), 2),
                "gdp_effect_pct": round(float(gdp_contrib), 2),
                "usd_effect_pct": round(float(usd_contrib), 2)
            },
            "parameters": {
                "rate_shock_bps": rate_shock_bps,
                "inflation_shock_pct": inflation_shock_pct,
                "oil_shock_pct": oil_shock_pct,
                "gdp_shock_pct": gdp_shock_pct,
                "usd_shock_pct": usd_shock_pct,
                "sector": sector,
                "beta": beta
            }
        }
