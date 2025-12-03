from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserPreferences(BaseModel):
    """User preferences for analysis"""
    default_weightage: Dict[str, int] = Field(
        default={
            "price_action": 1,
            "reversal_patterns": 1,
            "candlestick_patterns": 1,
            "indicators": 1,
            "volatility": 1,
            "time_analysis": 1,
            "news": 1
        }
    )
    theme: str = Field(default="light")
    default_timeframe: str = Field(default="1d")


class UserInDB(BaseModel):
    """User model for MongoDB"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    email: EmailStr
    username: str
    password_hash: str
    full_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    preferences: UserPreferences = Field(default_factory=UserPreferences)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class User(BaseModel):
    """User model for API responses (without sensitive data)"""
    id: str = Field(alias="_id")
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    preferences: UserPreferences

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
