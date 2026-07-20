from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import numpy as np


def _student():
    spec = spec_from_file_location("stable_softmax", Path(__file__).parents[1] / "starter.py")
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_extreme_scores_stay_finite_and_normalize():
    result = _student().stable_softmax(np.array([[1000.0, 999.0, 998.0]]))
    assert np.isfinite(result).all()
    np.testing.assert_allclose(result.sum(axis=-1), [1.0])
