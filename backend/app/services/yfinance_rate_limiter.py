import yfinance as yf
import asyncio
import time
import logging
import os
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Blocking all requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class YFinanceRateLimiter:
    """
    Centralized rate limiter for Yahoo Finance API requests.

    Features:
    - Token bucket rate limiting
    - Sequential request processing (one at a time)
    - Mandatory 3-second delay between requests
    - Circuit breaker for 429 errors
    - Request deduplication via caching
    - Exponential backoff retry logic
    """

    def __init__(self):
        # Configuration from environment
        self.requests_per_minute = int(os.getenv("YFINANCE_REQUESTS_PER_MINUTE", "10"))
        self.max_concurrent = int(os.getenv("YFINANCE_MAX_CONCURRENT", "2"))
        self.cache_ttl = int(os.getenv("YFINANCE_CACHE_TTL", "300"))  # 5 minutes
        self.circuit_breaker_threshold = int(os.getenv("YFINANCE_CIRCUIT_BREAKER_THRESHOLD", "5"))
        self.circuit_breaker_timeout = int(os.getenv("YFINANCE_CIRCUIT_BREAKER_TIMEOUT", "300"))  # 5 minutes

        # Token bucket
        # Start with 1 token to allow first request immediately, then enforce rate limiting
        self.tokens = 1.0
        self.max_tokens = float(self.requests_per_minute)
        self.refill_rate = self.requests_per_minute / 60.0  # tokens per second
        self.last_refill = time.time()

        # Request queue
        self.request_queue = asyncio.Queue()
        self.active_requests = 0

        # Cache for deduplication
        self.cache: Dict[str, tuple[Any, float]] = {}  # {cache_key: (result, expiry_time)}

        # Circuit breaker
        self.circuit_state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.circuit_opened_at: Optional[float] = None

        # Background task
        self.processor_task: Optional[asyncio.Task] = None
        self.is_running = False

        logger.info(
            f"YFinance Rate Limiter initialized: "
            f"{self.requests_per_minute} req/min (sequential processing), "
            f"3-second delay between requests, "
            f"{self.cache_ttl}s cache TTL"
        )

    async def start(self):
        """Start the background queue processor"""
        if not self.is_running:
            self.is_running = True
            self.processor_task = asyncio.create_task(self._process_queue())
            logger.info("YFinance Rate Limiter started")

    async def stop(self):
        """Stop the background queue processor"""
        self.is_running = False
        if self.processor_task:
            self.processor_task.cancel()
            try:
                await self.processor_task
            except asyncio.CancelledError:
                pass
        logger.info("YFinance Rate Limiter stopped")

    def _refill_tokens(self):
        """Refill token bucket based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_refill = now

    def _check_circuit_breaker(self) -> bool:
        """
        Check circuit breaker state

        Returns:
            True if requests should be allowed, False if blocked
        """
        if self.circuit_state == CircuitState.CLOSED:
            return True

        if self.circuit_state == CircuitState.OPEN:
            # Check if timeout has elapsed
            if self.circuit_opened_at and (time.time() - self.circuit_opened_at) > self.circuit_breaker_timeout:
                logger.info("Circuit breaker timeout elapsed, moving to HALF_OPEN state")
                self.circuit_state = CircuitState.HALF_OPEN
                self.consecutive_failures = 0
                return True
            return False

        if self.circuit_state == CircuitState.HALF_OPEN:
            # Allow a few test requests
            return True

        return False

    def _record_success(self):
        """Record a successful request"""
        self.consecutive_failures = 0
        if self.circuit_state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker closing after successful request")
            self.circuit_state = CircuitState.CLOSED

    def _record_failure(self, is_rate_limit: bool = False):
        """Record a failed request"""
        if is_rate_limit:
            self.consecutive_failures += 1
            logger.warning(
                f"Rate limit error count: {self.consecutive_failures}/{self.circuit_breaker_threshold}"
            )

            if self.consecutive_failures >= self.circuit_breaker_threshold:
                logger.error(f"Circuit breaker OPENING due to {self.consecutive_failures} consecutive 429 errors")
                self.circuit_state = CircuitState.OPEN
                self.circuit_opened_at = time.time()

    def _get_cache_key(self, request_type: str, identifier: str) -> str:
        """Generate cache key for request deduplication"""
        return f"{request_type}:{identifier}"

    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get cached result if not expired"""
        if cache_key in self.cache:
            result, expiry = self.cache[cache_key]
            if time.time() < expiry:
                logger.debug(f"Cache hit for {cache_key}")
                return result
            else:
                # Expired, remove from cache
                del self.cache[cache_key]
        return None

    def _set_cache(self, cache_key: str, result: Any):
        """Store result in cache"""
        expiry = time.time() + self.cache_ttl
        self.cache[cache_key] = (result, expiry)
        logger.debug(f"Cached result for {cache_key}")

    async def _wait_for_token(self):
        """Wait until a token is available"""
        while self.tokens < 1.0:
            self._refill_tokens()
            if self.tokens < 1.0:
                # Calculate wait time for next token
                wait_time = (1.0 - self.tokens) / self.refill_rate
                await asyncio.sleep(min(wait_time, 1.0))  # Sleep max 1 second at a time

    async def _execute_request(self, fetch_func, max_retries: int = 3) -> Optional[Any]:
        """
        Execute a request with retry logic

        Args:
            fetch_func: Function to execute (synchronous)
            max_retries: Maximum retry attempts

        Returns:
            Result from fetch_func or None on failure
        """
        for attempt in range(max_retries):
            try:
                # Execute the synchronous yfinance call
                result = await asyncio.to_thread(fetch_func)

                # Success - check if result is valid
                if result:
                    self._record_success()
                    return result
                else:
                    # Empty result, might be rate limited without exception
                    logger.warning(f"Empty result from yfinance on attempt {attempt + 1}/{max_retries}")
                    if attempt < max_retries - 1:
                        backoff = 10 * (2 ** attempt)
                        await asyncio.sleep(backoff)
                        continue
                    return None

            except Exception as e:
                error_str = str(e).lower()
                # Check for rate limiting or JSON parsing errors (which happen after 429)
                is_rate_limit = ('429' in error_str or
                                'too many requests' in error_str or
                                'expecting value' in error_str)

                if is_rate_limit:
                    self._record_failure(is_rate_limit=True)

                    if attempt < max_retries - 1:
                        # Exponential backoff: 10s, 20s, 40s
                        backoff = 10 * (2 ** attempt)
                        logger.warning(
                            f"Rate limit hit, retry {attempt + 1}/{max_retries} "
                            f"after {backoff}s backoff"
                        )
                        await asyncio.sleep(backoff)
                        continue
                    else:
                        logger.error(f"Max retries reached for rate limit error")
                        return None
                else:
                    # Non-rate-limit error
                    logger.error(f"Request failed with error: {e}")
                    return None

        return None

    async def _process_queue(self):
        """Background task to process queued requests sequentially"""
        logger.info("Queue processor started (sequential mode)")

        while self.is_running:
            try:
                # Check circuit breaker
                if not self._check_circuit_breaker():
                    logger.warning("Circuit breaker OPEN, waiting before processing requests...")
                    await asyncio.sleep(10)  # Wait 10s before checking again
                    continue

                # Wait for a token
                await self._wait_for_token()

                # Get request from queue (with timeout to allow loop to continue)
                try:
                    request_future, fetch_func = await asyncio.wait_for(
                        self.request_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Consume a token
                self.tokens -= 1.0
                self.active_requests += 1

                # Execute request and WAIT for it to complete before processing next
                # This ensures strict sequential processing
                await self._execute_and_respond(request_future, fetch_func)

            except Exception as e:
                logger.error(f"Error in queue processor: {e}", exc_info=True)
                await asyncio.sleep(1)

        logger.info("Queue processor stopped")

    async def _execute_and_respond(self, request_future: asyncio.Future, fetch_func):
        """Execute request and set result on future"""
        try:
            result = await self._execute_request(fetch_func)
            if not request_future.done():
                request_future.set_result(result)
        except Exception as e:
            if not request_future.done():
                request_future.set_exception(e)
        finally:
            self.active_requests -= 1
            # Mandatory 3-second delay after each request to respect Yahoo Finance limits
            # Yahoo Finance has strict rate limits; being conservative prevents 429 errors
            await asyncio.sleep(3.0)

    async def fetch_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Fetch stock information with rate limiting

        Args:
            symbol: Stock symbol (e.g., "RELIANCE.NS")

        Returns:
            Stock info dict or None
        """
        # Check cache first
        cache_key = self._get_cache_key("info", symbol)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Create fetch function
        def fetch():
            ticker = yf.Ticker(symbol)
            return ticker.info

        # Queue the request
        request_future = asyncio.Future()
        await self.request_queue.put((request_future, fetch))

        # Wait for result
        try:
            result = await asyncio.wait_for(request_future, timeout=120)  # 2 minute timeout

            if result:
                self._set_cache(cache_key, result)

            return result
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for stock info: {symbol}")
            return None

    async def fetch_stock_search(self, query: str) -> List[Dict[str, str]]:
        """
        Search for stocks with rate limiting

        Args:
            query: Search query

        Returns:
            List of matching stocks
        """
        # Check cache first
        cache_key = self._get_cache_key("search", query)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Try multiple symbol variations
        symbols_to_try = [
            query.upper(),
            f"{query.upper()}.NS",
            f"{query.upper()}.BO"
        ]

        results = []
        seen_symbols = set()

        for symbol in symbols_to_try:
            # Create fetch function
            def fetch(sym=symbol):
                ticker = yf.Ticker(sym)
                return ticker.info

            # Queue the request
            request_future = asyncio.Future()
            await self.request_queue.put((request_future, fetch))

            # Wait for result
            try:
                info = await asyncio.wait_for(request_future, timeout=60)

                if info and 'symbol' in info:
                    symbol_key = info.get('symbol', symbol)

                    if symbol_key not in seen_symbols:
                        seen_symbols.add(symbol_key)
                        results.append({
                            "symbol": symbol_key,
                            "name": info.get('longName', info.get('shortName', 'N/A')),
                            "exchange": info.get('exchange', 'NSE'),
                            "type": info.get('quoteType', 'EQUITY')
                        })
            except (asyncio.TimeoutError, Exception) as e:
                logger.debug(f"Error fetching {symbol} during search: {e}")
                continue

        # Cache results
        if results:
            self._set_cache(cache_key, results)

        return results


# Global singleton instance
_rate_limiter: Optional[YFinanceRateLimiter] = None


def get_rate_limiter() -> YFinanceRateLimiter:
    """Get the global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = YFinanceRateLimiter()
    return _rate_limiter
