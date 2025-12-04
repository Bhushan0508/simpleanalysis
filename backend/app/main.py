from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import settings, CORS_ORIGINS
from app.core.database import Database
from app.api.v1 import auth, watchlist, stocks, upload
from app.services.yfinance_rate_limiter import get_rate_limiter

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting application...")
    try:
        await Database.connect_db()

        # Start Yahoo Finance rate limiter
        rate_limiter = get_rate_limiter()
        await rate_limiter.start()

        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")

    # Stop Yahoo Finance rate limiter
    rate_limiter = get_rate_limiter()
    await rate_limiter.stop()

    await Database.close_db()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Stock Analysis Platform for Indian Markets (NSE/BSE)",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging"""
    errors = exc.errors()
    logger.error(f"Validation error for {request.url}: {errors}")

    # Format errors to be JSON serializable
    formatted_errors = []
    for error in errors:
        formatted_error = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", ""),
        }
        # Convert input to string if present
        if "input" in error:
            formatted_error["input"] = str(error["input"])
        formatted_errors.append(formatted_error)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": formatted_errors},
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to SimpleAnalysis API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs" if settings.DEBUG else "Documentation disabled in production"
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(watchlist.router, prefix="/api/v1")
app.include_router(stocks.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
