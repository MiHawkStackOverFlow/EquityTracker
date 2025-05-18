import os
import requests
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

def fetch_stock_data(ticker: str) -> dict:
    try:
        base_url = "https://finnhub.io/api/v1/quote"
        params = { "symbol": ticker.upper(), "token": FINNHUB_API_KEY }

        response = requests.get(base_url, params=params)
        data = response.json()

        if "c" not in data or data["c"] == 0:
            return {"error": "No data found. Invalid ticker?"}

        return {
            "ticker": ticker.upper(),
            "price": data["c"],
            "high": data["h"],
            "low": data["l"],
            "open": data["o"],
            "prev_close": data["pc"]
        }

    except Exception as e:
        return {"error": str(e)}
