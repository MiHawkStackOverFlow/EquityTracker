from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Literal
import random

from app import models, schemas, db
from app.stock_fetcher import fetch_stock_data

# Initialize the app
app = FastAPI()

# Configure CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://35.182.180.174",
    # add prod/staging origins when you deploy your frontend
    # "https://equitytracker.yourdomain.com",
    # "https://your-vercel-app.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes

@app.get("/")
def root():
    return {"message": "EquityTracker backend running on EC2!"}

@app.get("/stock/{ticker}")
async def get_stock(ticker: str):
    return await fetch_stock_data(ticker)

@app.post("/watchlist", response_model=schemas.WatchlistOut)
async def upsert_watchlist(item: schemas.WatchlistCreate, db_session: AsyncSession = Depends(db.get_db)):
    existing = (await db_session.execute(
        select(models.Watchlist).where(models.Watchlist.symbol == item.symbol)
    )).scalar_one_or_none()

    if existing:
        for f in ("name","market_cap","pe_ratio","price","currency","exchange"):
            setattr(existing, f, getattr(item, f))
        await db_session.commit()
        await db_session.refresh(existing)
        return existing

    row = models.Watchlist(**item.model_dump())
    db_session.add(row)
    await db_session.commit()
    await db_session.refresh(row)
    return row

@app.get("/watchlist", response_model=list[schemas.WatchlistOut])
async def get_watchlist(db_session: AsyncSession = Depends(db.get_db)):
    result = await db_session.execute(select(models.Watchlist))
    return result.scalars().all()

@app.get("/sorted-watchlist/{sort_by}", response_model=list[schemas.WatchlistOut])
async def get_watchlist_sorted(
    sort_by: Literal["symbol", "name", "market_cap", "pe_ratio", "price", "created_at"],
    order: Literal["asc", "desc"] = "asc",
    db_session: AsyncSession = Depends(db.get_db)):
    # Build a safe column attribute from the model
    col = getattr(models.Watchlist, sort_by, None)
    if col is None:
        raise HTTPException(status_code=400, detail="Invalid sort_by field")

    stmt = select(models.Watchlist).order_by(col.desc() if order == "desc" else col.asc())
    result = await db_session.execute(stmt)
    return result.scalars().all()


@app.get("/predict/{ticker}")
async def predict_stock(ticker: str):
    """
    Dummy ML prediction endpoint (Ticket #18).
    To be replaced with a real Scikit-learn model (Phase 1).
    """
    # Simulate a binary classification model (Up/Down)
    prediction = random.choice(["Up", "Down"])
    
    # Simulate a probability/confidence score from the model
    confidence = round(random.uniform(0.51, 0.99), 2)
    
    return {
        "ticker": ticker.upper(),
        "prediction": prediction,
        "confidence": confidence,
        "model_version": "dummy-v1"
    }