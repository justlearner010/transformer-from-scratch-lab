from pathlib import Path

import pytest

from learning_runtime.manifest import load_manifest
from learning_runtime.verification.rubric import RubricError, load_rubric


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = load_manifest(ROOT / "course-manifests/week-01.yaml", ROOT)


def test_gate_zero_has_one_versioned_matching_criterion() -> None:
    gate = MANIFEST.gate("week-01-gate-0")
    rubric = load_rubric(ROOT, gate)

    assert gate.rubric_ref == "course-manifests/rubrics/week-01.yaml"
    assert gate.rubric_version == 1
    assert rubric.rubric_id == "week-01-gate-0-rubric"
    assert rubric.version == 1
    assert tuple(item.criterion_id for item in rubric.criteria) == (
        "shape-bridge-complete",
    )
    assert rubric.content_hash.startswith("sha256:")


def test_gate_without_rubric_is_unavailable() -> None:
    with pytest.raises(RubricError, match="no rubric"):
        load_rubric(ROOT, MANIFEST.gate("week-01-gate-1"))
