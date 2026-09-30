"""
MarketMind AI — Unit Tests for Fundamentals Models, Validation, and Ratio Engine.
Phase 6.6: Tests strict model integrity, domain rules, zero-division safety,
negative values, and deterministic financial calculations.
"""
import pytest
from app.providers.fundamentals.models import (
    CompanyProfileData,
    IncomeStatementData,
    BalanceSheetData,
    CashFlowData,
    FinancialPeriodType,
    FundamentalDataStatus,
    FundamentalDataSource,
)
from app.providers.fundamentals.validator import (
    fundamentals_validator,
    FundamentalsValidationError,
)
from app.analytics.ratio_engine import ratio_engine
from app.providers.fundamentals.factory import get_fundamentals_provider


class TestFundamentalsModelsAndValidation:

    def test_1_company_profile_normalization(self):
        profile = CompanyProfileData(
            symbol="RELIANCE.NS",
            name="Reliance Industries",
            exchange="NSE",
            sector="Energy",
            country="IN",
            currency="INR",
            market_cap=20000000000000.0,
            data_source=FundamentalDataSource.INDIAN_PROVIDER,
            data_status=FundamentalDataStatus.DEMO,
        )
        assert profile.symbol == "RELIANCE.NS"
        assert profile.currency == "INR"
        assert profile.data_status == FundamentalDataStatus.DEMO

    def test_2_income_statement_validation_and_positive_revenue(self):
        raw = {
            "symbol": "TCS.NS",
            "fiscal_year": 2024,
            "fiscal_quarter": "FY",
            "revenue": 240000000000.0,
            "cost_of_revenue": 140000000000.0,
            "gross_profit": 100000000000.0,
            "operating_income": 60000000000.0,
            "net_income": 45000000000.0,
            "eps": 125.0,
        }
        validated = fundamentals_validator.validate_income_statement(raw)
        assert validated.symbol == "TCS.NS"
        assert validated.revenue == 240000000000.0
        assert validated.gross_profit == 100000000000.0
        assert validated.net_income == 45000000000.0

    def test_3_negative_net_income_allowed(self):
        raw = {
            "symbol": "TATAMOTORS.NS",
            "fiscal_year": 2020,
            "revenue": 150000000000.0,
            "net_income": -12000000000.0,  # Loss is allowed
        }
        validated = fundamentals_validator.validate_income_statement(raw)
        assert validated.net_income == -12000000000.0

    def test_4_negative_cash_flows_allowed(self):
        raw = {
            "symbol": "INFY.NS",
            "fiscal_year": 2024,
            "operating_cash_flow": 28000000000.0,
            "capital_expenditures": -5000000000.0,  # CapEx outflow
            "financing_cash_flow": -12000000000.0,
        }
        cf = fundamentals_validator.validate_cash_flow(raw)
        assert cf.capital_expenditures == -5000000000.0
        assert cf.free_cash_flow == 23000000000.0

    def test_5_invalid_negative_revenue_rejected(self):
        raw = {
            "symbol": "AAPL",
            "fiscal_year": 2024,
            "revenue": -1000.0,  # Invalid negative gross revenue
            "net_income": 500.0,
        }
        with pytest.raises(FundamentalsValidationError):
            fundamentals_validator.validate_income_statement(raw)

    def test_6_period_and_quarter_validation(self):
        assert fundamentals_validator.validate_fiscal_quarter("Q3") == "Q3"
        assert fundamentals_validator.validate_fiscal_quarter("fy") == "FY"
        assert fundamentals_validator.validate_fiscal_year(2025) == 2025

        with pytest.raises(FundamentalsValidationError):
            fundamentals_validator.validate_fiscal_year(1980)

        with pytest.raises(FundamentalsValidationError):
            fundamentals_validator.validate_fiscal_quarter("INVALID_Q")


