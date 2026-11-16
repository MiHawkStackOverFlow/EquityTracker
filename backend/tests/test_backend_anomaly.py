import numpy as np
from app import schemas
from app.main import evaluate_ticker_anomalies

np.random.seed(42)
closes = (100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.01, 80)))).tolist()
highs = [c * 1.005 for c in closes]
lows = [c * 0.995 for c in closes]
vols = [1_000_000.0] * 80

# Spike the final day (index 79) so latest_day triggers an alert
closes[-1] = closes[-2] * 0.89
lows[-1] = closes[-1] * 0.98
vols[-1] = 5_500_000.0

req = schemas.AnomalyEvaluateRequest(high=highs, low=lows, close=closes, volume=vols)
print(evaluate_ticker_anomalies("AAPL", req))