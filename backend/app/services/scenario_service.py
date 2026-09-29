"""
Scenario Simulation, Historical Stress Testing & Macro Elasticity Service.
"""
from typing import Dict, Any
from app.providers.market_data.factory import get_market_data_provider
from app.analytics.scenario import MonteCarloSimulator, HistoricalStressTester, MacroScenarioSimulator
from app.utils.constants import SUPPORTED_UNIVERSE, FINANCIAL_DISCLAIMER
from app.utils.validators import validate_ticker, validate_monte_carlo_params


class ScenarioService:

    def __init__(self):
        self.market_provider = get_market_data_provider()
        self.monte_carlo = MonteCarloSimulator()
        self.historical_tester = HistoricalStressTester()
        self.macro_simulator = MacroScenarioSimulator()

    async def run_monte_carlo(
        self,
        ticker: str = "AAPL",
        drift_annualized: float = 0.08,
        volatility_annualized: float = 0.25,
        days: int = 90,
        iterations: int = 5000,
        jump_intensity: float = 0.05
    ) -> Dict[str, Any]:
        sym = validate_ticker(ticker)
        days, iters = validate_monte_carlo_params(days, iterations)
        quote = await self.market_provider.get_quote(sym)
        current_price = float(quote["price"])

        res = self.monte_carlo.simulate(
            current_price=current_price,
            drift_annualized=drift_annualized,
            volatility_annualized=volatility_annualized,
            days=days,
            iterations=iters,
            jump_intensity=jump_intensity
        )
        res["ticker"] = sym
        res["disclaimer"] = FINANCIAL_DISCLAIMER
        return res

    async def run_historical_stress(
        self,
        ticker: str = "AAPL",
        current_price: float = None,
        sector: str = None,
        beta: float = None
    ) -> Dict[str, Any]:
        sym = validate_ticker(ticker)
        meta = SUPPORTED_UNIVERSE.get(sym, {})
        
        if current_price is None:
            quote = await self.market_provider.get_quote(sym)
            current_price = float(quote["price"])
        if sector is None:
            sector = meta.get("sector", "Information Technology")
        if beta is None:
            beta = float(meta.get("beta", 1.10))

        res = self.historical_tester.stress_test(
            ticker=sym,
            current_price=current_price,
            sector=sector,
            beta=beta
        )
        res["disclaimer"] = FINANCIAL_DISCLAIMER
        return res

    async def run_macro_shock(
        self,
        ticker: str = "AAPL",
        rate_shock_bps: float = 100.0,
        inflation_shock_pct: float = 1.5,
        oil_shock_pct: float = 20.0,
        gdp_shock_pct: float = -1.0
    ) -> Dict[str, Any]:
        sym = validate_ticker(ticker)
        quote = await self.market_provider.get_quote(sym)
        current_price = float(quote["price"])
        meta = SUPPORTED_UNIVERSE.get(sym, {})
        sector = meta.get("sector", "Information Technology")
        beta = float(meta.get("beta", 1.10))

        res = self.macro_simulator.simulate(
            ticker=sym,
            current_price=current_price,
            sector=sector,
            beta=beta,
            rate_shock_bps=rate_shock_bps,
            inflation_shock_pct=inflation_shock_pct,
            oil_shock_pct=oil_shock_pct,
            gdp_shock_pct=gdp_shock_pct
        )
        res["disclaimer"] = FINANCIAL_DISCLAIMER
        return res


scenario_service = ScenarioService()