class TestRatioEngine:

    def test_7_profitability_ratios(self):
        inc = IncomeStatementData(
            symbol="TEST.NS",
            period_end="2024-12-31",
            fiscal_year=2024,
            revenue=1000.0,
            gross_profit=400.0,
            operating_income=250.0,
            ebitda=300.0,
            net_income=180.0,
        )
        bal = BalanceSheetData(
            symbol="TEST.NS",
            period_end="2024-12-31",
            fiscal_year=2024,
            total_assets=2000.0,
            total_liabilities=800.0,
            total_equity=1200.0,
        )
        ratios = ratio_engine.calculate_profitability(inc, bal)
        assert ratios.gross_margin_pct == 40.0
        assert ratios.operating_margin_pct == 25.0
        assert ratios.ebitda_margin_pct == 30.0
        assert ratios.net_margin_pct == 18.0
        assert ratios.roe_pct == 15.0  # 180 / 1200 * 100
        assert ratios.roa_pct == 9.0   # 180 / 2000 * 100

    def test_8_zero_division_protection(self):
        # Revenue is 0.0 or None
        inc = IncomeStatementData(
            symbol="ZERO.NS",
            period_end="2024-12-31",
            fiscal_year=2024,
            revenue=0.0,
            net_income=50.0,
        )
        ratios = ratio_engine.calculate_profitability(inc, None)
        assert ratios.gross_margin_pct is None
        assert ratios.net_margin_pct is None

    def test_9_leverage_and_altman_z_score(self):
        inc = IncomeStatementData(
            symbol="HEALTHY.NS",
            period_end="2024-12-31",
            fiscal_year=2024,
            revenue=1000.0,
            ebit=200.0,
            operating_income=200.0,
            interest_expense=20.0,
            net_income=150.0,
        )
        bal = BalanceSheetData(
            symbol="HEALTHY.NS",
            period_end="2024-12-31",
            fiscal_year=2024,
            total_current_assets=500.0,
            current_liabilities=200.0,
            retained_earnings=400.0,
            total_assets=1000.0,
            total_debt=300.0,
            total_liabilities=400.0,
            total_equity=600.0,
        )
        lev = ratio_engine.calculate_leverage(inc, bal, market_cap=1200.0)
        assert lev.debt_to_equity == 0.5
        assert lev.interest_coverage == 10.0
        assert lev.altman_z_score is not None
        assert lev.altman_z_score >= 3.0
        assert lev.health_score in ["STRONG", "EXCELLENT"]

    def test_10_liquidity_and_efficiency(self):
        inc = IncomeStatementData(
            symbol="EFF.NS",
            period_end="2024-12-31",
            fiscal_year=2024,
            revenue=2000.0,
            cost_of_revenue=1200.0,
            net_income=200.0,
        )
        bal = BalanceSheetData(
            symbol="EFF.NS",
            period_end="2024-12-31",
            fiscal_year=2024,
            cash_and_equivalents=300.0,
            receivables=200.0,
            inventory=400.0,
            total_current_assets=1000.0,
            current_liabilities=500.0,
            total_assets=2500.0,
            total_liabilities=1000.0,
            total_equity=1500.0,
        )
        liq = ratio_engine.calculate_liquidity(bal)
        eff = ratio_engine.calculate_efficiency(inc, bal)

        assert liq.current_ratio == 2.0  # 1000 / 500
        assert liq.quick_ratio == 1.0    # (300 + 200) / 500
        assert eff.asset_turnover == 0.8  # 2000 / 2500
        assert eff.inventory_turnover == 3.0  # 1200 / 400


class TestProviderRoutingAndProvenance:

    def test_11_provider_factory_routing(self):
        p_indian = get_fundamentals_provider("RELIANCE.NS")
        p_us = get_fundamentals_provider("AAPL")

        assert p_indian.provider_name == "INDIAN_PROVIDER"
        assert p_us.provider_name == "US_PROVIDER"

    @pytest.mark.asyncio
    async def test_12_indian_provider_provenance(self):
        p = get_fundamentals_provider("INFY.NS")
        overview = await p.get_fundamentals("INFY.NS")
        assert overview is not None
        assert overview.currency == "INR"
        assert overview.data_source == FundamentalDataSource.INDIAN_PROVIDER
        assert overview.data_status == FundamentalDataStatus.DEMO
