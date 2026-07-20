from pathlib import Path


def test_each_micro_lab_has_one_editable_starter_and_one_public_check() -> None:
    root = Path(__file__).resolve().parents[1] / "micro"
    for name in ("00-shape-trace", "01-score-probe", "02-stable-softmax", "03-value-read", "04-qkv-projection", "compose"):
        assert (root / name / "starter.py").is_file()
        assert (root / name / "tests" / "checks.py").is_file()
