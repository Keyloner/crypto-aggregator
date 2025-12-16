from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.schemas.market_data import Ticker, Period
from app.services.aggregator import PriceAggregator
from app.services.analytics import AnalyticsService
from app.services.visualizer import GraphService

router = APIRouter()

@router.get("/price/{ticker}")
async def get_price(ticker: Ticker):
    aggregator = PriceAggregator()
    prices = await aggregator.get_prices(ticker)
    return [p.model_dump(mode='json') for p in prices]

@router.get("/report/{ticker}")
async def get_analytics(
        ticker: Ticker,
        period: Period = Period.ALL
):
    service = AnalyticsService()
    try:
        report = service.get_report(ticker,period)
        return report.model_dump(mode='json')
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/graph/{ticker}")
async def get_graph(
        ticker: Ticker,
        period: Period = Period.ALL
):
    service = GraphService()
    try:
        image_bytes = service.create_price_chart(ticker,period)
        return Response(content=image_bytes, media_type="image/png")
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=404, detail=str(e))