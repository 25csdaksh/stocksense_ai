"""
MARKETMIND AI — Unified Machine Learning & Quantitative Analytics Engine Facade.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

from anomaly.isolation_forest import MarketAnomalyDetector
from anomaly.garch_volatility import GARCHVolatilityModel
from anomaly.volume_spikes import VolumeSpikeDetector
from correlation.rolling_matrix import RollingCorrelationEngine
from correlation.granger_causality import GrangerCausalityAnalyzer
from correlation.network_graph import MarketRelationshipGraph
from scenario.monte_carlo import MonteCarloSimulator
from scenario.historical_shocks import HistoricalStressTester
from scenario.macro_simulator import MacroScenarioSimulator
from dna.factor_model import StockDNAProfiler
from dna.stock_dna_cluster import StockDNAClusterer


class MLEngine:
    """
    Central orchestration facade for all quantitative ML and econometric models.
    """

    def __init__(self):
        self.anomaly_detector = MarketAnomalyDetector()
        self.garch_model = GARCHVolatilityModel()
        self.volume_detector = VolumeSpikeDetector()
        self.correlation_engine = RollingCorrelationEngine()
        self.granger_analyzer = GrangerCausalityAnalyzer()
        self.network_graph_builder = MarketRelationshipGraph()
        self.monte_carlo_simulator = MonteCarloSimulator()
        self.historical_stress_tester = HistoricalStressTester()
        self.macro_simulator = MacroScenarioSimulator()
        self.dna_profiler = StockDNAProfiler()
        self.dna_clusterer = StockDNAClusterer()

    def run_anomaly_pipeline(self, df: pd.DataFrame, ticker: str) -> Dict[str, Any]:
        """Runs Isolation Forest, Volume spikes, and GARCH volatility models."""
        anomalies = self.anomaly_detector.detect_anomalies(df, ticker)
        volume_analysis = self.volume_detector.analyze(df, ticker)
        
        returns = np.log(df["close"] / df["close"].shift(1)).dropna().values
        garch_forecast = self.garch_model.forecast_volatility(returns, horizon=5)

        return {
            "ticker": ticker,
            "detected_anomalies": anomalies,
            "volume_profile": volume_analysis,
            "garch_volatility": garch_forecast
        }

    def run_monte_carlo(
        self,
        current_price: float,
        mu: float = 0.08,
        sigma: float = 0.25,
        days: int = 90,
        iterations: int = 5000,
        jump_intensity: float = 0.05
    ) -> Dict[str, Any]:
        """Runs Merton Jump Diffusion Monte Carlo simulation."""
        return self.monte_carlo_simulator.simulate(
            current_price=current_price,
            annualized_mu=mu,
            annualized_sigma=sigma,
            days=days,
            iterations=iterations,
            jump_intensity=jump_intensity
        )

    def run_historical_stress(
        self,
        ticker: str,
        current_price: float,
        sector: str = "Information Technology",
        beta: float = 1.10
    ) -> Dict[str, Any]:
        """Evaluates historical crisis drawdowns."""
        return self.historical_stress_tester.stress_test_asset(
            ticker=ticker,
            current_price=current_price,
            sector=sector,
            beta=beta
        )

    def run_macro_shock(
        self,
        ticker: str,
        current_price: float,
        sector: str = "Information Technology",
        beta: float = 1.10,
        rate_shock_bps: float = 100.0,
        inflation_shock_pct: float = 1.5,
        oil_shock_pct: float = 20.0,
        gdp_shock_pct: float = -1.0,
        usd_shock_pct: float = 5.0
    ) -> Dict[str, Any]:
        """Simulates price impact of macroeconomic parameter shocks."""
        return self.macro_simulator.simulate_macro_shock(
            ticker=ticker,
            current_price=current_price,
            sector=sector,
            beta=beta,
            rate_shock_bps=rate_shock_bps,
            inflation_shock_pct=inflation_shock_pct,
            oil_shock_pct=oil_shock_pct,
            gdp_shock_pct=gdp_shock_pct,
            usd_shock_pct=usd_shock_pct
        )

    def calculate_stock_dna(
        self,
        ticker: str,
        fundamentals: Dict[str, Any],
        price_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculates 5-factor DNA vector."""
        return self.dna_profiler.calculate_dna(ticker, fundamentals, price_metrics)

    def build_relationship_graph(
        self,
        returns_df: pd.DataFrame,
        metadata_map: Dict[str, Dict[str, Any]],
        threshold: float = 0.50
    ) -> Dict[str, Any]:
        """Builds relationship network graph."""
        builder = MarketRelationshipGraph(correlation_threshold=threshold)
        return builder.build_network(returns_df, metadata_map)


# Global Singleton Instance
ml_engine = MLEngine()


if __name__ == "__main__":
    print("MARKETMIND ML Engine initialized successfully.")
    # Smoke test Monte Carlo
    res = ml_engine.run_monte_carlo(current_price=180.0, days=30, iterations=1000)
    print(f"Monte Carlo smoke test: VaR 95% = {res['value_at_risk_95_pct']}%, P50 Target = ${res['expected_terminal_price_p50']}")
