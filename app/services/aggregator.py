import asyncio
from typing import List
import time
from app.schemas.market_data import Ticker, CryptoPrice
from app.services.api_clients import BinanceClient, CoinGeckoClient
from app.services.storage import CsvStorage

CACHE = {}
CACHE_TTL = 10 #время жизни = 10 секунд

class PriceAggregator:
    def __init__(self):
        self.clients = [
            BinanceClient(),
            CoinGeckoClient()
        ]
        self.storage = CsvStorage()

    async def get_prices(self,ticker: Ticker) -> List[CryptoPrice]:
        ticker_key = ticker.value
        current_time = time.time()

        if ticker_key in CACHE:
            saved_data = CACHE[ticker_key]

            #если прошло меньше 10 сек:
            if current_time - saved_data["time"] < CACHE_TTL:
                print(f"Из кэша {ticker_key}")
                return saved_data["data"]

        #если кэша нет или он старый:
        print(f"Запрос к API {ticker_key}")
        tasks =[]
        for client in self.clients:
            tasks.append(client.get_current_price(ticker))
                                                #Если кто-то упал с ошибкой, то вернет ошибку
        results = await asyncio.gather(*tasks, return_exceptions=True)

        valid_prices = []
        for res in results:
            if isinstance(res,Exception):
                print(f"Aggregator error: {res}")
            else:
                valid_prices.append(res)

        if valid_prices:
            self.storage.save(valid_prices)
            #сохраняем в кэш
            CACHE[ticker_key] = {
                "data": valid_prices,
                "time": current_time
            }

        return valid_prices
