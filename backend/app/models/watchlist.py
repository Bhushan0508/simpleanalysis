from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

from app.models.user import PyObjectId


class Stock(BaseModel):
    """Individual stock in a watchlist"""
    symbol: str = Field(..., description="Stock symbol (e.g., RELIANCE.NS)")
    name: Optional[str] = Field(None, description="Company name")
    added_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Watchlist(BaseModel):
    """Watchlist model for MongoDB"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId = Field(..., description="User who owns this watchlist")
    name: str = Field(..., min_length=1, max_length=100, description="Watchlist name")
    description: Optional[str] = Field(None, max_length=500)
    stocks: List[Stock] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_default: bool = Field(default=False, description="Whether this is the default watchlist")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
