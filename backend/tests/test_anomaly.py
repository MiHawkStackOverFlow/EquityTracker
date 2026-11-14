import numpy as np
import pandas as pd
from z_score_detector import compute_rolling_z_scores
from isolation_forest_detector import train_and_evaluate_isolation_forest

# 1. Create 100 days of synthetic normal OHLCV market data
np.random.seed(42)
n_days = 100
closes = 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.01, n_days)))
highs = closes * (1 + np.abs(np.random.normal(0.005, 0.003, n_days)))
lows = closes * (1 - np.abs(np.random.normal(0.005, 0.003, n_days)))
volumes = np.random.normal(1_000_000, 150_000, n_days)

df = pd.DataFrame({"high": highs, "low": lows, "close": closes, "volume": volumes})

# 2. Inject 2 deliberate anomalies
# Day 55: Massive single-day flash crash (-12% drop, 5x volume)
df.loc[55, "close"] = df.loc[54, "close"] * 0.88
df.loc[55, "low"] = df.loc[55, "close"] * 0.98
df.loc[55, "volume"] = 5_000_000

# Day 85: Subtle 3D whipsaw (Close barely moves, but 4.5x volume + 9% intraday swing)
df.loc[85, "high"] = df.loc[85, "close"] * 1.045
df.loc[85, "low"] = df.loc[85, "close"] * 0.955
df.loc[85, "volume"] = 4_500_000

# 3. Run File 1: Rolling Z-Score Detector
z_df = compute_rolling_z_scores(df)
print("=== 1. Z-SCORE DETECTOR RESULTS ===")
print("Total Z-Score Anomalies (|z| >= 2.5):", int(z_df["is_z_anomaly"].sum()))
print("Day 55 Flagged by Z-Score?:", bool(z_df.loc[55, "is_z_anomaly"]), f"(max_z = {z_df.loc[55, 'max_abs_z']:.2f})")
print("Day 85 Flagged by Z-Score?:", bool(z_df.loc[85, "is_z_anomaly"]), f"(max_z = {z_df.loc[85, 'max_abs_z']:.2f})")

# 4. Run Files 2 & 3: PurgedTimeSeriesSplit + Isolation Forest Pipeline
res = train_and_evaluate_isolation_forest(df, contamination=0.05)
scored = res["scored_df"]
print("\n=== 2. ISOLATION FOREST + PURGED CV RESULTS ===")
print("Observations Evaluated:", res["n_observations"])
print("Walk-Forward CV Mean Anomaly Rate:", res["cv_mean_anomaly_rate"])
print("Total Isolation Forest Anomalies:", res["total_anomalies_flagged"])
print("Day 55 Flagged by IsolationForest?:", bool(scored.loc[55, "is_iforest_anomaly"]), f"(score = {scored.loc[55, 'anomaly_score']:.4f})")
print("Day 85 Flagged by IsolationForest?:", bool(scored.loc[85, "is_iforest_anomaly"]), f"(score = {scored.loc[85, 'anomaly_score']:.4f})")
print("Saved Artifact Path:", res["artifact_path"])