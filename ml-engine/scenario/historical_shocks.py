"""
Historical Crisis Stress Testing Engine for Portfolios and Individual Equities.
"""
from typing import Dict, Any, List


class HistoricalStressTester:
    """
    Replays systemic historical drawdowns and factor sensitivities across 4 major crises:
    1. 2008 Global Financial Crisis (Lehman Collapse & Liquidity Crunch)
    2. 2020 COVID-19 Flash Crash
    3. 2022 Fed Aggressive Tightening & Inflation Shock
    4. 2000 Dot-Com Tech Bubble Burst
    """

    HISTORICAL_SCENARIOS = {
        "GFC_2008": {
            "name": "2008 Global Financial Crisis",
            "period": "Sep 2008 - Mar 2009",
            "market_drawdown_pct": -48.0,
            "vix_peak": 80.0,
            "sector_shocks": {
                "Financials": -65.0,
                "Real Estate": -55.0,
                "Consumer Discretionary": -42.0,
                "Information Technology": -38.0,
                "Health Care": -22.0,
                "Consumer Staples": -18.0,
                "Utilities": -24.0,
                "Energy": -40.0,
                "Communication Services": -35.0,
            },
            "description": "Systemic banking crisis, global credit freeze, and widespread asset de-leveraging."
        },
        "COVID_2020": {
            "name": "2020 COVID-19 Liquidity Shock",
            "period": "Feb 2020 - Mar 2020",
            "market_drawdown_pct": -34.0,
            "vix_peak": 82.7,
            "sector_shocks": {
                "Energy": -52.0,
                "Consumer Discretionary": -38.0,
                "Financials": -35.0,
                "Industrials": -36.0,
                "Information Technology": -25.0,
                "Health Care": -15.0,
                "Consumer Staples": -12.0,
                "Utilities": -20.0,
                "Communication Services": -24.0,
            },
            "description": "Rapid pandemic lockdowns causing immediate global supply chain disruption and high-frequency cash dash."
        },
        "FED_TIGHTENING_2022": {
            "name": "2022 Fed Rate Shock & Inflation",
            "period": "Jan 2022 - Oct 2022",
            "market_drawdown_pct": -25.4,
            "vix_peak": 36.4,
            "sector_shocks": {
                "Information Technology": -33.0,
                "Communication Services": -38.0,
                "Consumer Discretionary": -37.0,
                "Real Estate": -28.0,
                "Financials": -12.0,
                "Health Care": -5.0,
                "Consumer Staples": -2.0,
                "Energy": +54.0,
                "Utilities": -1.0,
            },
            "description": "Fastest 500bps rate hiking cycle in 40 years, triggering multi-expansion collapse for high-duration growth assets."
        },
        "DOT_COM_2000": {
            "name": "2000 Dot-Com Bubble Collapse",
            "period": "Mar 2000 - Oct 2002",
            "market_drawdown_pct": -49.1,
            "vix_peak": 45.0,
            "sector_shocks": {
                "Information Technology": -78.0,
                "Communication Services": -68.0,
                "Consumer Discretionary": -30.0,
                "Financials": -8.0,
                "Health Care": -14.0,
                "Consumer Staples": +12.0,
                "Utilities": +5.0,
                "Energy": -2.0,
            },
            "description": "Valuation implosion in unprofitable tech and telecommunications infrastructure."
        }
    }

    def stress_test_asset(
        self,
        ticker: str,
        current_price: float,
        sector: str = "Information Technology",
        beta: float = 1.10
    ) -> Dict[str, Any]:
        """
        Calculates projected drawdown for a single asset across all 4 historical crises.
        """
        results = {}
        for scenario_id, data in self.HISTORICAL_SCENARIOS.items():
            base_sector_shock = data["sector_shocks"].get(sector, data["market_drawdown_pct"])
            # Adjusted by beta factor: shock * (1 + (beta - 1.0) * 0.5)
            adjusted_shock = base_sector_shock * (1.0 + (beta - 1.0) * 0.4)
            stressed_price = max(0.01, current_price * (1.0 + adjusted_shock / 100.0))
            loss_amount = current_price - stressed_price

            results[scenario_id] = {
                "scenario_name": data["name"],
                "period": data["period"],
                "projected_drawdown_pct": round(float(adjusted_shock), 2),
                "stressed_price": round(float(stressed_price), 2),
                "estimated_loss_per_share": round(float(loss_amount), 2),
                "description": data["description"]
            }

        return {
            "ticker": ticker,
            "current_price": current_price,
            "sector": sector,
            "beta": beta,
            "scenario_results": results
        }

    def stress_test_portfolio(
        self,
        holdings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Stress tests a multi-asset portfolio against historical crises.
        Each holding item: { ticker: str, weight: float, price: float, shares: float, sector: str, beta: float }
        """
        total_val = sum(h["shares"] * h["price"] for h in holdings)
        if total_val <= 0:
            return {"total_portfolio_value": 0, "scenario_impacts": {}}

        scenario_impacts = {}
        for scenario_id, data in self.HISTORICAL_SCENARIOS.items():
            stressed_portfolio_val = 0.0
            holding_breakdowns = []

            for h in holdings:
                curr_h_val = h["shares"] * h["price"]
                sector = h.get("sector", "Information Technology")
                beta = h.get("beta", 1.0)
                base_shock = data["sector_shocks"].get(sector, data["market_drawdown_pct"])
                adj_shock = base_shock * (1.0 + (beta - 1.0) * 0.4)
                stressed_h_val = max(0.0, curr_h_val * (1.0 + adj_shock / 100.0))
                stressed_portfolio_val += stressed_h_val

                holding_breakdowns.append({
                    "ticker": h["ticker"],
                    "current_value": round(curr_h_val, 2),
                    "stressed_value": round(stressed_h_val, 2),
                    "drawdown_pct": round(float(adj_shock), 2)
                })

            port_drawdown_pct = ((stressed_portfolio_val - total_val) / total_val) * 100.0
            scenario_impacts[scenario_id] = {
                "scenario_name": data["name"],
                "initial_value": round(total_val, 2),
                "stressed_value": round(stressed_portfolio_val, 2),
                "portfolio_drawdown_pct": round(float(port_drawdown_pct), 2),
                "dollar_drawdown": round(float(total_val - stressed_portfolio_val), 2),
                "holding_breakdowns": holding_breakdowns
            }

        return {
            "total_portfolio_value": round(total_val, 2),
            "scenario_impacts": scenario_impacts
        }
