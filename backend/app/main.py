from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import models, schemas, db
from sqlalchemy.future import select
from app.stock_fetcher import fetch_stock_data
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/")
def root():
    return {"message": "EquityTracker backend running on EC2!"}

@app.get("/stock/{ticker}")
def get_stock(ticker: str):
    return fetch_stock_data(ticker)

@app.post("/watchlist")
async def add_to_watchlist(watch: schemas.WatchlistCreate, db: AsyncSession = Depends(db.get_db)):
    new_entry = models.Watchlist(symbol=watch.symbol)
    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)
    return new_entry

@app.get("/watchlist", response_model=list[schemas.WatchlistOut])
async def get_watchlist(db_session: AsyncSession = Depends(db.get_db)):
    result = await db_session.execute(select(models.Watchlist))
    return result.scalars().all()