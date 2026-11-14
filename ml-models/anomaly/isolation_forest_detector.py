from pathlib import Path
from typing import Dict, Any
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import RobustScaler

from data_splitter import PurgedTimeSeriesSplit
from z_score_detector import engineer_market_features

FEATURE_COLS = ["log_return", "volume_delta", "intraday_range"]
DEFAULT_ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "artifacts" / "isolation_forest_v1.joblib"

def build_isolation_forest_pipeline(contamination: float = 0.05, n_estimators: int = 100, random_state: int = 42) -> Pipeline:
    """
    Constructs a leakage-safe Scikit-Learn Pipeline chaining RobustScaler and IsolationForest.
    """
    # Pass RobustScaler() and IsolationForest() into make_pipeline
    pipeline = make_pipeline(
        RobustScaler(),
        IsolationForest(contamination=contamination, n_estimators=n_estimators, random_state=random_state)
    )
    return pipeline


def train_and_evaluate_isolation_forest(
    df: pd.DataFrame,
    window: int = 30,
    contamination: float = 0.05,
    n_splits: int = 3,
    test_size: int = 10,
    embargo_days: int = 5,
    save_artifact: bool = True,
    artifact_path: Path = DEFAULT_ARTIFACT_PATH
) -> Dict[str, Any]:
    """
    1. Engineers daily market features (log_return, volume_delta, intraday_range).
    2. Evaluates the Pipeline across walk-forward PurgedTimeSeriesSplit folds.
    3. Refits on the full feature matrix and exports the artifact via joblib.
    """
    featured_df = engineer_market_features(df, window=window)
    X = featured_df[FEATURE_COLS].to_numpy()

    splitter = PurgedTimeSeriesSplit(n_splits=n_splits, test_size=test_size, embargo_days=embargo_days)

    fold_anomaly_rates = []
    for train_idx, val_idx in splitter.split(X):
        fold_pipe = build_isolation_forest_pipeline(contamination=contamination)
        # Fit fold_pipe ONLY on the training slice X[train_idx]
        fold_pipe.fit(X[train_idx])

        # Predict on the validation slice X[val_idx] (-1 = anomaly, +1 = normal)
        val_preds = fold_pipe.predict(X[val_idx])
        fold_anomaly_rates.append(float(np.mean(val_preds == -1)))

    # Final refit on all available historical rows
    final_pipeline = build_isolation_forest_pipeline(contamination=contamination)
    final_pipeline.fit(X)

    # Generate predictions and anomaly severity scores
    raw_preds = final_pipeline.predict(X)
    featured_df["is_iforest_anomaly"] = raw_preds == -1
    featured_df["anomaly_score"] = -final_pipeline.score_samples(X)

    if save_artifact:
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        # Save `final_pipeline` to `artifact_path` using joblib.dump
        joblib.dump(final_pipeline, artifact_path)

    return {
        "n_observations": len(featured_df),
        "cv_mean_anomaly_rate": round(float(np.mean(fold_anomaly_rates)), 4),
        "total_anomalies_flagged": int(featured_df["is_iforest_anomaly"].sum()),
        "artifact_path": str(artifact_path) if save_artifact else None,
        "scored_df": featured_df
    }