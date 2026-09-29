"""
Monte Carlo Simulation Engine with Geometric Brownian Motion & Poisson Jump Diffusion.
"""
from typing import Dict, Any, List
import numpy as np


class MonteCarloSimulator:
    """
    Simulates asset price paths using Merton's Jump-Diffusion Model:
      dS_t = (\mu - \lambda k) S_t dt + \sigma S_t dW_t + J_t S_t dN_t
    where N_t is a Poisson process with intensity \lambda, and \ln(1 + J_t) ~ N(\mu_J, \sigma_J^2).
    """

    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed

    def simulate(
        self,
        current_price: float,
        annualized_mu: float = 0.08,
        annualized_sigma: float = 0.25,
        days: int = 90,
        iterations: int = 5000,
        jump_intensity: float = 0.05,  # Expected jumps per year
        jump_mean: float = -0.05,      # Average jump size
        jump_std: float = 0.15         # Jump size volatility
    ) -> Dict[str, Any]:
        """
        Executes Monte Carlo simulation and returns quantile bands, VaR/CVaR, and sampled paths.
        """
        np.random.seed(self.random_seed)
        dt = 1.0 / 252.0  # Daily time step in years
        total_steps = days

        # Compensator k = E[J] = exp(mu_J + 0.5 * sigma_J^2) - 1
        k = np.exp(jump_mean + 0.5 * (jump_std ** 2)) - 1
        drift = (annualized_mu - 0.5 * (annualized_sigma ** 2) - jump_intensity * k) * dt
        vol = annualized_sigma * np.sqrt(dt)

        # Standard normal increments for continuous diffusion: shape (iterations, steps)
        dW = np.random.normal(0, 1, size=(iterations, total_steps))
        
        # Poisson jumps
        poi = np.random.poisson(jump_intensity * dt, size=(iterations, total_steps))
        jump_sizes = np.random.normal(jump_mean, jump_std, size=(iterations, total_steps)) * poi

        # Daily log returns
        log_returns = drift + vol * dW + jump_sizes

        # Cumulative price trajectories
        cum_returns = np.cumsum(log_returns, axis=1)
        price_paths = current_price * np.exp(cum_returns)

        # Terminal prices at day T
        terminal_prices = price_paths[:, -1]
        terminal_returns = (terminal_prices - current_price) / current_price

        # Quantile Trajectories for Fan Chart (P10, P25, P50, P75, P90)
        time_steps = list(range(0, total_steps + 1))
        p10_path = [current_price] + np.percentile(price_paths, 10, axis=0).tolist()
        p25_path = [current_price] + np.percentile(price_paths, 25, axis=0).tolist()
        p50_path = [current_price] + np.percentile(price_paths, 50, axis=0).tolist()
        p75_path = [current_price] + np.percentile(price_paths, 75, axis=0).tolist()
        p90_path = [current_price] + np.percentile(price_paths, 90, axis=0).tolist()

        # Risk Metrics
        var_95_return = np.percentile(terminal_returns, 5)
        var_99_return = np.percentile(terminal_returns, 1)

        # Conditional VaR (Expected Shortfall) = mean of returns worse than VaR
        tail_95 = terminal_returns[terminal_returns <= var_95_return]
        tail_99 = terminal_returns[terminal_returns <= var_99_return]
        cvar_95_return = float(np.mean(tail_95)) if len(tail_95) > 0 else var_95_return
        cvar_99_return = float(np.mean(tail_99)) if len(tail_99) > 0 else var_99_return

        prob_profit = float(np.mean(terminal_returns > 0) * 100)
        prob_loss_gt_10pct = float(np.mean(terminal_returns < -0.10) * 100)
        prob_gain_gt_20pct = float(np.mean(terminal_returns > 0.20) * 100)

        # Sample 15 paths for frontend visualization
        sample_paths = []
        for i in range(min(15, iterations)):
            sample_paths.append([current_price] + [round(float(p), 2) for p in price_paths[i]])

        # Create histogram bins for distribution visualization
        hist_counts, bin_edges = np.histogram(terminal_returns * 100, bins=25)
        hist_data = []
        for i in range(len(hist_counts)):
            hist_data.append({
                "range_label": f"{bin_edges[i]:.1f}% to {bin_edges[i+1]:.1f}%",
                "midpoint": round(float((bin_edges[i] + bin_edges[i+1]) / 2), 2),
                "frequency": int(hist_counts[i])
            })

        fan_chart_data = []
        for t in range(len(time_steps)):
            fan_chart_data.append({
                "day": t,
                "p10": round(float(p10_path[t]), 2),
                "p25": round(float(p25_path[t]), 2),
                "p50": round(float(p50_path[t]), 2),
                "p75": round(float(p75_path[t]), 2),
                "p90": round(float(p90_path[t]), 2),
            })

        return {
            "initial_price": current_price,
            "days": days,
            "iterations": iterations,
            "annualized_drift_pct": round(annualized_mu * 100, 2),
            "annualized_volatility_pct": round(annualized_sigma * 100, 2),
            "expected_terminal_price_p50": round(float(p50_path[-1]), 2),
            "terminal_p10_price": round(float(p10_path[-1]), 2),
            "terminal_p90_price": round(float(p90_path[-1]), 2),
            "value_at_risk_95_pct": round(float(var_95_return * 100), 2),
            "value_at_risk_99_pct": round(float(var_99_return * 100), 2),
            "cvar_expected_shortfall_95_pct": round(float(cvar_95_return * 100), 2),
            "cvar_expected_shortfall_99_pct": round(float(cvar_99_return * 100), 2),
            "probability_of_profit_pct": round(prob_profit, 2),
            "prob_loss_exceeding_10pct": round(prob_loss_gt_10pct, 2),
            "prob_gain_exceeding_20pct": round(prob_gain_gt_20pct, 2),
            "fan_chart": fan_chart_data,
            "distribution_histogram": hist_data,
            "sample_paths": sample_paths
        }
