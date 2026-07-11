from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def load_contracts_module():
    path = Path(__file__).resolve().parents[1] / "src" / "contracts.py"
    spec = spec_from_file_location("week_00_contracts", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_week_00_exports_required_functions() -> None:
    contracts = load_contracts_module()

    assert callable(contracts.validate_matrix_shape)
    assert callable(contracts.matrix_product_shape)


def test_week_00_starter_signals_unimplemented_work() -> None:
    contracts = load_contracts_module()

    try:
        contracts.validate_matrix_shape((3, 2), name="left")
    except NotImplementedError:
        pass
