from typing import Any, Dict, List
import numpy as np
from scipy import stats

def mean_and_uncertainty(prices: List[float] | np.ndarray) -> Dict[str, Any]:
    """
    Converts prices to daily returns and computes central tendency and dispersion.
    """
    price_array = np.asarray(prices, dtype=float)
    
    if len(price_array) < 2:
        raise ValueError("At least 2 price observations are required to calculate returns.")

    """
        `Daily_Return_Percent = (Price_Today - Price_Yesterday) / Price_Yesterday`
    """
    returns = np.diff(price_array) / price_array[:-1]

    mu = float(np.mean(returns))  # E[X]
    sigma = float(np.std(returns, ddof=1)) if len(returns) > 1 else 0.0  # Sample Std Dev
    variance = float(sigma ** 2)  # Var(X)

    return {
        "mean_return": mu,
        "variance": variance,
        "std_dev": sigma,
        "returns": returns
    }


def prob_odds_logodds(returns: np.ndarray) -> Dict[str, Any]:
    """
    Calculates empirical probability, odds, and log-odds for positive return days.
    """
    p_up = float(np.mean(returns > 0))

    if 0.0 < p_up < 1.0:
        odds = p_up / (1.0 - p_up)
        log_odds = float(np.log(odds))
    else:
        # Edge cases where asset strictly rises or strictly falls
        odds = float("inf") if p_up == 1.0 else 0.0
        log_odds = float("inf") if p_up == 1.0 else float("-inf")

    return {
        "p_up": p_up,
        "odds": odds,
        "log_odds": log_odds
    }


def shannon_entropy_mle(returns: np.ndarray, bins: int = 20) -> Dict[str, Any]:
    """
    Computes Shannon Entropy across return bins and fits a Gaussian curve via MLE.
    """
    hist_counts, _ = np.histogram(returns, bins=bins, density=False)
    probs = hist_counts / np.sum(hist_counts)
    probs = probs[probs > 0]  # Remove empty bins to avoid log(0)

    entropy_val = float(-np.sum(probs * np.log(probs)))

    # Fit Gaussian distribution using Maximum Likelihood Estimation
    mle_mu, mle_std = stats.norm.fit(returns)

    return {
        "entropy_val": entropy_val,
        "mle_mu": float(mle_mu),
        "mle_std": float(mle_std)
    }


def compute_distribution_metrics(prices: List[float] | np.ndarray) -> Dict[str, Any]:
    """
    Takes a chronological sequence of daily closing prices and produces
    the parametric distribution summaries, entropy, logit transforms, and Poisson jump metrics.
    """
    # 1. Base Summaries & Returns Array
    summary = mean_and_uncertainty(prices)
    returns = summary["returns"]
    mu = summary["mean_return"]
    sigma = summary["std_dev"]
    variance = summary["variance"]

    # 2. Probability & Log-Odds
    odds_data = prob_odds_logodds(returns)
    p_up = odds_data["p_up"]
    odds = odds_data["odds"]
    log_odds = odds_data["log_odds"]

    # 3. Information Entropy & MLE
    entropy_data = shannon_entropy_mle(returns)
    entropy_val = entropy_data["entropy_val"]
    mle_mu = entropy_data["mle_mu"]
    mle_std = entropy_data["mle_std"]

    # 4. Poisson Jump Process: Shock arrival intensity outside 2 standard deviations
    if sigma > 0:
        extreme_days = np.abs(returns - mu) > (2.0 * sigma)
        lambda_jump_rate = float(np.mean(extreme_days))
    else:
        lambda_jump_rate = 0.0

    return {
        "mean_return": mu,
        "variance": variance,
        "std_dev": sigma,
        "probability_up": p_up,
        "odds_up": odds,
        "log_odds_up": log_odds,
        "shannon_entropy": entropy_val,
        "mle_normal_fit": {
            "mu": mle_mu,
            "sigma": mle_std,
        },
        "poisson_jump_rate": lambda_jump_rate
    }