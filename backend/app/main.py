from fastapi import FastAPI
from app.stock_fetcher import fetch_stock_data

app = FastAPI()

@app.get("/")
def root():
    return {"message": "EquityTracker backend running on EC2!"}

@app.get("/stock/{ticker}")
def get_stock(ticker: str):
    return fetch_stock_data(ticker)
