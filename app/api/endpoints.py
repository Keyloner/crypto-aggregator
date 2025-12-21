from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from typing import List, Dict, Any

from app.schemas.market_data import Ticker, Period, ComparisonReport, CryptoPrice, ErrorResponse
from app.services.aggregator import PriceAggregator
from app.services.analytics import AnalyticsService
from app.services.visualizer import GraphService

router = APIRouter()
aggregator = PriceAggregator()
analytics = AnalyticsService()
visualizer = GraphService()

validation_error = {
    "description": "Ошибка валидации параметров",
    "content": {
        "application/json": {
            "example": {
                "detail": [
                    {
                        "loc": ["query", "period"],
                        "msg": "Значение должно быть одним из: 1h, 24h, 7d, 30d, 1y",
                        "type": "type_error.enum"
                    }
                ]
            }
        }
    }
}

common_responses: Dict[int, Any] = {
    404: {"model": ErrorResponse, "description": "Данные не найдены"},
    500: {"model": ErrorResponse, "description": "Ошибка сервера"},
    422: validation_error
}

@router.get("/price/{ticker}", response_model=List[CryptoPrice], responses=common_responses)
async def get_price(ticker: Ticker):
    return await aggregator.get_prices(ticker)

@router.get("/report/{ticker}", response_model=ComparisonReport, responses=common_responses)
async def get_analytics(ticker: Ticker, period: Period = Period.HOUR_24):
    binance_data, gecko_data = await aggregator.get_history(ticker, period)
    if not binance_data and not gecko_data:
        raise HTTPException(status_code=404, detail="Нет данных")
    return analytics.create_report(ticker, period, binance_data, gecko_data)

@router.get("/graph/{ticker}", response_class=Response, responses={200: {"content": {"image/png": {}}}, **common_responses})
async def get_graph(ticker: Ticker, period: Period = Period.HOUR_24):
    try:
        image_bytes = await visualizer.create_comparison_chart(ticker, period)
        return Response(content=image_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))