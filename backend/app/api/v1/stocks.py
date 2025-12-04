from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional

from app.schemas.watchlist import StockSearchResult
from app.services.stock_service import StockService
from app.services.cache_service import CacheService
from app.core.security import get_current_user_id

router = APIRouter(prefix="/stocks", tags=["Stocks"])


@router.get("/search", response_model=List[StockSearchResult])
async def search_stocks(
    q: str = Query(..., min_length=1, description="Search query"),
    user_id: str = Depends(get_current_user_id)
):
    """
    Search for stocks by symbol or name
    Results are cached for 5 minutes
    """

    # Check cache first
    cache_key = CacheService.make_search_key(q)
    cached_results = await CacheService.get(cache_key)

    if cached_results:
        return cached_results

    # Search stocks
    results = await StockService.search_stock(q)

    if not results:
        return []

    # Format results
    formatted_results = [
        StockSearchResult(
            symbol=r["symbol"],
            name=r["name"],
            exchange=r["exchange"],
            type=r["type"]
        ) for r in results
    ]

    # Cache results for 5 minutes
    await CacheService.set(cache_key, [r.model_dump() for r in formatted_results], ttl=300)

    return formatted_results


@router.get("/{symbol}/info")
async def get_stock_info(
    symbol: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get detailed information about a stock
    Results are cached for 5 minutes
    """

    # Check cache first
    cache_key = CacheService.make_stock_key(symbol, "info")
    cached_info = await CacheService.get(cache_key)

    if cached_info:
        return cached_info

    # Fetch stock info
    stock_info = await StockService.get_stock_info(symbol)

    if not stock_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock {symbol} not found"
        )

    # Cache for 5 minutes
    await CacheService.set(cache_key, stock_info, ttl=300)

    return stock_info


@router.get("/{symbol}/historical")
async def get_historical_data(
    symbol: str,
    period: str = Query("1mo", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    interval: str = Query("1d", description="Data interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo"),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get historical price data for a stock
    Results are cached based on interval
    """

    # Check cache first
    cache_key = CacheService.make_stock_key(symbol, f"historical:{period}:{interval}")
    cached_data = await CacheService.get(cache_key)

    if cached_data:
        return cached_data

    # Fetch historical data
    historical_data = await StockService.get_historical_data(symbol, period, interval)

    if not historical_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No historical data found for {symbol}"
        )

    # Cache with appropriate TTL based on interval
    ttl = 60  # 1 minute for intraday
    if interval in ["1d", "5d", "1wk", "1mo", "3mo"]:
        ttl = 300  # 5 minutes for daily+

    await CacheService.set(cache_key, historical_data, ttl=ttl)

    return historical_data


@router.get("/{symbol}/validate")
async def validate_stock_symbol(
    symbol: str,
    user_id: str = Depends(get_current_user_id)
):
    """Validate if a stock symbol exists"""

    is_valid = await StockService.validate_symbol(symbol)

    return {
        "symbol": symbol,
        "valid": is_valid
    }
