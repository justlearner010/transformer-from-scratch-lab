"""Composition gate: call the completed micro-lab components; do not rewrite them."""
import importlib.util
from pathlib import Path
import numpy as np


def _component(directory: str, function: str):
    path = Path(__file__).parents[1] / directory / "starter.py"
    spec = importlib.util.spec_from_file_location(directory, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return getattr(module, function)


def scaled_dot_product_attention(tokens: np.ndarray, w_query: np.ndarray, w_key: np.ndarray, w_value: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compose projection → score → stable softmax → value read in that order."""
    raise NotImplementedError("只组装已完成组件，不要重新实现 attention 的局部机制")
