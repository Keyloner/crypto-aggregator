import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import pandas as pd
import numpy as np
from app.schemas.market_data import Ticker, Period
from app.services.aggregator import PriceAggregator


class GraphService:
    def __init__(self):
        self.aggregator = PriceAggregator()

    async def create_comparison_chart(self, ticker: Ticker, period: Period) -> bytes:
        binance_data, gecko_data = await self.aggregator.get_history(ticker, period)

        if not binance_data and not gecko_data:
            raise ValueError("Нет данных для графика")

        plt.figure(figsize=(12,7))

        if binance_data:
            self._plot_series_with_stats(binance_data, "Binance", "blue")

        if gecko_data:
            self._plot_series_with_stats(gecko_data, "CoinGecko", "green")


        plt.title(f"{ticker.value} Analysis ({period.value})")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.grid(True, alpha=0.2)
        plt.gcf().autofmt_xdate()
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        plt.close()
        buf.seek(0)
        return buf.getvalue()

    def _plot_series_with_stats(self, data, label, color):
        df = pd.DataFrame(data, columns=["timestamp", "price"])

        # Основная линия цены
        plt.plot(df["timestamp"], df["price"], label=label, color=color, linewidth=2, alpha=0.9)

        # СКОЛЬЗЯЩАЯ СРЕДНЯЯ
        window_size = max(5, int(len(df) * 0.1))

        rolling_mean = df["price"].rolling(window=window_size, center=True).mean()
        rolling_std = df["price"].rolling(window=window_size, center=True).std()

        rolling_mean = rolling_mean.bfill().ffill()
        rolling_std = rolling_std.bfill().ffill()

        plt.plot(df["timestamp"], rolling_mean, color=color, linestyle='--', alpha=0.7, linewidth=1.5,
                 label=f"{label} Trend")

        # Правило 3 сигм
        SIGMA = 3
        upper_bound = rolling_mean + (SIGMA * rolling_std)
        lower_bound = rolling_mean - (SIGMA * rolling_std)


        outliers = df[(df["price"] > upper_bound) | (df["price"] < lower_bound)]

        if not outliers.empty:
            plt.scatter(
                outliers["timestamp"],
                outliers["price"],
                color="red", marker="x", s=40, zorder=6, label=f"{label} Anomaly"
            )

        min_idx = df["price"].idxmin()
        max_idx = df["price"].idxmax()

        plt.scatter(df.loc[max_idx, "timestamp"], df.loc[max_idx, "price"], color=color, marker="^", s=100,
                    edgecolors="black", zorder=7)
        plt.scatter(df.loc[min_idx, "timestamp"], df.loc[min_idx, "price"], color=color, marker="v", s=100,
                    edgecolors="black", zorder=7)