import asyncio
import time
from typing import List, Tuple
from app.schemas.market_data import Ticker, CryptoPrice, Period
from app.services.api_clients import BinanceClient, CoinGeckoClient

# Глобальный кэш
CACHE = {}


class PriceAggregator:
    def __init__(self):
        self.clients = [BinanceClient(), CoinGeckoClient()]

    # Текущая цена
    async def get_prices(self, ticker: Ticker) -> List[CryptoPrice]:
        cache_key = f"price_{ticker.value}"
        if self._check_cache(cache_key): return CACHE[cache_key]["data"]

        tasks = [client.get_current_price(ticker) for client in self.clients]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        valid = [r for r in results if not isinstance(r, Exception)]

        if valid: self._set_cache(cache_key, valid, ttl=10)
        return valid

    # История
    async def get_history(self, ticker: Ticker, period: Period) -> Tuple[list, list]:
        cache_key = f"hist_{ticker.value}_{period.value}"
        if self._check_cache(cache_key): return CACHE[cache_key]["data"]

        b_task = self.clients[0].get_history(ticker, period)
        g_task = self.clients[1].get_history(ticker, period)

        results = await asyncio.gather(b_task, g_task, return_exceptions=True)

        # Если была ошибка, вернем пустой список
        binance_data = results[0] if not isinstance(results[0], Exception) else []
        gecko_data = results[1] if not isinstance(results[1], Exception) else []

        # Кэшируем на 60 сек,т.к. 'тяжелые данные'
        if binance_data or gecko_data:
            self._set_cache(cache_key, (binance_data, gecko_data), ttl=60)

        return binance_data, gecko_data

    def _check_cache(self, key: str) -> bool:
        return key in CACHE and time.time() < CACHE[key]["expires"]

    def _set_cache(self, key: str, data, ttl: int):
        CACHE[key] = {"data": data, "expires": time.time() + ttl}