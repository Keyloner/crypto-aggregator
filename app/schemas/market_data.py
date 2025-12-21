from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class Ticker(str, Enum):
    BTC = "BTC"
    ETH = "ETH"
    SOL = "SOL"


class Period(str, Enum):
    YEAR = "1y"
    HOUR_24 = "24h"
    DAY_7 = "7d"
    MONTH_1 = "30d"


# Модель Цены
class CryptoPrice(BaseModel):
    ticker: Ticker
    price: float = Field(..., gt=0, description="Цена в USD")
    timestamp: datetime = Field(description="Время получения")
    source: str = Field(description="Биржа")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ticker": "BTC",
                "price": 95432.10,
                "timestamp": "2025-12-21T12:00:00",
                "source": "Binance"
            }
        }
    )


# Статистика одной биржи
class ExchangeStats(BaseModel):
    min_price: float = Field(examples=[95000.0])
    max_price: float = Field(examples=[98000.0])
    avg_price: float = Field(examples=[96500.0])
    volatility_percent: float = Field(examples=[3.15])


# Общий отчет
class ComparisonReport(BaseModel):
    ticker: Ticker = Field(examples=["BTC"])
    period: Period = Field(examples=["24h"])
    timestamp: datetime = Field(default_factory=datetime.now)
    binance_stats: Optional[ExchangeStats]
    coingecko_stats: Optional[ExchangeStats]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "ticker": "BTC",
                "period": "24h",
                "timestamp": "2025-12-22T12:00:00",
                "binance_stats": {
                    "min_price": 95100.0, "max_price": 98200.0,
                    "avg_price": 96600.0, "volatility_percent": 3.25
                },
                "coingecko_stats": {
                    "min_price": 95050.0, "max_price": 98100.0,
                    "avg_price": 96550.0, "volatility_percent": 3.10
                }
            }
        }
    )


class ErrorResponse(BaseModel):
    detail: str = Field(examples=["Ошибка получения данных"])