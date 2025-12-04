from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, GetCoreSchemaHandler
from pydantic_core import core_schema
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2"""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ],
        serialization=core_schema.plain_serializer_function_ser_schema(
            lambda x: str(x)
        ))

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


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
