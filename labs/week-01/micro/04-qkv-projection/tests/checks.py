from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import numpy as np


def _student():
    spec = spec_from_file_location("qkv_projection", Path(__file__).parents[1] / "starter.py")
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_projection_preserves_sequence_axis():
    tokens = np.array([[1.0, 2.0], [3.0, 4.0]])
    q, k, v = _student().project_qkv(tokens, np.eye(2), np.eye(2), np.array([[1.0], [2.0]]))
    assert q.shape == (2, 2) and k.shape == (2, 2) and v.shape == (2, 1)
