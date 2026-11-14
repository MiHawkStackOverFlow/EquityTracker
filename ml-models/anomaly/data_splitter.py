import numpy as np
from typing import Iterator, Tuple

class PurgedTimeSeriesSplit:
    """
    Expanding-window time-series cross-validator with an explicit embargo buffer
    to prevent rolling-window lookahead leakage.
    """

    def __init__(self, n_splits: int = 5, test_size: int = 20, embargo_days: int = 5):
        if n_splits < 1:
            raise ValueError("n_splits must be at least 1")
        if test_size < 1:
            raise ValueError("test_size must be at least 1")
        if embargo_days < 0:
            raise ValueError("embargo_days cannot be negative")

        self.n_splits = n_splits
        self.test_size = test_size
        self.embargo_days = embargo_days

    def split(self, X) -> Iterator[Tuple[np.ndarray, np.ndarray]]:
        n_samples = len(X)
        indices = np.arange(n_samples)

        # Total rows needed for all test folds + the embargo gap before the first test fold
        total_test_span = (self.n_splits * self.test_size) + self.embargo_days
        initial_train_size = n_samples - total_test_span

        if initial_train_size <= 0:
            raise ValueError(
                f"Not enough samples ({n_samples}) for {self.n_splits} splits "
                f"with test_size={self.test_size} and embargo_days={self.embargo_days}."
            )

        for i in range(self.n_splits):
            # 1. Where does the expanding training window end for fold i?
            train_end = initial_train_size + (i * self.test_size)

            # 2. Where does the test window start (after skipping embargo_days)?
            test_start = train_end + self.embargo_days # train_end and self.embargo_days

            # 3. Where does the test window end?
            test_end = test_start + self.test_size 
            train_indices = indices[0:train_end]
            test_indices = indices[test_start:test_end]

            yield train_indices, test_indices