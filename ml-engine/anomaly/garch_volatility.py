"""
GARCH(1,1) Volatility Modeling and Volatility Regime Shift Detector.
"""
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from scipy.optimize import minimize


class GARCHVolatilityModel:
    """
    Fits a standard GARCH(1,1) process:
      r_t = \mu + \epsilon_t
      \epsilon_t = \sigma_t z_t, z_t ~ N(0, 1)
      \sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2
    subject to \omega > 0, \alpha >= 0, \beta >= 0, \alpha + \beta < 1.
    """

    def __init__(self):
        self.omega: Optional[float] = None
        self.alpha: Optional[float] = None
        self.beta: Optional[float] = None
        self.mu: Optional[float] = None
        self.conditional_volatilities: List[float] = []

    def fit(self, returns: np.ndarray) -> "GARCHVolatilityModel":
        """
        Fits GARCH(1,1) parameters using Maximum Likelihood Estimation (MLE).
        """
        returns = np.asarray(returns, dtype=float)
        # Drop NaNs or Infs
        returns = returns[np.isfinite(returns)]
        if len(returns) < 30:
            # Fallback estimation for small sample
            self.omega = float(np.var(returns) * 0.1) if len(returns) > 0 else 0.0001
            self.alpha = 0.10
            self.beta = 0.85
            self.mu = float(np.mean(returns)) if len(returns) > 0 else 0.0
            return self

        mu_init = np.mean(returns)
        var_init = np.var(returns)
        omega_init = var_init * 0.05
        alpha_init = 0.08
        beta_init = 0.88

        # Bounds: omega > 0, alpha in [0, 1], beta in [0, 1]
        bounds = ((1e-7, None), (0.001, 0.4), (0.4, 0.98))
        
        def garch_log_likelihood(params):
            omega, alpha, beta = params
            if alpha + beta >= 0.999:
                return 1e10  # Stationarity penalty
            
            residuals = returns - mu_init
            n = len(residuals)
            sigma2 = np.zeros(n)
            sigma2[0] = var_init

            for t in range(1, n):
                sigma2[t] = omega + alpha * (residuals[t - 1] ** 2) + beta * sigma2[t - 1]

            # Gaussian negative log-likelihood
            ll = 0.5 * np.sum(np.log(2 * np.pi) + np.log(sigma2) + (residuals ** 2) / sigma2)
            return ll if np.isfinite(ll) else 1e10

        res = minimize(
            garch_log_likelihood,
            [omega_init, alpha_init, beta_init],
            bounds=bounds,
            method="L-BFGS-B"
        )

        if res.success:
            self.omega, self.alpha, self.beta = res.x
        else:
            self.omega, self.alpha, self.beta = omega_init, alpha_init, beta_init
        
        self.mu = mu_init
        return self

    def forecast_volatility(self, returns: np.ndarray, horizon: int = 5) -> Dict[str, Any]:
        """
        Computes conditional volatility time series and forecasts next N periods.
        """
        if self.omega is None:
            self.fit(returns)

        returns = np.asarray(returns, dtype=float)
        returns = returns[np.isfinite(returns)]
        n = len(returns)
        residuals = returns - self.mu

        sigma2 = np.zeros(n)
        sigma2[0] = np.var(returns) if n > 0 else 0.0004

        for t in range(1, n):
            sigma2[t] = self.omega + self.alpha * (residuals[t - 1] ** 2) + self.beta * sigma2[t - 1]

        annualized_cond_vol = np.sqrt(sigma2 * 252) * 100
        current_sigma2 = sigma2[-1] if n > 0 else 0.0004

        # Forecast forward
        long_term_var = self.omega / (1.0 - (self.alpha + self.beta))
        forecasted_vols = []
        sig2_f = current_sigma2
        for _ in range(horizon):
            sig2_f = self.omega + (self.alpha + self.beta) * sig2_f
            forecasted_vols.append(round(float(np.sqrt(sig2_f * 252) * 100), 2))

        # Check for volatility regime shift
        recent_vol = annualized_cond_vol[-1] if len(annualized_cond_vol) > 0 else 15.0
        historical_mean_vol = np.mean(annualized_cond_vol) if len(annualized_cond_vol) > 0 else 15.0
        vol_zscore = (recent_vol - historical_mean_vol) / (np.std(annualized_cond_vol) + 1e-6)

        return {
            "current_annualized_volatility_pct": round(float(recent_vol), 2),
            "historical_mean_volatility_pct": round(float(historical_mean_vol), 2),
            "volatility_zscore": round(float(vol_zscore), 2),
            "persistence_factor": round(float(self.alpha + self.beta), 4),
            "long_term_equilibrium_vol_pct": round(float(np.sqrt(max(0, long_term_var) * 252) * 100), 2),
            "forecast_next_days": forecasted_vols,
            "regime": "HIGH_VOLATILITY" if vol_zscore > 1.5 else ("LOW_VOLATILITY" if vol_zscore < -1.0 else "NORMAL_VOLATILITY")
        }
