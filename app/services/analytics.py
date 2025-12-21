from typing import List, Tuple, Optional
from datetime import datetime
from app.schemas.market_data import Ticker, Period, ExchangeStats, ComparisonReport


class AnalyticsService:
    def calculate_stats(self, data: List[Tuple[datetime, float]]) -> Optional[ExchangeStats]:
        if not data: return None

        prices = [x[1] for x in data]
        min_p, max_p = min(prices), max(prices)
        avg_p = sum(prices) / len(prices)
        volatility = ((max_p - min_p) / min_p) * 100 if min_p > 0 else 0

        return ExchangeStats(
            min_price=round(min_p, 2),
            max_price=round(max_p, 2),
            avg_price=round(avg_p, 2),
            volatility_percent=round(volatility, 2)
        )

    def create_report(self, ticker: Ticker, period: Period, b_data: list, g_data: list) -> ComparisonReport:
        return ComparisonReport(
            ticker=ticker,
            period=period,
            timestamp=datetime.now(),
            binance_stats=self.calculate_stats(b_data),
            coingecko_stats=self.calculate_stats(g_data)
        )