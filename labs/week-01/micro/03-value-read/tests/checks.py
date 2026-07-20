from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import numpy as np


def _student():
    spec = spec_from_file_location("value_read", Path(__file__).parents[1] / "starter.py")
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_weights_read_value_rows():
    actual = _student().read_values(np.array([[0.75, 0.25]]), np.array([[2.0, 0.0], [0.0, 4.0]]))
    np.testing.assert_allclose(actual, [[1.5, 1.0]])
