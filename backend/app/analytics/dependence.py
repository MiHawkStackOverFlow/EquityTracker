import pandas as pd

def compute_kendall(x: list[float], y: list[float]) -> float:
    """
    Implementation of Kendall's Rank Correlation (tau_k).
    Time Complexity: O(n^2) | Space Complexity: O(1)
    """
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Arrays must have equal length of at least 2.")

    n = len(x)
    concordant = 0
    discordant = 0

    for i in range(n):
        for j in range(i+1, n):
            dx = x[j] - x[i]
            dy = y[j] - y[i]
            
            product = dx * dy
            if product > 0:
                concordant += 1
            elif product < 0:
                discordant += 1

    total_pairs = n * (n - 1) // 2
    if total_pairs == 0:
        return 0.0

    return ((concordant - discordant) / total_pairs)


def prepare_returns_dataframe(price_series: dict[str, list[float]]) -> pd.DataFrame:
    """
    Converts a dictionary of raw closing prices into a clean DataFrame of daily returns.
    Example input: {"AAPL": [100.0, 101.0, 104.03], "NVDA": [200.0, 204.0, 224.4]}
    """
    df_prices = pd.DataFrame(price_series)
    
    if len(df_prices) < 3:
        raise ValueError("Need at least 3 price observations (2 return days) to compute correlation.")

    df_returns = df_prices.pct_change().dropna()
    
    return df_returns

def compute_dependency_matrices(returns_df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Computes Pearson (linear), Kendall (rank), and absolute divergence (|rho - tau_k|)
    matrices across all tickers in the returns DataFrame.
    """
    # Compute the N x N Pearson and Kendall correlation DataFrames
    pearson_df = returns_df.corr(method="pearson")
    kendall_df = returns_df.corr(method="kendall")

    # Compute the element-wise absolute difference |pearson - kendall|
    divergence_df = (pearson_df - kendall_df).abs()

    return {
        "pearson": pearson_df,
        "kendall": kendall_df,
        "divergence": divergence_df
    }

def extract_divergent_pairs(pearson_df: pd.DataFrame, kendall_df: pd.DataFrame, divergence_df: pd.DataFrame, divergence_threshold: float = 0.25) -> list[dict]:
    """
    Scans the upper triangle (i < j) of the correlation matrices and returns
    stock pairs where |Pearson - Kendall| >= divergence_threshold.
    """
    tickers = list(pearson_df.columns)
    n_tickers = len(tickers)
    divergent_pairs = []

    for i in range(n_tickers):
        for j in range(i + 1, n_tickers):
            rho = float(pearson_df.iloc[i, j])
            tau_k = float(kendall_df.iloc[i, j])
            diff = float(divergence_df.iloc[i, j])

            if diff >= divergence_threshold:
                regime_type = (
                    "OUTLIER_DRIVEN_CONTAGION"
                    if abs(rho) > abs(tau_k)
                    else "NON_LINEAR_MONOTONIC"
                )
                divergent_pairs.append({
                    "pair": f"{tickers[i]}-{tickers[j]}",
                    "pearson_rho": round(rho, 4),
                    "kendall_tau": round(tau_k, 4),
                    "divergence": round(diff, 4),
                    "regime_flag": regime_type
                })

    divergent_pairs.sort(key=lambda item: item["divergence"], reverse=True)
    return divergent_pairs

def analyze_portfolio_dependence(price_series: dict[str, list[float]], divergence_threshold: float = 0.25) -> dict:
    """
    End-to-end orchestrator for portfolio correlation and regime divergence analysis.
    """
    returns_df = prepare_returns_dataframe(price_series)
    matrices = compute_dependency_matrices(returns_df)

    divergent_pairs = extract_divergent_pairs(
        pearson_df=matrices["pearson"],
        kendall_df=matrices["kendall"],
        divergence_df=matrices["divergence"],
        divergence_threshold=divergence_threshold
    )

    return {
        "tickers": list(returns_df.columns),
        "observations_used": len(returns_df),
        "pearson_matrix": matrices["pearson"].round(4).to_dict(),
        "kendall_matrix": matrices["kendall"].round(4).to_dict(),
        "divergence_matrix": matrices["divergence"].round(4).to_dict(),
        "divergent_pairs": divergent_pairs
    }
