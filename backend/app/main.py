from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import AsyncSessionLocal
from app import models, schemas
from sqlalchemy.future import select
from app.stock_fetcher import fetch_stock_data

app = FastAPI()

@app.get("/")
def root():
    return {"message": "EquityTracker backend running on EC2!"}

@app.get("/stock/{ticker}")
def get_stock(ticker: str):
    return fetch_stock_data(ticker)


# Dependency: get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.post("/watchlist")
async def add_to_watchlist(
    watch: schemas.WatchlistCreate,
    db: AsyncSession = Depends(get_db)
):
    new_entry = models.Watchlist(symbol=watch.symbol)
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)
    return new_entry