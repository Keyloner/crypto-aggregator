from datetime import datetime, timedelta
import pandas as pd
import os
from app.schemas.market_data import Ticker, AnalyticsReport, Period

class AnalyticsService:
    FILENAME = "history.csv"

    def get_report(self, ticker: Ticker, period: Period) -> AnalyticsReport:
        if not os.path.exists(self.FILENAME):
            raise FileNotFoundError("Нет данных для анализа")

        df = pd.read_csv(self.FILENAME)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df[df["ticker"] == ticker.value]


        if period != Period.ALL:
            now = datetime.now()
            cutoff = now #время отсечения

            if period == Period.HOUR_1:
                cutoff = now-timedelta(hours=1)
            elif period == Period.HOUR_24:
                cutoff = now - timedelta(hours=24)
            elif period == Period.DAY_7:
                cutoff = now - timedelta(days=7)

            df = df[df["timestamp"] >= cutoff]






        if df.empty:
            raise ValueError(f"Нет истории данных для {ticker.value}")

        min_price = df["price"].min()
        max_price = df["price"].max()
        avg_price = df["price"].mean()
        #расчет разброса в процентах
        spread = ((max_price - min_price) / min_price) * 100

        std_dev = df["price"].std()
        #замена Nan на 0
        if pd.isna(std_dev):
            std_dev = 0
        #границы : среднее +/- 2 откл
        upper_bound = avg_price+(2*std_dev)
        lower_bound = avg_price-(2*std_dev)

        #поиск цен которые вылетели за границы
        outliers_df = df[
            (df["price"] > upper_bound)|
            (df["price"] < lower_bound)
            ]
        outliers_count = len(outliers_df)

        last_timestamp = pd.to_datetime(df["timestamp"].iloc[-1])

        return AnalyticsReport(
            ticker=ticker,
            min_price=round(min_price, 2),
            max_price=round(max_price, 2),
            avg_price=round(avg_price, 2),
            spread_percentage=round(spread, 4),
            outliers_count = outliers_count,
            timestamp=last_timestamp
        )
