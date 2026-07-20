"""运行 Week 1 的一个最小机制实验。"""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import numpy as np


def load_micro_labs():
    path = Path(__file__).parent / "src" / "micro_labs.py"
    spec = spec_from_file_location("week_01_micro_labs", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(name: str) -> object:
    micro = load_micro_labs()
    if name == "shape":
        return micro.shape_trace((3, 4), (4, 2), (4, 2), (4, 2))
    if name == "score":
        return micro.score_probe(
            np.array([[1.0, 2.0]]), np.array([[3.0, 4.0], [5.0, 6.0]])
        )
    if name == "softmax":
        return micro.stable_softmax_probe(np.array([[1000.0, 999.0, 998.0]]))
    if name == "value":
        return micro.value_read_probe(
            np.array([[0.75, 0.25]]), np.array([[2.0, 0.0], [0.0, 4.0]])
        )
    if name == "compose":
        return micro.compose_attention(
            np.ones((2, 2)), np.eye(2), np.eye(2), np.eye(2)
        )
    raise ValueError(f"unknown micro-lab: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="run one Week 1 micro-lab")
    parser.add_argument("name", choices=("shape", "score", "softmax", "value", "compose"))
    args = parser.parse_args()
    print(run(args.name))


if __name__ == "__main__":
    main()
