import httpx
import asyncio
from abc import ABC, abstractmethod
from typing import List, Tuple
from datetime import datetime
from app.schemas.market_data import CryptoPrice, Ticker, Period

class BaseCryptoClient(ABC):
    @abstractmethod
    async def get_current_price(self, ticker: Ticker) -> CryptoPrice:
        pass

    @abstractmethod
    async def get_history(self, ticker: Ticker, period: Period) -> List[Tuple[datetime, float]]:
        pass

class BinanceClient(BaseCryptoClient):
    BASE_URL = "https://api.binance.com/api/v3"

    async def get_current_price(self, ticker: Ticker) -> CryptoPrice:
        symbol = f"{ticker.value}USDT"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"{self.BASE_URL}/ticker/price", params={"symbol": symbol})
                return CryptoPrice(ticker=ticker, price=float(resp.json()["price"]), timestamp=datetime.now(), source="Binance")
            except Exception:
                raise

    async def get_history(self, ticker: Ticker, period: Period) -> List[Tuple[datetime, float]]:
        symbol = f"{ticker.value}USDT"

        if period == Period.HOUR_24:
            interval = "5m"
            limit = 288
        elif period == Period.DAY_7:
            interval = "1h"
            limit = 168
        elif period == Period.MONTH_1:
            interval = "4h"
            limit = 180
        else:
            interval = "1d"
            limit = 365

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/klines",
                    params={"symbol": symbol, "interval": interval, "limit": limit},
                    timeout=10.0
                )
                if resp.status_code != 200: return []

                return [(datetime.fromtimestamp(x[0]/1000), float(x[4])) for x in resp.json()]
            except Exception as e:
                print(f"Binance Error: {e}")
                return []

class CoinGeckoClient(BaseCryptoClient):
    BASE_URL = "https://api.coingecko.com/api/v3"
    TICKER_MAP = {Ticker.BTC: "bitcoin", Ticker.ETH: "ethereum", Ticker.SOL: "solana"}

    async def get_current_price(self, ticker: Ticker) -> CryptoPrice:
        coin_id = self.TICKER_MAP[ticker]
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/simple/price",
                    params={"ids": coin_id, "vs_currencies": "usd"},
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                val = resp.json().get(coin_id, {}).get("usd")
                if not val: raise ValueError("No price")
                return CryptoPrice(ticker=ticker, price=float(val), timestamp=datetime.now(), source="CoinGecko")
            except Exception:
                raise

    async def get_history(self, ticker: Ticker, period: Period) -> List[Tuple[datetime, float]]:
        coin_id = self.TICKER_MAP[ticker]

        days = "1"
        if period == Period.HOUR_24: days = "1"
        elif period == Period.DAY_7: days = "7"
        elif period == Period.MONTH_1: days = "30"
        elif period == Period.YEAR: days = "365"

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/coins/{coin_id}/market_chart",
                    params={"vs_currency": "usd", "days": days},
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=20.0
                )
                if resp.status_code != 200:
                    print(f"CoinGecko Error: {resp.status_code}")
                    return []

                prices = resp.json().get("prices", [])
                return [(datetime.fromtimestamp(x[0]/1000), x[1]) for x in prices]
            except Exception as e:
                print(f"Gecko Exception: {e}")
                return []