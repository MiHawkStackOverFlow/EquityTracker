from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Literal
import random

import sys
import pandas as pd
from pathlib import Path
from app import models, schemas, db
from app.stock_fetcher import fetch_stock_data
from app.analytics.dependence import analyze_portfolio_dependence

# Import ML modules from ml-models/anomaly
ANOMALY_DIR = Path(__file__).resolve().parent.parent.parent / "ml-models" / "anomaly"
if str(ANOMALY_DIR) not in sys.path:
    sys.path.append(str(ANOMALY_DIR))

from z_score_detector import compute_rolling_z_scores
from isolation_forest_detector import train_and_evaluate_isolation_forest

# Initialize the app
app = FastAPI()

# Configure CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://35.182.180.174",
    # add prod/staging origins when deploy frontend
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

@app.post("/api/v1/analytics/dependence")
def get_portfolio_dependence(payload: schemas.DependenceRequest):
    try:
        return analyze_portfolio_dependence(
            price_series=payload.price_series,
            divergence_threshold=payload.divergence_threshold,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/api/v1/anomalies/evaluate/{symbol}")
def evaluate_ticker_anomalies(symbol: str, payload: schemas.AnomalyEvaluateRequest):
    n_bars = len(payload.close)
    
    if not (len(payload.high) == len(payload.low) == len(payload.volume) == n_bars):
        raise HTTPException(status_code=400, detail="high, low, close, and volume arrays must have equal length.")
    if n_bars < 50:
        raise HTTPException(status_code=400, detail="At least 50 daily observations are required for purged CV.")

    try:
        df = pd.DataFrame({ "high": payload.high, "low": payload.low, "close": payload.close, "volume": payload.volume })

        z_df = compute_rolling_z_scores(df, window=payload.window, z_threshold=payload.z_threshold)

        iforest_res = train_and_evaluate_isolation_forest(df, window=payload.window, contamination=payload.contamination)
        scored_df = iforest_res["scored_df"]

        latest_z = z_df.iloc[-1]
        latest_iforest = scored_df.iloc[-1]

        return {
            "symbol": symbol.upper(),
            "observations_evaluated": iforest_res["n_observations"],
            "cv_mean_anomaly_rate": iforest_res["cv_mean_anomaly_rate"],
            "z_score_anomalies_total": int(z_df["is_z_anomaly"].sum()),
            "iforest_anomalies_total": iforest_res["total_anomalies_flagged"],
            "latest_day": {
                "max_abs_z": round(float(latest_z["max_abs_z"]), 4),
                "is_z_anomaly": bool(latest_z["is_z_anomaly"]),
                "is_tail_jump": bool(latest_z["is_tail_jump"]),
                "is_iforest_anomaly": bool(latest_iforest["is_iforest_anomaly"]),
                "anomaly_score": round(float(latest_iforest["anomaly_score"]), 4),
                "trigger_langgraph_triage": bool(
                    latest_z["is_z_anomaly"] or latest_iforest["is_iforest_anomaly"]
                )
            }
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))    