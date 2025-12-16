import httpx
from abc import ABC, abstractmethod
from app.schemas.market_data import CryptoPrice, Ticker

#Шаблон
class BaseCryptoClient(ABC):
    @abstractmethod
    async def get_current_price(self,ticker: Ticker) -> CryptoPrice:
        pass

class BinanceClient(BaseCryptoClient):
    BASE_URL = "https://api.binance.com/api/v3"
    async  def get_current_price(self, ticker: Ticker) -> CryptoPrice:
        symbol = f"{ticker.value}USDT"
        async  with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.BASE_URL}/ticker/price",
                                            params={"symbol":symbol},
                                            timeout=10.0)
                response.raise_for_status()
                data = response.json()

                return CryptoPrice(
                    ticker=ticker,
                    price=float(data["price"]),
                    source="Binance"
                )
            except Exception as e:
                print(f"Error Binance: {e}")
                raise e

class CoinGeckoClient(BaseCryptoClient):
    BASE_URL = "https://api.coingecko.com/api/v3"
    TICKER_MAP = {
        Ticker.BTC: "bitcoin",
        Ticker.ETH: "ethereum",
        Ticker.SOL: "solana"
    }

    async def get_current_price(self, ticker: Ticker) -> CryptoPrice:
        coin_id = self.TICKER_MAP.get(ticker)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/simple/price",
                    params={"ids": coin_id, "vs_currencies": "usd"},
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()

                if coin_id not in data:
                    raise ValueError(f"CoinGecko не вернул данные для {coin_id}")

                price = data[coin_id]["usd"]

                return CryptoPrice(
                    ticker=ticker,
                    price=float(price),
                    source="CoinGecko"
                )
            except Exception as e:
                print(f"Error CoinGecko: {e}")
                raise e

