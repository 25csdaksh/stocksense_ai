"""
Stochastic Scenario Simulation, Merton Jump Diffusion, Historical Stress & Macro Elasticity Models.
"""
from typing import Dict, Any, List, Optional
import numpy as np


class MonteCarloSimulator:
    """Simulates multi-step stochastic price trajectories with Merton's Jump Diffusion."""

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed

    def simulate(
        self,
        current_price: float,
        drift_annualized: float = 0.08,
        volatility_annualized: float = 0.25,
        days: int = 90,
        iterations: int = 5000,
        jump_intensity: float = 0.05,
        jump_mean: float = -0.05,
        jump_std: float = 0.15
    ) -> Dict[str, Any]:
        np.random.seed(self.random_seed)
        dt = 1.0 / 252.0
        steps = days

        k = np.exp(jump_mean + 0.5 * (jump_std ** 2)) - 1
        drift = (drift_annualized - 0.5 * (volatility_annualized ** 2) - jump_intensity * k) * dt
        vol = volatility_annualized * np.sqrt(dt)

        dW = np.random.normal(0, 1, size=(iterations, steps))
        poi = np.random.poisson(jump_intensity * dt, size=(iterations, steps))
        jumps = np.random.normal(jump_mean, jump_std, size=(iterations, steps)) * poi

        log_returns = drift + vol * dW + jumps
        cum_ret = np.cumsum(log_returns, axis=1)
        paths = current_price * np.exp(cum_ret)

        terminal_prices = paths[:, -1]
        terminal_returns = (terminal_prices - current_price) / current_price

        # Quantile Bands (Fan Chart)
        p10 = [current_price] + np.percentile(paths, 10, axis=0).tolist()
        p25 = [current_price] + np.percentile(paths, 25, axis=0).tolist()
        p50 = [current_price] + np.percentile(paths, 50, axis=0).tolist()
        p75 = [current_price] + np.percentile(paths, 75, axis=0).tolist()
        p90 = [current_price] + np.percentile(paths, 90, axis=0).tolist()

        fan_chart = [
            {
                "day": t,
                "p10": round(float(p10[t]), 2),
                "p25": round(float(p25[t]), 2),
                "p50": round(float(p50[t]), 2),
                "p75": round(float(p75[t]), 2),
                "p90": round(float(p90[t]), 2),
            }
            for t in range(steps + 1)
        ]

        var_95 = float(np.percentile(terminal_returns, 5) * 100.0)
        var_99 = float(np.percentile(terminal_returns, 1) * 100.0)
        tail_99 = terminal_returns[terminal_returns <= (var_99 / 100.0)]
        cvar_99 = float(np.mean(tail_99) * 100.0) if len(tail_99) > 0 else var_99

        counts, bin_edges = np.histogram(terminal_returns * 100.0, bins=25)
        hist_data = [
            {
                "range_label": f"{bin_edges[i]:.1f}% to {bin_edges[i+1]:.1f}%",
                "midpoint": round(float((bin_edges[i] + bin_edges[i+1]) / 2), 2),
                "frequency": int(counts[i])
            }
            for i in range(len(counts))
        ]

        return {
            "initial_price": current_price,
            "days": days,
            "iterations": iterations,
            "annualized_drift_pct": round(drift_annualized * 100.0, 2),
            "annualized_volatility_pct": round(volatility_annualized * 100.0, 2),
            "expected_terminal_price_p50": round(float(p50[-1]), 2),
            "terminal_p10_price": round(float(p10[-1]), 2),
            "terminal_p90_price": round(float(p90[-1]), 2),
            "value_at_risk_95_pct": round(var_95, 2),
            "value_at_risk_99_pct": round(var_99, 2),
            "cvar_expected_shortfall_99_pct": round(cvar_99, 2),
            "probability_of_profit_pct": round(float(np.mean(terminal_returns > 0) * 100.0), 2),
            "prob_loss_exceeding_10pct": round(float(np.mean(terminal_returns < -0.10) * 100.0), 2),
            "prob_gain_exceeding_20pct": round(float(np.mean(terminal_returns > 0.20) * 100.0), 2),
            "fan_chart": fan_chart,
            "distribution_histogram": hist_data,
        }


