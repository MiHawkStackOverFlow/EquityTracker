import yfinance as yf

def fetch_stock_data(ticker: str) -> dict:
    try:
        stock = yf.Ticker(ticker)
        print("DEBUG1:", stock)
        data = stock.info
        print("DEBUG2:", data)
        return {
            "ticker": ticker.upper(),
            "name": data.get("shortName"),
            "price": data.get("regularMarketPrice"),
            "currency": data.get("currency"),
            "change_percent": data.get("regularMarketChangePercent"),
            "exchange": data.get("exchange"),
        }
    except Exception as e:
        return {"error": str(e)}
