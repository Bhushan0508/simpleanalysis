import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = os.getenv("APP_NAME", "simpleanalysis")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8005"))

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Database
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "simpleanalysis")

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    # File Upload
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "52428800"))  # 50MB
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./data/uploads")

    # Yahoo Finance
    YF_RATE_LIMIT: int = int(os.getenv("YF_RATE_LIMIT", "2000"))  # requests per hour

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


# Create global settings instance
settings = Settings()

# Parse CORS origins manually from environment variable
_cors_origins_str = os.getenv("CORS_ORIGINS_STR", "http://localhost:3000,http://localhost:5173,http://localhost:85,http://localhost:8005")
CORS_ORIGINS: List[str] = [origin.strip() for origin in _cors_origins_str.split(',') if origin.strip()]
