# MARKETMIND AI — Quantitative & ML Methodology

## 1. Anomaly Detection Pipeline

### A. Isolation Forest on Multi-Factor Vectors
The feature vector $\mathbf{x}_t$ for asset $i$ at time $t$ is defined as:
$$\mathbf{x}_t = \left[ r_t, \; \Delta r_t, \; \frac{H_t - L_t}{C_t}, \; z_{\text{vol}, t}, \; \sigma_{5d, t} \right]^T$$
where:
- $r_t = \ln(C_t / C_{t-1})$ is log-return.
- $\Delta r_t = r_t - r_{t-1}$ is return acceleration.
- $z_{\text{vol}, t} = \frac{V_t - \mu_{20}(V)}{\sigma_{20}(V)}$ is volume Z-score.
- $\sigma_{5d, t}$ is 5-day realized volatility.

### B. GARCH(1,1) Conditional Volatility Process
Conditional variance $\sigma_t^2$ is estimated via Maximum Likelihood:
$$\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$
subject to $\omega > 0$, $\alpha \ge 0$, $\beta \ge 0$, $\alpha + \beta < 1$.

---

## 2. Stock DNA Multi-Factor Model

Five normalized percentile scores $S_k \in [0, 100]$ are computed:
1. **Value Factor ($S_{\text{val}}$)**:
   $$S_{\text{val}} = 0.45 \cdot \text{Norm}(\text{P/E})^{-1} + 0.35 \cdot \text{Norm}(\text{P/B})^{-1} + 0.20 \cdot \text{Norm}(\text{DivYield})$$
2. **Growth Factor ($S_{\text{gro}}$)**:
   $$S_{\text{gro}} = 0.50 \cdot \text{Norm}(\text{RevGrowth}_{\text{YoY}}) + 0.50 \cdot \text{Norm}(\text{NetIncGrowth}_{\text{YoY}})$$
3. **Quality Factor ($S_{\text{qua}}$)**:
   $$S_{\text{qua}} = 0.40 \cdot \text{Norm}(\text{ROE}) + 0.30 \cdot \text{Norm}(\text{ROA}) + 0.30 \cdot \text{Norm}(\text{D/E})^{-1}$$
4. **Momentum Factor ($S_{\text{mom}}$)**:
   $$S_{\text{mom}} = 0.40 \cdot \text{Norm}(R_{3m}) + 0.60 \cdot \text{Norm}(R_{12m})$$
5. **Low Volatility Factor ($S_{\text{vol}}$)**:
   $$S_{\text{vol}} = 0.50 \cdot \text{Norm}(\beta)^{-1} + 0.50 \cdot \text{Norm}(\sigma_{\text{ann}})^{-1}$$

---

## 3. Econometric Granger Causality Test

Tests the null hypothesis $H_0: \gamma_1 = \dots = \gamma_p = 0$ in the Vector Autoregressive (VAR) model:
$$Y_t = c + \sum_{k=1}^p \alpha_k Y_{t-k} + \sum_{k=1}^p \gamma_k X_{t-k} + \epsilon_t$$
using the Wald $F$-statistic:
$$F = \frac{(\text{RSS}_R - \text{RSS}_{UR}) / p}{\text{RSS}_{UR} / (T - 2p - 1)}$$
If $p < 0.05$, time series $X$ significantly Granger-causes time series $Y$ at lag $p$.
