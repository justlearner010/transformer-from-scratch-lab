from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import numpy as np


def _student():
    spec = spec_from_file_location("score_probe", Path(__file__).parents[1] / "starter.py")
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_score_uses_key_transpose():
    query = np.array([[1.0, 2.0], [3.0, 4.0]])
    key = np.array([[5.0, 6.0], [7.0, 8.0], [9.0, 10.0]])
    np.testing.assert_allclose(_student().score_probe(query, key), [[17, 23, 29], [39, 53, 67]])
