from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import numpy as np


def _student():
    spec = spec_from_file_location("compose", Path(__file__).parents[1] / "starter.py")
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_composed_attention_returns_output_and_weights():
    output, weights = _student().scaled_dot_product_attention(np.ones((2, 2)), np.eye(2), np.eye(2), np.eye(2))
    assert output.shape == (2, 2)
    np.testing.assert_allclose(weights.sum(axis=-1), [1.0, 1.0])
