from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Form
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from typing import Optional
import pandas as pd
import io
import logging

from app.core.database import get_database
from app.core.security import get_current_user_id
from app.models.watchlist import Watchlist, Stock
from app.schemas.watchlist import WatchlistResponse, StockResponse

router = APIRouter(prefix="/upload", tags=["Upload"])
logger = logging.getLogger(__name__)


@router.post("/excel", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def upload_excel_watchlist(
    file: UploadFile = File(..., description="Excel file with stock symbols"),
    watchlist_name: Optional[str] = Form(None, description="Name for the watchlist"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Upload an Excel file to create a watchlist

    Excel file should have at least one column with stock symbols.
    Acceptable column names: 'symbol', 'symbols', 'stock', 'stocks', 'ticker', 'tickers'
    Optional column: 'name' or 'company' for stock names

    Example Excel format:
    | Symbol      | Name               |
    |-------------|--------------------|
    | RELIANCE.NS | Reliance Industries|
    | TCS.NS      | Tata Consultancy   |
    """

    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be Excel (.xlsx, .xls) or CSV (.csv)"
        )

    try:
        # Read file content
        content = await file.read()

        # Parse based on file type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))

        # Check if dataframe is empty
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Excel file is empty"
            )

        # Find symbol column (case-insensitive)
        symbol_column = None
        name_column = None

        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()

        # Find symbol column
        for col in ['symbol', 'symbols', 'stock', 'stocks', 'ticker', 'tickers', 'code']:
            if col in df.columns:
                symbol_column = col
                break

        if not symbol_column:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Excel file must have a column named 'symbol', 'stock', or 'ticker'"
            )

        # Find name column (optional)
        for col in ['name', 'company', 'company_name', 'stock_name']:
            if col in df.columns:
                name_column = col
                break

        # Extract stocks
        stocks = []
        for _, row in df.iterrows():
            symbol = str(row[symbol_column]).strip()

            # Skip empty symbols
            if not symbol or symbol.lower() in ['nan', 'none', '']:
                continue

            # Get name if available
            stock_name = None
            if name_column and pd.notna(row[name_column]):
                stock_name = str(row[name_column]).strip()

            # Ensure symbol has exchange suffix
            if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                symbol = f"{symbol}.NS"  # Default to NSE

            stocks.append(Stock(symbol=symbol, name=stock_name))

        if not stocks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid stock symbols found in Excel file"
            )

        # Create watchlist name
        if not watchlist_name:
            watchlist_name = f"Imported from {file.filename}"

        # Create watchlist
        watchlist = Watchlist(
            user_id=ObjectId(user_id),
            name=watchlist_name,
            description=f"Imported from Excel file: {file.filename}",
            stocks=stocks
        )

        # Insert into database
        result = await db.watchlists.insert_one(
            watchlist.model_dump(by_alias=True, exclude={"id"})
        )

        # Fetch created watchlist
        created_watchlist = await db.watchlists.find_one({"_id": result.inserted_id})

        logger.info(f"Created watchlist from Excel: {watchlist_name} with {len(stocks)} stocks")

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

    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Excel file is empty or corrupted"
        )
    except Exception as e:
        logger.error(f"Error processing Excel upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing Excel file: {str(e)}"
        )


@router.post("/excel/append/{watchlist_id}", response_model=WatchlistResponse)
async def append_excel_to_watchlist(
    watchlist_id: str,
    file: UploadFile = File(..., description="Excel file with stock symbols"),
    user_id: str = Depends(get_current_user_id),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Append stocks from Excel file to an existing watchlist
    """

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

    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be Excel (.xlsx, .xls) or CSV (.csv)"
        )

    try:
        # Read file content
        content = await file.read()

        # Parse based on file type
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))

        # Find symbol column
        df.columns = df.columns.str.strip().str.lower()

        symbol_column = None
        name_column = None

        for col in ['symbol', 'symbols', 'stock', 'stocks', 'ticker', 'tickers', 'code']:
            if col in df.columns:
                symbol_column = col
                break

        if not symbol_column:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Excel file must have a column named 'symbol', 'stock', or 'ticker'"
            )

        for col in ['name', 'company', 'company_name', 'stock_name']:
            if col in df.columns:
                name_column = col
                break

        # Get existing stock symbols to avoid duplicates
        existing_symbols = {s["symbol"] for s in watchlist.get("stocks", [])}

        # Extract new stocks
        new_stocks = []
        for _, row in df.iterrows():
            symbol = str(row[symbol_column]).strip()

            if not symbol or symbol.lower() in ['nan', 'none', '']:
                continue

            stock_name = None
            if name_column and pd.notna(row[name_column]):
                stock_name = str(row[name_column]).strip()

            if not symbol.endswith('.NS') and not symbol.endswith('.BO'):
                symbol = f"{symbol}.NS"

            # Skip if already exists
            if symbol in existing_symbols:
                continue

            new_stocks.append(Stock(symbol=symbol, name=stock_name))

        if not new_stocks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No new valid stock symbols found in Excel file (all may already exist)"
            )

        # Append stocks to watchlist
        await db.watchlists.update_one(
            {"_id": ObjectId(watchlist_id)},
            {
                "$push": {"stocks": {"$each": [s.model_dump() for s in new_stocks]}},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        # Fetch updated watchlist
        updated_watchlist = await db.watchlists.find_one({"_id": ObjectId(watchlist_id)})

        logger.info(f"Appended {len(new_stocks)} stocks to watchlist {watchlist_id}")

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

    except Exception as e:
        logger.error(f"Error appending Excel to watchlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing Excel file: {str(e)}"
        )
