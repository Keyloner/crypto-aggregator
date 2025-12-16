from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class Period(str,Enum):
    ALL = "all"
    HOUR_1 = "1h"
    HOUR_24 = "24h"
    DAY_7 = "7d"

class Ticker(str, Enum):
    BTC = "BTC"
    ETH = "ETH"
    SOL = "SOL"

class CryptoPrice(BaseModel):
    ticker: Ticker
    price: float = Field(..., gt=0, description="Цена в USD")
    timestamp: datetime = Field(default_factory=datetime.now)#datetime.now(timezone.utc)
    source: str = Field(..., description = "Источник данных")
    model_config = ConfigDict(from_attributes=True)

class AnalyticsReport(BaseModel):
    ticker: Ticker
    min_price: float
    max_price: float
    avg_price: float
    spread_percentage: float
    outliers_count: int
    timestamp: datetime


