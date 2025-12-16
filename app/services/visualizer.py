import matplotlib
#Переключаем Matplotlib в режим для сервера
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import io
import os
from app.schemas.market_data import Ticker, Period

class GraphService:
    FILENAME = "history.csv"

    def create_price_chart(self, ticker: Ticker, period: Period) -> bytes:
        if not os.path.exists(self.FILENAME):
            raise FileNotFoundError("Нет данных")

        df = pd.read_csv(self.FILENAME)
        df = df[df["ticker"] == ticker.value]

        if period != Period.ALL:
            now = datetime.now()
            if period == Period.HOUR_1:
                cutoff = now - timedelta(hours=1)
            elif period == Period.HOUR_24:
                cutoff = now - timedelta(hours=24)
            elif period == Period.DAY_7:
                cutoff = now - timedelta(days=7)
            else:
                cutoff = now

            df = df[df["timestamp"] >= cutoff]

        if df.empty:
            raise ValueError(f"Нет данных для графика {ticker.value} ({period.value})")

        df = df.sort_values("timestamp")

        plt.figure(figsize = (12,7))
        plt.plot(df["timestamp"],df["price"],marker="o",linestyle="-")

        plt.title(f"Price History: {ticker.value} ({period.value})")
        plt.xlabel("Time")
        plt.ylabel("Price (USD)")
        plt.grid(True)
        plt.xticks(rotation=45)  # Наклонить подписи дат
        plt.tight_layout()  # Чтобы подписи не обрезались

        #Сохраняем в оперативную память
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        #Перематываем в начало
        buf.seek(0)

        return buf.getvalue()
