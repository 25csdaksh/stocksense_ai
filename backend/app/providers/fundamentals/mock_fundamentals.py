"""
Financial Statements & Normalized Fundamentals Provider.
"""
from typing import Dict, Any
from app.providers.fundamentals.base import FundamentalsProvider
from app.utils.constants import SUPPORTED_UNIVERSE


class MockFundamentalsProvider(FundamentalsProvider):

    async def get_overview(self, ticker: str) -> Dict[str, Any]:
        ticker = ticker.upper()
        meta = SUPPORTED_UNIVERSE.get(ticker, {
            "name": ticker,
            "sector": "Information Technology",
            "pe": 28.5,
            "pb": 6.4,
            "dividend_yield": 0.01,
            "beta": 1.10
        })

        return {
            "ticker": ticker,
            "name": meta["name"],
            "sector": meta["sector"],
            "valuation": {
                "pe_ratio": meta.get("pe", 28.5),
                "forward_pe": round(meta.get("pe", 28.5) * 0.88, 2),
                "pb_ratio": meta.get("pb", 6.4),
                "ev_ebitda": 22.4,
                "fcf_yield_pct": 3.8
            },
            "profitability": {
                "gross_margin_pct": 68.5,
                "operating_margin_pct": 34.2,
                "net_margin_pct": 26.8,
                "roe_pct": 38.4,
                "roa_pct": 16.2
            },
            "financial_health": {
                "current_ratio": 1.45,
                "debt_to_equity": 0.62,
                "interest_coverage_ratio": 18.5,
                "altman_z_score": 4.85,
                "health_score": "EXCELLENT"
            }
        }

    async def get_financial_statements(self, ticker: str, statement_type: str = "income") -> Dict[str, Any]:
        ticker = ticker.upper()
        if statement_type == "balance":
            return {
                "ticker": ticker,
                "statement_type": "balance_sheet",
                "periods": [
                    {"period": "2024-Q3", "cash_and_equivalents": 38_000_000_000, "total_assets": 365_000_000_000, "total_liabilities": 140_000_000_000, "stockholders_equity": 225_000_000_000},
                    {"period": "2023-FY", "cash_and_equivalents": 35_000_000_000, "total_assets": 350_000_000_000, "total_liabilities": 145_000_000_000, "stockholders_equity": 205_000_000_000}
                ]
            }
        elif statement_type == "cashflow":
            return {
                "ticker": ticker,
                "statement_type": "cash_flow",
                "periods": [
                    {"period": "2024-Q3", "operating_cash_flow": 28_000_000_000, "capital_expenditures": -8_500_000_000, "free_cash_flow": 19_500_000_000, "dividends_paid": -3_800_000_000},
                    {"period": "2023-FY", "operating_cash_flow": 110_000_000_000, "capital_expenditures": -32_000_000_000, "free_cash_flow": 78_000_000_000, "dividends_paid": -15_000_000_000}
                ]
            }
        else:
            return {
                "ticker": ticker,
                "statement_type": "income_statement",
                "periods": [
                    {"period": "2024-Q3", "total_revenue": 94_800_000_000, "gross_profit": 64_900_000_000, "operating_income": 32_400_000_000, "net_income": 25_400_000_000, "eps": 1.64},
                    {"period": "2023-FY", "total_revenue": 383_000_000_000, "gross_profit": 260_000_000_000, "operating_income": 128_000_000_000, "net_income": 97_000_000_000, "eps": 6.13}
                ]
            }