class HistoricalStressTester:
    """Evaluates crisis drawdown replay across 4 major macroeconomic stress events."""

    CRISES = {
        "GFC_2008": {"name": "2008 Global Financial Crisis", "period": "Sep 2008 - Mar 2009", "market_drop": -48.0, "sector_shocks": {"Financials": -65.0, "Information Technology": -38.0, "Consumer Discretionary": -42.0}, "desc": "Subprime mortgage collapse, Lehman bankruptcy and systemic credit freeze."},
        "COVID_2020": {"name": "2020 COVID-19 Flash Crash", "period": "Feb 2020 - Mar 2020", "market_drop": -34.0, "sector_shocks": {"Energy": -52.0, "Information Technology": -25.0, "Consumer Discretionary": -38.0}, "desc": "Global pandemic lockdowns and unprecedented dash for dollar cash liquidity."},
        "FED_TIGHTENING_2022": {"name": "2022 Fed Rate Shock & Inflation", "period": "Jan 2022 - Oct 2022", "market_drop": -25.4, "sector_shocks": {"Information Technology": -33.0, "Communication Services": -38.0, "Energy": +54.0}, "desc": "Aggressive 500bps monetary tightening cycle and valuation compression for high-duration assets."},
        "DOT_COM_2000": {"name": "2000 Dot-Com Tech Bubble Burst", "period": "Mar 2000 - Oct 2002", "market_drop": -49.1, "sector_shocks": {"Information Technology": -78.0, "Communication Services": -68.0, "Financials": -8.0}, "desc": "Speculative valuation implosion across internet and optical networking infrastructure."}
    }

    def stress_test(self, ticker: str, current_price: float, sector: str = "Information Technology", beta: float = 1.10) -> Dict[str, Any]:
        results = {}
        for c_id, data in self.CRISES.items():
            base_drop = data["sector_shocks"].get(sector, data["market_drop"])
            adj_drop = base_drop * (1.0 + (beta - 1.0) * 0.4)
            stressed_p = max(0.01, current_price * (1.0 + adj_drop / 100.0))
            loss = current_price - stressed_p

            results[c_id] = {
                "scenario_name": data["name"],
                "period": data["period"],
                "projected_drawdown_pct": round(float(adj_drop), 2),
                "stressed_price": round(float(stressed_p), 2),
                "estimated_loss_per_share": round(float(loss), 2),
                "description": data["desc"]
            }

        return {
            "ticker": ticker,
            "current_price": current_price,
            "sector": sector,
            "beta": beta,
            "scenario_results": results
        }


class MacroScenarioSimulator:
    """Multi-variable macroeconomic factor sensitivity model."""

    SECTOR_ELASTICITY = {
        "Information Technology": {"rates": -0.065, "inflation": -0.35, "oil": -0.15, "gdp": 1.20},
        "Financials": {"rates": 0.045, "inflation": 0.10, "oil": 0.05, "gdp": 1.10},
        "Energy": {"rates": -0.015, "inflation": 0.60, "oil": 0.85, "gdp": 0.90},
        "Consumer Discretionary": {"rates": -0.055, "inflation": -0.50, "oil": -0.30, "gdp": 1.35},
        "Health Care": {"rates": -0.025, "inflation": -0.15, "oil": -0.05, "gdp": 0.50},
        "Index ETF": {"rates": -0.045, "inflation": -0.25, "oil": -0.10, "gdp": 1.00}
    }

    def simulate(
        self,
        ticker: str,
        current_price: float,
        sector: str = "Information Technology",
        beta: float = 1.10,
        rate_shock_bps: float = 100.0,
        inflation_shock_pct: float = 1.5,
        oil_shock_pct: float = 20.0,
        gdp_shock_pct: float = -1.0
    ) -> Dict[str, Any]:
        sens = self.SECTOR_ELASTICITY.get(sector, {"rates": -0.045, "inflation": -0.25, "oil": -0.10, "gdp": 1.0})
        rate_c = (rate_shock_bps / 100.0) * sens["rates"] * 100.0
        inf_c = inflation_shock_pct * sens["inflation"]
        oil_c = oil_shock_pct * sens["oil"]
        gdp_c = gdp_shock_pct * sens["gdp"]

        tot_unscaled = rate_c + inf_c + oil_c + gdp_c
        total_ret = tot_unscaled * (1.0 + (beta - 1.0) * 0.3)
        proj_p = max(0.01, current_price * (1.0 + total_ret / 100.0))

        return {
            "ticker": ticker,
            "current_price": current_price,
            "projected_price": round(float(proj_p), 2),
            "total_projected_return_pct": round(float(total_ret), 2),
            "dollar_impact_per_share": round(float(proj_p - current_price), 2),
            "factor_decomposition": {
                "rates_effect_pct": round(float(rate_c), 2),
                "inflation_effect_pct": round(float(inf_c), 2),
                "oil_effect_pct": round(float(oil_c), 2),
                "gdp_effect_pct": round(float(gdp_c), 2)
            }
        }
