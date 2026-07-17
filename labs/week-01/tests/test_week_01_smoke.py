from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np


def load_attention_module():
    path = Path(__file__).resolve().parents[1] / "src" / "attention.py"
    spec = spec_from_file_location("week_01_attention", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_lab_exports_required_functions() -> None:
    attention = load_attention_module()

    assert callable(attention.softmax)
    assert callable(attention.project_qkv)
    assert callable(attention.scaled_dot_product_attention)


def test_lab_starter_accepts_the_documented_input_types() -> None:
    attention = load_attention_module()
    scores = np.array([[1.0, 2.0]])
    try:
        attention.softmax(scores)
    except NotImplementedError:
        pass
