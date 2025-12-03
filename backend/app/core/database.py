from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection manager"""

    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        try:
            logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}")
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URL,
                maxPoolSize=100,
                minPoolSize=10,
                serverSelectionTimeoutMS=5000,
            )
            cls.database = cls.client[settings.MONGODB_DB_NAME]

            # Test connection
            await cls.client.admin.command("ping")
            logger.info(f"Successfully connected to MongoDB database: {settings.MONGODB_DB_NAME}")

            # Create indexes
            await cls.create_indexes()

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            logger.info("Closing MongoDB connection")
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if cls.database is None:
            raise Exception("Database not connected. Call connect_db() first")
        return cls.database

    @classmethod
    async def create_indexes(cls):
        """Create database indexes for performance"""
        if cls.database is None:
            return

        try:
            logger.info("Creating database indexes...")

            # Users collection indexes
            await cls.database.users.create_index("email", unique=True)
            await cls.database.users.create_index("username", unique=True)

            # Watchlists collection indexes
            await cls.database.watchlists.create_index("user_id")
            await cls.database.watchlists.create_index([("user_id", 1), ("name", 1)])

            # Stock analysis collection indexes
            await cls.database.stock_analysis.create_index("user_id")
            await cls.database.stock_analysis.create_index("symbol")
            await cls.database.stock_analysis.create_index([
                ("user_id", 1),
                ("symbol", 1),
                ("analysis_date", -1)
            ])

            # Trades collection indexes
            await cls.database.trades.create_index("user_id")
            await cls.database.trades.create_index([("user_id", 1), ("trade_date", -1)])
            await cls.database.trades.create_index("symbol")
            await cls.database.trades.create_index("status")

            # Stock cache collection indexes (with TTL)
            await cls.database.stock_cache.create_index("symbol", unique=True)
            await cls.database.stock_cache.create_index(
                "last_updated",
                expireAfterSeconds=604800  # 7 days TTL
            )

            # Sector rotation collection indexes
            await cls.database.sector_rotation.create_index("user_id")
            await cls.database.sector_rotation.create_index([
                ("user_id", 1),
                ("date_updated", -1)
            ])

            # File versions collection indexes
            await cls.database.file_versions.create_index("user_id")
            await cls.database.file_versions.create_index([
                ("user_id", 1),
                ("original_filename", 1),
                ("version", -1)
            ])

            logger.info("Database indexes created successfully")

        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            # Don't raise - indexes are not critical for startup


# Dependency for FastAPI
async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency to get database instance"""
    return Database.get_database()
