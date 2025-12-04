from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StockAdd(BaseModel):
    """Schema for adding a stock to watchlist"""
    symbol: str = Field(..., min_length=1, max_length=50, description="Stock symbol (e.g., RELIANCE.NS)")
    name: Optional[str] = Field(None, max_length=200, description="Company name")


class WatchlistCreate(BaseModel):
    """Schema for creating a new watchlist"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    stocks: List[StockAdd] = Field(default_factory=list)


class WatchlistUpdate(BaseModel):
    """Schema for updating watchlist metadata"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class StockResponse(BaseModel):
    """Schema for stock response"""
    symbol: str
    name: Optional[str]
    added_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WatchlistResponse(BaseModel):
    """Schema for watchlist response"""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    stocks: List[StockResponse]
    created_at: datetime
    updated_at: datetime
    is_default: bool

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StockSearchResult(BaseModel):
    """Schema for stock search result"""
    symbol: str
    name: str
    exchange: str
    type: str


class IndexWatchlistCreate(BaseModel):
    """Schema for creating watchlist from index"""
    index_name: str = Field(..., description="Index name: nifty50, banknifty, nifty100, niftynext50")
    watchlist_name: Optional[str] = Field(None, description="Custom watchlist name (optional)")
