from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import List

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistUpdate,
    WatchlistResponse,
    StockAdd,
    StockResponse,
    IndexWatchlistCreate
)
from app.models.watchlist import Watchlist, Stock
from app.services.stock_service import StockService

router = APIRouter(prefix="/watchlists", tags=["Watchlists"])


@router.post("", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def create_watchlist(
    watchlist_data: WatchlistCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a new watchlist"""

    # Create watchlist
    watchlist = Watchlist(
        user_id=ObjectId(user_id),
        name=watchlist_data.name,
        description=watchlist_data.description,
        stocks=[Stock(symbol=s.symbol, name=s.name) for s in watchlist_data.stocks]
    )

    # Insert into database
    result = await db.watchlists.insert_one(
        watchlist.model_dump(by_alias=True, exclude={"id"})
    )

    # Fetch created watchlist
    created_watchlist = await db.watchlists.find_one({"_id": result.inserted_id})

    return WatchlistResponse(
        id=str(created_watchlist["_id"]),
        user_id=str(created_watchlist["user_id"]),
        name=created_watchlist["name"],
        description=created_watchlist.get("description"),
        stocks=[
            StockResponse(
                symbol=s["symbol"],
                name=s.get("name"),
                added_at=s["added_at"]
            ) for s in created_watchlist.get("stocks", [])
        ],
        created_at=created_watchlist["created_at"],
        updated_at=created_watchlist["updated_at"],
        is_default=created_watchlist.get("is_default", False)
    )


@router.get("", response_model=List[WatchlistResponse])
async def get_watchlists(
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all watchlists for current user"""

    cursor = db.watchlists.find({"user_id": ObjectId(user_id)})
    watchlists = await cursor.to_list(length=None)

    return [
        WatchlistResponse(
            id=str(w["_id"]),
            user_id=str(w["user_id"]),
            name=w["name"],
            description=w.get("description"),
            stocks=[
                StockResponse(
                    symbol=s["symbol"],
                    name=s.get("name"),
                    added_at=s["added_at"]
                ) for s in w.get("stocks", [])
            ],
            created_at=w["created_at"],
            updated_at=w["updated_at"],
            is_default=w.get("is_default", False)
        ) for w in watchlists
    ]


@router.get("/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist(
    watchlist_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get a specific watchlist"""

    watchlist = await db.watchlists.find_one({
        "_id": ObjectId(watchlist_id),
        "user_id": ObjectId(user_id)
    })

    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )

    return WatchlistResponse(
        id=str(watchlist["_id"]),
        user_id=str(watchlist["user_id"]),
        name=watchlist["name"],
        description=watchlist.get("description"),
        stocks=[
            StockResponse(
                symbol=s["symbol"],
                name=s.get("name"),
                added_at=s["added_at"]
            ) for s in watchlist.get("stocks", [])
        ],
        created_at=watchlist["created_at"],
        updated_at=watchlist["updated_at"],
        is_default=watchlist.get("is_default", False)
    )


@router.put("/{watchlist_id}", response_model=WatchlistResponse)
async def update_watchlist(
    watchlist_id: str,
    watchlist_update: WatchlistUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Update watchlist metadata"""

    # Check if watchlist exists and belongs to user
    watchlist = await db.watchlists.find_one({
        "_id": ObjectId(watchlist_id),
        "user_id": ObjectId(user_id)
    })

    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )

    # Prepare update data
    update_data = {"updated_at": datetime.utcnow()}

    if watchlist_update.name is not None:
        update_data["name"] = watchlist_update.name
    if watchlist_update.description is not None:
        update_data["description"] = watchlist_update.description

    # Update watchlist
    await db.watchlists.update_one(
        {"_id": ObjectId(watchlist_id)},
        {"$set": update_data}
    )

    # Fetch updated watchlist
    updated_watchlist = await db.watchlists.find_one({"_id": ObjectId(watchlist_id)})

    return WatchlistResponse(
        id=str(updated_watchlist["_id"]),
        user_id=str(updated_watchlist["user_id"]),
        name=updated_watchlist["name"],
        description=updated_watchlist.get("description"),
        stocks=[
            StockResponse(
                symbol=s["symbol"],
                name=s.get("name"),
                added_at=s["added_at"]
            ) for s in updated_watchlist.get("stocks", [])
        ],
        created_at=updated_watchlist["created_at"],
        updated_at=updated_watchlist["updated_at"],
        is_default=updated_watchlist.get("is_default", False)
    )


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(
    watchlist_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Delete a watchlist"""

    result = await db.watchlists.delete_one({
        "_id": ObjectId(watchlist_id),
        "user_id": ObjectId(user_id)
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )


@router.post("/{watchlist_id}/stocks", response_model=WatchlistResponse)
async def add_stock_to_watchlist(
    watchlist_id: str,
    stock_data: StockAdd,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Add a stock to watchlist"""

    # Check if watchlist exists and belongs to user
    watchlist = await db.watchlists.find_one({
        "_id": ObjectId(watchlist_id),
        "user_id": ObjectId(user_id)
    })

    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )

    # Check if stock already exists in watchlist
    existing_stocks = watchlist.get("stocks", [])
    if any(s["symbol"] == stock_data.symbol for s in existing_stocks):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock already exists in watchlist"
        )

    # Add stock to watchlist
    new_stock = Stock(symbol=stock_data.symbol, name=stock_data.name)

    await db.watchlists.update_one(
        {"_id": ObjectId(watchlist_id)},
        {
            "$push": {"stocks": new_stock.model_dump()},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )

    # Fetch updated watchlist
    updated_watchlist = await db.watchlists.find_one({"_id": ObjectId(watchlist_id)})

    return WatchlistResponse(
        id=str(updated_watchlist["_id"]),
        user_id=str(updated_watchlist["user_id"]),
        name=updated_watchlist["name"],
        description=updated_watchlist.get("description"),
        stocks=[
            StockResponse(
                symbol=s["symbol"],
                name=s.get("name"),
                added_at=s["added_at"]
            ) for s in updated_watchlist.get("stocks", [])
        ],
        created_at=updated_watchlist["created_at"],
        updated_at=updated_watchlist["updated_at"],
        is_default=updated_watchlist.get("is_default", False)
    )


@router.delete("/{watchlist_id}/stocks/{symbol}", response_model=WatchlistResponse)
async def remove_stock_from_watchlist(
    watchlist_id: str,
    symbol: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Remove a stock from watchlist"""

    # Check if watchlist exists and belongs to user
    watchlist = await db.watchlists.find_one({
        "_id": ObjectId(watchlist_id),
        "user_id": ObjectId(user_id)
    })

    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found"
        )

    # Remove stock from watchlist
    await db.watchlists.update_one(
        {"_id": ObjectId(watchlist_id)},
        {
            "$pull": {"stocks": {"symbol": symbol}},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )

    # Fetch updated watchlist
    updated_watchlist = await db.watchlists.find_one({"_id": ObjectId(watchlist_id)})

    return WatchlistResponse(
        id=str(updated_watchlist["_id"]),
        user_id=str(updated_watchlist["user_id"]),
        name=updated_watchlist["name"],
        description=updated_watchlist.get("description"),
        stocks=[
            StockResponse(
                symbol=s["symbol"],
                name=s.get("name"),
                added_at=s["added_at"]
            ) for s in updated_watchlist.get("stocks", [])
        ],
        created_at=updated_watchlist["created_at"],
        updated_at=updated_watchlist["updated_at"],
        is_default=updated_watchlist.get("is_default", False)
    )


@router.post("/from-index", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def create_watchlist_from_index(
    index_data: IndexWatchlistCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Create a watchlist from a market index"""

    try:
        # Get stocks from index
        stocks_data = await StockService.get_index_stocks(index_data.index_name)

        # Create watchlist name
        watchlist_name = index_data.watchlist_name or f"{index_data.index_name.upper()} Stocks"

        # Create watchlist
        watchlist = Watchlist(
            user_id=ObjectId(user_id),
            name=watchlist_name,
            description=f"Auto-generated from {index_data.index_name.upper()} index",
            stocks=[Stock(symbol=s["symbol"], name=s["name"]) for s in stocks_data]
        )

        # Insert into database
        result = await db.watchlists.insert_one(
            watchlist.model_dump(by_alias=True, exclude={"id"})
        )

        # Fetch created watchlist
        created_watchlist = await db.watchlists.find_one({"_id": result.inserted_id})

        return WatchlistResponse(
            id=str(created_watchlist["_id"]),
            user_id=str(created_watchlist["user_id"]),
            name=created_watchlist["name"],
            description=created_watchlist.get("description"),
            stocks=[
                StockResponse(
                    symbol=s["symbol"],
                    name=s.get("name"),
                    added_at=s["added_at"]
                ) for s in created_watchlist.get("stocks", [])
            ],
            created_at=created_watchlist["created_at"],
            updated_at=created_watchlist["updated_at"],
            is_default=created_watchlist.get("is_default", False)
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating watchlist from index: {str(e)}"
        )
