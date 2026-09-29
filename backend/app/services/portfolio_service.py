"""
Portfolio Risk Analytics, Transaction Ingestion & Watchlist Service.
Utilizes PostgreSQL/TimescaleDB Repositories with transparent fallback.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.providers.market_data.factory import get_market_data_provider
from app.analytics.scenario import HistoricalStressTester
from app.utils.constants import SUPPORTED_UNIVERSE
from app.utils.validators import validate_ticker
from app.db.repositories.portfolio_repository import PortfolioRepository
from app.db.repositories.watchlist_repository import WatchlistRepository


class InMemoryPortfolioRepository:
    """Mock repository for user holdings and watchlist entries (fallback)."""

    def __init__(self):
        self._positions: Dict[str, Dict[str, Any]] = {
            "AAPL": {"ticker": "AAPL", "shares": 50.0, "avg_cost": 175.0, "sector": "Information Technology", "beta": 1.15},
            "NVDA": {"ticker": "NVDA", "shares": 25.0, "avg_cost": 420.0, "sector": "Information Technology", "beta": 1.75},
            "MSFT": {"ticker": "MSFT", "shares": 30.0, "avg_cost": 380.0, "sector": "Information Technology", "beta": 1.20},
            "JPM": {"ticker": "JPM", "shares": 40.0, "avg_cost": 185.0, "sector": "Financials", "beta": 0.95},
        }
        self._watchlist: Dict[str, Dict[str, Any]] = {
            "TSLA": {"ticker": "TSLA", "added_at": datetime.utcnow().isoformat(), "target_price": 280.0, "notes": "EV margin inflection watch"},
            "GOOGL": {"ticker": "GOOGL", "added_at": datetime.utcnow().isoformat(), "target_price": 190.0, "notes": "Gemini AI server monetization"}
        }

    def get_positions(self) -> List[Dict[str, Any]]:
        return list(self._positions.values())

    def add_transaction(self, ticker: str, shares: float, price: float, tx_type: str = "BUY") -> Dict[str, Any]:
        sym = ticker.upper()
        meta = SUPPORTED_UNIVERSE.get(sym, {"sector": "Information Technology", "beta": 1.0})
        
        if sym in self._positions:
            pos = self._positions[sym]
            if tx_type == "BUY":
                tot_shares = pos["shares"] + shares
                tot_cost = (pos["shares"] * pos["avg_cost"]) + (shares * price)
                pos["shares"] = tot_shares
                pos["avg_cost"] = round(tot_cost / tot_shares, 2)
            elif tx_type == "SELL":
                pos["shares"] = max(0.0, pos["shares"] - shares)
                if pos["shares"] == 0:
                    del self._positions[sym]
        else:
            if tx_type == "BUY":
                self._positions[sym] = {
                    "ticker": sym,
                    "shares": shares,
                    "avg_cost": price,
                    "sector": meta.get("sector", "Information Technology"),
                    "beta": meta.get("beta", 1.0)
                }
        return {"status": "SUCCESS", "ticker": sym, "type": tx_type, "shares": shares, "price": price}

    def get_watchlist(self) -> List[Dict[str, Any]]:
        return list(self._watchlist.values())

    def add_to_watchlist(self, ticker: str, target_price: Optional[float] = None, notes: Optional[str] = None) -> Dict[str, Any]:
        sym = ticker.upper()
        item = {
            "ticker": sym,
            "added_at": datetime.utcnow().isoformat(),
            "target_price": target_price,
            "notes": notes or ""
        }
        self._watchlist[sym] = item
        return item

    def remove_from_watchlist(self, ticker: str) -> bool:
        sym = ticker.upper()
        if sym in self._watchlist:
            del self._watchlist[sym]
            return True
        return False


class PortfolioService:

    def __init__(self):
        self.in_memory_repo = InMemoryPortfolioRepository()
        self.market_provider = get_market_data_provider()
        self.stress_tester = HistoricalStressTester()

    async def get_portfolio_summary(
        self,
        db: Optional[AsyncSession] = None,
        user_id: str = "usr_dev_admin_001"
    ) -> Dict[str, Any]:
        raw_positions = []
        if db:
            try:
                repo = PortfolioRepository(db)
                port = await repo.get_or_create_default(user_id)
                db_positions = await repo.get_positions(port.id)
                if db_positions:
                    raw_positions = [
                        {
                            "ticker": p.ticker,
                            "shares": p.shares,
                            "avg_cost": p.avg_cost,
                            "sector": p.sector,
                            "beta": p.beta
                        }
                        for p in db_positions
                    ]
            except Exception:
                raw_positions = []

        if not raw_positions:
            raw_positions = self.in_memory_repo.get_positions()

        enriched_positions = []
        total_value = 0.0
        weighted_beta_sum = 0.0

        for pos in raw_positions:
            sym = pos["ticker"]
            quote = await self.market_provider.get_quote(sym)
            cur_price = float(quote["price"])
            pos_val = cur_price * pos["shares"]
            total_value += pos_val

            enriched_positions.append({
                "ticker": sym,
                "shares": pos["shares"],
                "price": cur_price,
                "market_value": round(pos_val, 2),
                "avg_cost": pos["avg_cost"],
                "unrealized_pnl_pct": round(((cur_price - pos["avg_cost"]) / pos["avg_cost"]) * 100.0, 2),
                "sector": pos.get("sector", "Information Technology"),
                "beta": float(pos.get("beta", 1.0))
            })

        for p in enriched_positions:
            w = (p["market_value"] / total_value) if total_value > 0 else 0.0
            weighted_beta_sum += w * p["beta"]

        daily_var_95 = round(1.65 * 0.015 * weighted_beta_sum * 100.0, 2)

        return {
            "total_value": round(total_value, 2),
            "weighted_beta": round(weighted_beta_sum, 2),
            "daily_var_95_pct": daily_var_95,
            "positions_count": len(enriched_positions),
            "positions": enriched_positions
        }

    async def add_transaction(
        self,
        ticker: str,
        shares: float,
        price: float,
        tx_type: str = "BUY",
        db: Optional[AsyncSession] = None,
        user_id: str = "usr_dev_admin_001"
    ) -> Dict[str, Any]:
        sym = validate_ticker(ticker)
        res = None
        if db:
            try:
                repo = PortfolioRepository(db)
                port = await repo.get_or_create_default(user_id)
                meta = SUPPORTED_UNIVERSE.get(sym, {})
                res = await repo.add_transaction(
                    portfolio_id=port.id,
                    ticker=sym,
                    shares=shares,
                    price=price,
                    tx_type=tx_type,
                    sector=meta.get("sector", "Information Technology"),
                    beta=meta.get("beta", 1.0)
                )
            except Exception:
                res = None

        # Always sync with in-memory store
        in_mem_res = self.in_memory_repo.add_transaction(sym, shares, price, tx_type)
        return res or in_mem_res

    async def stress_test_portfolio(self, holdings: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        if holdings is None or len(holdings) == 0:
            summary = await self.get_portfolio_summary()
            holdings = summary["positions"]

        tot_val = sum(h["shares"] * h["price"] for h in holdings)
        stress_results = {}

        for crisis_id, crisis_meta in self.stress_tester.CRISES.items():
            stressed_portfolio_val = 0.0
            for h in holdings:
                sec = h.get("sector", "Information Technology")
                beta = float(h.get("beta", 1.0))
                p = float(h.get("price", 100.0))
                shs = float(h.get("shares", 1.0))
                
                base_drop = crisis_meta["sector_shocks"].get(sec, crisis_meta["market_drop"])
                adj_drop = base_drop * (1.0 + (beta - 1.0) * 0.4)
                stressed_p = max(0.01, p * (1.0 + adj_drop / 100.0))
                stressed_portfolio_val += stressed_p * shs

            loss_val = tot_val - stressed_portfolio_val
            drawdown_pct = round(-((loss_val / tot_val) * 100.0), 2) if tot_val > 0 else 0.0

            stress_results[crisis_id] = {
                "crisis_name": crisis_meta["name"],
                "period": crisis_meta["period"],
                "projected_portfolio_loss_dollars": round(loss_val, 2),
                "projected_drawdown_pct": drawdown_pct,
                "stressed_portfolio_value": round(stressed_portfolio_val, 2),
                "description": crisis_meta["desc"]
            }

        return {
            "initial_portfolio_value": round(tot_val, 2),
            "crises_stress_results": stress_results
        }

    # Watchlist methods
    async def get_watchlist(
        self,
        db: Optional[AsyncSession] = None,
        user_id: str = "usr_dev_admin_001"
    ) -> List[Dict[str, Any]]:
        raw = []
        if db:
            try:
                repo = WatchlistRepository(db)
                db_items = await repo.get_by_user(user_id)
                if db_items:
                    raw = [
                        {
                            "ticker": w.ticker,
                            "added_at": w.added_at.isoformat(),
                            "target_price": w.target_price,
                            "notes": w.notes
                        }
                        for w in db_items
                    ]
            except Exception:
                raw = []

        if not raw:
            raw = self.in_memory_repo.get_watchlist()

        enriched = []
        for w in raw:
            sym = w["ticker"]
            quote = await self.market_provider.get_quote(sym)
            enriched.append({
                **w,
                "current_price": float(quote["price"]),
                "change_pct": float(quote["change_pct"])
            })
        return enriched

    async def add_to_watchlist(
        self,
        ticker: str,
        target_price: Optional[float] = None,
        notes: Optional[str] = None,
        db: Optional[AsyncSession] = None,
        user_id: str = "usr_dev_admin_001"
    ) -> Dict[str, Any]:
        sym = validate_ticker(ticker)
        if db:
            try:
                repo = WatchlistRepository(db)
                w = await repo.add_item(user_id, sym, target_price, notes)
                return {
                    "ticker": w.ticker,
                    "added_at": w.added_at.isoformat(),
                    "target_price": w.target_price,
                    "notes": w.notes
                }
            except Exception:
                pass
        return self.in_memory_repo.add_to_watchlist(sym, target_price, notes)

    async def remove_from_watchlist(
        self,
        ticker: str,
        db: Optional[AsyncSession] = None,
        user_id: str = "usr_dev_admin_001"
    ) -> bool:
        sym = validate_ticker(ticker)
        if db:
            try:
                repo = WatchlistRepository(db)
                removed = await repo.remove_item(user_id, sym)
                if removed:
                    self.in_memory_repo.remove_from_watchlist(sym)
                    return True
            except Exception:
                pass
        return self.in_memory_repo.remove_from_watchlist(sym)


portfolio_service = PortfolioService()
