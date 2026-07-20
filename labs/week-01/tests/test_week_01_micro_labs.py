from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import subprocess
import sys

import numpy as np


def load_micro_module():
    path = Path(__file__).resolve().parents[1] / "src" / "micro_labs.py"
    assert path.is_file(), "Week 1 micro-lab module is missing"
    spec = spec_from_file_location("week_01_micro_labs", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_shape_trace_reports_the_full_attention_shape_chain() -> None:
    micro = load_micro_module()
    report = micro.shape_trace((3, 4), (4, 2), (4, 2), (4, 2))

    assert report == {
        "Q": (3, 2),
        "K": (3, 2),
        "V": (3, 2),
        "scores": (3, 3),
        "weights": (3, 3),
        "output": (3, 2),
    }


def test_score_probe_requires_the_transposed_key_dimension() -> None:
    micro = load_micro_module()
    query = np.array([[1.0, 2.0], [3.0, 4.0]])
    key = np.array([[5.0, 6.0], [7.0, 8.0], [9.0, 10.0]])

    np.testing.assert_allclose(
        micro.score_probe(query, key),
        np.array([[17.0, 23.0, 29.0], [39.0, 53.0, 67.0]]),
    )


def test_stable_softmax_stays_finite_and_normalizes_rows() -> None:
    micro = load_micro_module()
    weights = micro.stable_softmax_probe(np.array([[1000.0, 999.0, 998.0]]))

    assert np.isfinite(weights).all()
    np.testing.assert_allclose(weights.sum(axis=-1), np.array([1.0]))


def test_value_read_changes_output_without_changing_weights() -> None:
    micro = load_micro_module()
    weights = np.array([[0.75, 0.25]])
    values = np.array([[2.0, 0.0], [0.0, 4.0]])

    np.testing.assert_allclose(
        micro.value_read_probe(weights, values), np.array([[1.5, 1.0]])
    )


def test_compose_attention_reuses_all_public_micro_components(monkeypatch) -> None:
    micro = load_micro_module()
    calls: list[str] = []

    def project(tokens, wq, wk, wv):
        calls.append("project")
        return tokens @ wq, tokens @ wk, tokens @ wv

    def score(query, key):
        calls.append("score")
        return query @ key.T

    def softmax(scores):
        calls.append("softmax")
        return np.ones_like(scores) / scores.shape[-1]

    def read(weights, values):
        calls.append("read")
        return weights @ values

    monkeypatch.setattr(micro, "project_qkv_probe", project)
    monkeypatch.setattr(micro, "score_probe", score)
    monkeypatch.setattr(micro, "stable_softmax_probe", softmax)
    monkeypatch.setattr(micro, "value_read_probe", read)

    output, weights = micro.compose_attention(
        np.ones((2, 2)), np.eye(2), np.eye(2), np.eye(2)
    )

    assert calls == ["project", "score", "softmax", "read"]
    assert output.shape == (2, 2)
    assert weights.shape == (2, 2)


def test_micro_runner_runs_one_named_experiment() -> None:
    runner = Path(__file__).resolve().parents[1] / "run_micro.py"
    result = subprocess.run(
        [sys.executable, str(runner), "shape"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "scores" in result.stdout
