"""Micro-lab 1: implement the score matrix, not an elementwise product."""
import numpy as np


def score_probe(query: np.ndarray, key: np.ndarray) -> np.ndarray:
    """Return Q @ K.T; reject non-2D inputs and mismatched feature dimensions."""
    raise NotImplementedError("完成 score probe：解释为什么必须是 K.T")
