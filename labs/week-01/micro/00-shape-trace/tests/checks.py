from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _student():
    path = Path(__file__).parents[1] / "starter.py"
    spec = spec_from_file_location("shape_trace", path)
    module = module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_full_attention_shape_chain():
    assert _student().complete_shape_chain((3, 4), (4, 2), (4, 2), (4, 2)) == {
        "Q": (3, 2), "K": (3, 2), "V": (3, 2), "scores": (3, 3),
        "weights": (3, 3), "output": (3, 2),
    }
