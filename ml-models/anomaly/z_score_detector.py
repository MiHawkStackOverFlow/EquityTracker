import numpy as np
import pandas as pd

def engineer_market_features(df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    """
    Stationary daily microstructure features from OHLCV data:
      1. log_return     = ln(close_t / close_{t-1})
      2. volume_delta   = volume_t / rolling_median(volume, window)
      3. intraday_range = (high_t - low_t) / close_t
    """
    required_cols = {"high", "low", "close", "volume"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"DataFrame must contain columns: {required_cols}")

    out = df.copy()

    # 1. Daily log return: ln(close / previous close)
    out["log_return"] = np.log(out["close"] / out["close"].shift(1))

    # 2. Volume delta relative to rolling median (min_periods=5 avoids full NaN start)
    rolling_vol_median = out["volume"].rolling(window=window, min_periods=5).median()
    # Divide out["volume"] by rolling_vol_median
    out["volume_delta"] = out["volume"] / rolling_vol_median

    # 3. Intraday high-low range normalized by closing price
    # Compute (high - low) / close
    out["intraday_range"] = (out["high"] - out["low"]) / out["close"]

    return out.dropna(subset=["log_return", "volume_delta", "intraday_range"])


def compute_rolling_z_scores(df: pd.DataFrame, window: int = 30, z_threshold: float = 2.5, jump_threshold: float = 3.0) -> pd.DataFrame:
    """
    Computes causal rolling z-scores z = (x - rolling_mean) / rolling_std
    across the 3 microstructure features and flags >= 2.5 sigma breaches.
    """
    featured_df = engineer_market_features(df, window=window)
    feature_cols = ["log_return", "volume_delta", "intraday_range"]

    for col in feature_cols:
        rolling_mean = featured_df[col].rolling(window=window, min_periods=5).mean()
        rolling_std = featured_df[col].rolling(window=window, min_periods=5).std()

        # Replace 0 std with NaN to prevent division-by-zero on flat days
        safe_std = rolling_std.replace(0, np.nan)

        # Apply the z-score formula
        featured_df[f"{col}_z"] = (featured_df[col] - rolling_mean) / safe_std
        featured_df[f"{col}_z"] = featured_df[f"{col}_z"].fillna(0.0)

    z_cols = ["log_return_z", "volume_delta_z", "intraday_range_z"]

    # Maximum absolute z-score across all 3 features on each day
    featured_df["max_abs_z"] = featured_df[z_cols].abs().max(axis=1)

    # Flag True where max_abs_z >= z_threshold (2.5) and jump where >= jump_threshold (3.0)
    featured_df["is_z_anomaly"] = featured_df["max_abs_z"] >= z_threshold
    featured_df["is_tail_jump"] = featured_df["max_abs_z"] >=jump_threshold

    return featured_df