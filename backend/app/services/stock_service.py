import yfinance as yf
from typing import Optional, List, Dict
import logging
from datetime import datetime, timedelta
from .yfinance_rate_limiter import get_rate_limiter

logger = logging.getLogger(__name__)


class StockService:
    """Service for fetching stock data from Yahoo Finance with centralized rate limiting"""

    # Indian market index constituents
    INDICES = {
        "nifty50": [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
            "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
            "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
            "TITAN.NS", "BAJFINANCE.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "WIPRO.NS",
            "HCLTECH.NS", "TATAMOTORS.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS",
            "TATASTEEL.NS", "M&M.NS", "TECHM.NS", "ADANIENT.NS", "JSWSTEEL.NS",
            "INDUSINDBK.NS", "HINDALCO.NS", "COALINDIA.NS", "BAJAJFINSV.NS", "CIPLA.NS",
            "DRREDDY.NS", "EICHERMOT.NS", "BRITANNIA.NS", "GRASIM.NS", "APOLLOHOSP.NS",
            "BPCL.NS", "DIVISLAB.NS", "TATACONSUM.NS", "HEROMOTOCO.NS", "SHRIRAMFIN.NS",
            "SBILIFE.NS", "ADANIPORTS.NS", "UPL.NS", "BAJAJ-AUTO.NS", "LTIM.NS"
        ],
        "banknifty": [
            "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS",
            "INDUSINDBK.NS", "BANDHANBNK.NS", "FEDERALBNK.NS", "AUBANK.NS", "IDFCFIRSTB.NS",
            "PNB.NS", "BANKBARODA.NS"
        ],
        "nifty100": [],  # Can be populated later
        "niftynext50": []  # Can be populated later
    }

    @staticmethod
    async def search_stock(query: str) -> List[Dict[str, str]]:
        """
        Search for stocks by symbol or name using rate limiter

        Args:
            query: Search query string

        Returns:
            List of matching stocks
        """
        try:
            rate_limiter = get_rate_limiter()
            results = await rate_limiter.fetch_stock_search(query)
            return results
        except Exception as e:
            logger.error(f"Error searching stock {query}: {e}")
            return []

    @staticmethod
    async def get_stock_info(symbol: str) -> Optional[Dict]:
        """
        Get detailed stock information using rate limiter

        Args:
            symbol: Stock symbol

        Returns:
            Stock information dict or None
        """
        try:
            rate_limiter = get_rate_limiter()
            info = await rate_limiter.fetch_stock_info(symbol)

            if not info:
                return None

            return {
                "symbol": symbol,
                "name": info.get('longName', info.get('shortName', 'N/A')),
                "exchange": info.get('exchange', 'NSE'),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "marketCap": info.get('marketCap', 0),
                "currentPrice": info.get('currentPrice', info.get('regularMarketPrice', 0)),
                "previousClose": info.get('previousClose', 0),
                "dayHigh": info.get('dayHigh', 0),
                "dayLow": info.get('dayLow', 0),
                "volume": info.get('volume', 0),
                "averageVolume": info.get('averageVolume', 0),
            }
        except Exception as e:
            logger.error(f"Error getting stock info for {symbol}: {e}")
            return None

    @staticmethod
    async def get_historical_data(
        symbol: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[Dict]:
        """
        Get historical price data

        Args:
            symbol: Stock symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            Historical data dict or None
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)

            if hist.empty:
                return None

            return {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "data": hist.to_dict('records')
            }
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return None

    @classmethod
    async def get_index_stocks(cls, index_name: str) -> List[Dict[str, str]]:
        """
        Get list of stocks in an index using centralized rate limiter

        Args:
            index_name: Index name (nifty50, banknifty, etc.)

        Returns:
            List of stocks with symbol and name
        """
        index_name_lower = index_name.lower()

        if index_name_lower not in cls.INDICES:
            raise ValueError(f"Unknown index: {index_name}. Available: {list(cls.INDICES.keys())}")

        symbols = cls.INDICES[index_name_lower]
        stocks = []
        rate_limiter = get_rate_limiter()

        logger.info(f"Queuing {len(symbols)} stocks for {index_name} to rate limiter...")

        for i, symbol in enumerate(symbols):
            try:
                info = await rate_limiter.fetch_stock_info(symbol)

                if info:
                    stocks.append({
                        "symbol": symbol,
                        "name": info.get('longName', info.get('shortName', symbol))
                    })
                    logger.debug(f"Successfully fetched {symbol} ({i+1}/{len(symbols)})")
                else:
                    # Failed to fetch info, use symbol as fallback
                    stocks.append({
                        "symbol": symbol,
                        "name": symbol.replace('.NS', '').replace('.BO', '')
                    })
                    logger.warning(f"Using fallback name for {symbol}")

            except Exception as e:
                logger.warning(f"Could not fetch info for {symbol}: {e}")
                stocks.append({
                    "symbol": symbol,
                    "name": symbol.replace('.NS', '').replace('.BO', '')
                })

        logger.info(f"Completed fetching {len(stocks)} stocks for {index_name}")
        return stocks

    @staticmethod
    async def validate_symbol(symbol: str) -> bool:
        """
        Validate if a stock symbol exists

        Args:
            symbol: Stock symbol to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return bool(info and 'symbol' in info)
        except Exception:
            return False
