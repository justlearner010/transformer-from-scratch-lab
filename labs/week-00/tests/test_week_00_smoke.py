from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np


def load_contracts_module():
    path = Path(__file__).resolve().parents[1] / "src" / "contracts.py"
    spec = spec_from_file_location("week_00_contracts", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_week_00_exports_six_lab_functions() -> None:
    contracts = load_contracts_module()

    assert callable(contracts.require_matrix)
    assert callable(contracts.matrix_shape)
    assert callable(contracts.require_multipliable)
    assert callable(contracts.dot_entry)
    assert callable(contracts.matmul_from_entries)
    assert callable(contracts.describe_product)


def test_week_00_starter_signals_first_unimplemented_gate() -> None:
    contracts = load_contracts_module()

    try:
        contracts.require_matrix(np.ones((2, 2)), name="left")
    except NotImplementedError:
        pass
